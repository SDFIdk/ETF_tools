import rasterio as rio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import Resampling
from rasterio.features import geometry_window
from shapely.geometry import Polygon
import json
import sys
import numpy as np
import os
from shapely.geometry import box
from tools.dmi_data_parser.dmi_tools import DMITools

class RasterTools:
    """
    Tools for working with rasterio objects
    All tools take open rasterio objects
    """

    def __init__(self, input_path, output_dir):
        self.input_path = input_path
        self.output_path = os.path.join(output_dir, os.path.basename(input_path))
        self.create_empty_raster()
                

    def process_geotiff_within_bbox(self, json_str):
        """
        Multiply the area of a raster within a specified bounding box by a numerical value 
        and overwrite the original GeoTIFF with the processed data.

        Parameters:
        - geotiff_file (str): Path to the GeoTIFF file.
        - bbox_str (str): Bounding box coordinates in the format 
                        '[[[lng1, lat1], [lng2, lat2], ..., [lng1, lat1]]]'.
        - multiplier (float): The value to multiply the raster values by within the bounding box.
        """

        def get_bbox(json_str):
            """
            Takes json string from a DMI climate grid file
            Returns bbox
            """
            return json.loads(json_str)['geometry']['coordinates']
        
        def get_value(json_str):
            """
            Takes json string from a DMI climate grid file
            Returns value associated with parameter
            """
            return json.loads(json_str)['properties']['value']
        
        with rio.open(self.input_path, 'r') as src:
            nodata = src.nodata
                
            bbox_str = get_bbox(json_str)[0]
            bbox_str = DMITools.convert_bbox_to_geotiff_crs(src, bbox_str)
            bbox_polygon = Polygon(bbox_str)
     
            try:
                out_image, _ = mask(src, [bbox_polygon], crop=True)
            except Exception:
                return
            
        if np.all(out_image == -9999): 
            return
        
        out_image = np.where(
            out_image != nodata, 
            (out_image * get_value(json_str) / 10000.0).astype('float32'), 
            nodata
            )

        with rio.open(self.output_path, 'r+') as dst:
            window = rio.features.geometry_window(dst, [bbox_polygon])
            original_data = dst.read(window=window)
            original_data[:, :out_image.shape[1], :out_image.shape[2]] = out_image
            dst.write(original_data, window=window)


    def constrict_dynamic_range(self, range, band = 1):
        """
        Sets all data outside of range to nodata on the destination raster
        
        Parameters:
         - range (tuple): tuple with min and max range numbers
         - band (int): The band to be modified, defaults to first
        """
        with rio.open(self.output_path, 'r+') as dst:
            data = dst.read(band)

            data = np.where(
                (data >= range[0]) & (data <= range[1]), 
                data, 
                dst.nodata
                )
            
            dst.write(data, 1)


    def convert_to_crs(self, src, dst, dst_crs = 'EPSG:4326'):
        """
        Checks the CRS of a GeoTIFF file and converts it to EPSG:4326 if it is not already.

        Parameters:
        - input_file (str): Path to the input GeoTIFF file.
        - output_file (str): Path to the output GeoTIFF file (in EPSG:4326).
        """

        if src.crs.to_string() == dst_crs:
            return

        transform, _, _ = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)

        for i in range(1, src.count + 1):
            reproject(
                source=rio.band(src, i),
                destination=rio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )


    def create_empty_raster(self):
        """
        Creates an empty copy of the raster with the same metadata but no data.

        The source raster and output path are expected to be provided during the
        initialization of the class.

        Returns:
        - rasterio.DatasetWriter: An open rasterio object for the created empty raster.
        """
        with rio.open(self.input_path) as src:
            meta = src.meta.copy()
            meta.update(dtype='float32')

            with rio.open(self.output_path, 'w', **meta) as dst:
                for i in range(1, src.count + 1):
                    empty_band = src.read(i) * 0.0  # Ensure the empty band is float32
                    empty_band[:] = meta['nodata']  # Set all values to nodata
                    dst.write(empty_band.astype('float32'), i)  # Write the band as float32


    def smooth_nodata_pixels(self):
        with rio.open(self.output_path, 'r+') as dst:
            data = dst.read(1)
            nodata_value = dst.nodata
            height, width = data.shape

            smoothed_data = data.copy()

            # Offsets to get the neighboring pixels
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1),  # direct neighbors
                    (-1, -1), (-1, 1), (1, -1), (1, 1)]  # diagonal neighbors

            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if data[y, x] == nodata_value:

                        neighbor_values = []
                        for dy, dx in offsets:
                            neighbor_val = data[y + dy, x + dx]
                            if neighbor_val != nodata_value:
                                neighbor_values.append(neighbor_val)

                        if len(neighbor_values) >= 2:
                            smoothed_data[y, x] = np.mean(neighbor_values)

            dst.write(smoothed_data, 1)


    def multiply_entire_geotiff(self, multiplier, band = 1):

        """
        This tool takes an open rasterio raster object and a value.
        It will take a band number as an optional value, defaulting to band 0
        It is meant to multiply reference ET values with evaporative fraction rasters

        As this is just a single value, it must be assumed that the quality of the 
        local adjustment will fall with distance from that reference values point of origin.
        """

        processed_band = self.src * multiplier

        meta = self.src.meta.copy()
        meta.update(dtype=rio.float32)

        self.dst.write(processed_band.astype(rio.float32), band)