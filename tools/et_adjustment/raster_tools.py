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
from tools.dmi_data_parser.dmi_tools import DMITools

class RasterTools:
    """
    Tools for working with rasterio objects
    All tools take open rasterio objects
    """

    def __init__(self, input_raster, output_dir):
        self.src = rio.open(input_raster, 'r')
        self.output_path = os.path.join(output_dir, os.path.basename(input_raster))
        # self.dst = self.create_empty_raster()
        self.create_empty_raster()

        # sys.exit()

    
    def close(self):
        self.src.close()
        self.dst.close()


    def get_src(self):
        return self.src
    
    
    def get_dst(self):
        return self.dst
    

    def is_bbox_all_nodata(self, bbox_polygon):
        """
        Check if all pixels within the bounds of a shapely bounding box are src.nodata.

        Parameters:
        - src (rasterio.io.DatasetReader): An open rasterio GeoTIFF object.
        - bbox_polygon (shapely.geometry.Polygon): A shapely Polygon representing the bounding box.

        Returns:
        - bool: True if all pixels within the bounding box are nodata, False otherwise.
        """

        window = geometry_window(self.src, [bbox_polygon])
        data = self.src.read(1, window=window)
        return np.all(data == self.src.nodata)
            

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
        
        bbox_str = get_bbox(json_str)[0]
        bbox_str = DMITools.convert_bbox_to_geotiff_crs(self.src, bbox_str)
        bbox_polygon = Polygon(bbox_str)
        if not self.is_bbox_all_nodata(bbox_polygon):
            return
        
        
        with rio.open(self.output_path, 'r+') as dst:
            out_image, _ = mask(self.src, [bbox_polygon], crop=True)
            print(out_image)

            out_image = np.where(
                out_image != self.src.nodata, 
                (out_image * get_value(json_str) / 10000.0).astype('float32'), 
                self.src.nodata
                )
            
            a = out_image[out_image != self.src.nodata]
            if a: print(a)
            # average_value = np.mean(out_image[out_image != self.src.nodata])
            # if not np.isnan(average_value):
            #     print(f"Avg: {average_value}")
            # sys.exit()
            
            
            window = rio.features.geometry_window(dst, [bbox_polygon])
            original_data = dst.read(window=window)
            original_data[:, :out_image.shape[1], :out_image.shape[2]] = out_image
            dst.write(original_data, window=window)

        return


    def constrict_dynamic_range(self, range, band = 1):
        """
        Sets all data outside of range to nodata on the destination raster
        
        Parameters:
         - range (tuple): tuple with min and max range numbers
         - band (int): The band to be modified, defaults to first
        """
        data = self.dst.read(band)

        data = np.where(
            (data >= range[0]) & (data <= range[1]), 
            data, 
            self.dst.nodata
            )
        
        self.dst.write(data, 1)


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

        meta = self.src.meta.copy()

        with rio.open(self.output_path, 'w', **meta) as dst:
            for i in range(1, self.src.count + 1):
                empty_band = self.src.read(i) * 0
                empty_band[:] = meta['nodata']
                dst.write(empty_band, i)

        # return rio.open(self.output_path, 'r+')

    # def create_empty_raster(self):
    #     """
    #     Creates an empty raster file with the same metadata as the source raster.

    #     The source raster and output path are expected to be provided during the
    #     initialization of the class.

    #     Returns:
    #     - rasterio.DatasetWriter: An open rasterio object for the created empty raster.
    #     """

    #     meta = self.src.meta.copy()
    #     return rio.open(self.output_path, 'w', **meta)


    def smooth_nodata_pixels(self):
        data = self.dst.read(1)
        nodata_value = self.dst.nodata
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

        self.dst.write(smoothed_data, 1)


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