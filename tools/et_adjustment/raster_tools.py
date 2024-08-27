import rasterio as rio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import Resampling
from rasterio.features import geometry_window
from shapely.geometry import Polygon
import json
import sys
import numpy as np
from tools.dmi_data_parser.dmi_tools import DMITools

class RasterTools:

    def multiply_entire_geotiff(src, multiplier, output_file, band = 1):

        """
        This tool takes an open rasterio raster object and a value.
        It will take a band number as an optional value, defaulting to band 0
        It is meant to multiply reference ET values with evaporative fraction rasters

        As this is just a single value, it must be assumed that the quality of the 
        local adjustment will fall with distance from that reference values point of origin.
        """

        processed_band = src * multiplier

        meta = src.meta.copy()
        meta.update(dtype=rio.float32)

        with rio.open(output_file, 'w', **meta) as dst:
            dst.write(processed_band.astype(rio.float32), band)

    def is_bbox_all_nodata(src, bbox_polygon):
        """
        Check if all pixels within the bounds of a shapely bounding box are src.nodata.

        Parameters:
        - src (rasterio.io.DatasetReader): An open rasterio GeoTIFF object.
        - bbox_polygon (shapely.geometry.Polygon): A shapely Polygon representing the bounding box.

        Returns:
        - bool: True if all pixels within the bounding box are nodata, False otherwise.
        """

        window = geometry_window(src, [bbox_polygon])
        data = src.read(1, window=window)
        return np.all(data == src.nodata)
            

    def process_geotiff_within_bbox(src, output_file, json_str):
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
        bbox_str = DMITools.convert_bbox_to_geotiff_crs(src, bbox_str)
        bbox_polygon = Polygon(bbox_str)

        #check reduces processing time by 25% !!!
        if not RasterTools.is_bbox_all_nodata(src, bbox_polygon):
            return

        out_image, _ = mask(src, [bbox_polygon], crop=True)

        out_image = np.where(
            out_image != src.nodata, 
            (out_image * get_value(json_str) / 10000.0).astype('float32'), 
            src.nodata
            )

        with rio.open(output_file, "r+") as dst:
            window = rio.features.geometry_window(dst, [bbox_polygon])
            original_data = dst.read(window=window)
            original_data[:, :out_image.shape[1], :out_image.shape[2]] = out_image
            dst.write(original_data, window=window)


    def convert_to_4326(input_file, output_file):
        """
        Checks the CRS of a GeoTIFF file and converts it to EPSG:4326 if it is not already.

        Parameters:
        - input_file (str): Path to the input GeoTIFF file.
        - output_file (str): Path to the output GeoTIFF file (in EPSG:4326).
        """
        with rio.open(input_file) as src:
            src_crs = src.crs

            if src_crs.to_string() == 'EPSG:4326':
                return

            dst_crs = 'EPSG:4326'

            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rio.open(output_file, 'w', **kwargs) as dst:
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

    def create_empty_raster(reference_raster, output_raster):
        """
        Creates an empty raster with the same extent and metadata as the reference raster.

        Parameters:
        - reference_raster (str): Path to the original GeoTIFF file.
        - output_raster (str): Path to the output empty GeoTIFF file.
        
        Returns:
        - dst: The open rasterio DatasetWriter object for the created raster.
        """

        with rio.open(reference_raster) as src:
            rio.open(output_raster, 'w', **src.meta.copy())


    def smooth_nodata_pixels(input_file, output_file):
        with rio.open(input_file) as src:
            data = src.read(1)
            nodata_value = src.nodata
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

            with rio.open(
                output_file,
                'w',
                driver=src.driver,
                height=src.height,
                width=src.width,
                count=1,
                dtype=src.dtypes[0],
                crs=src.crs,
                transform=src.transform,
                nodata=nodata_value,
            ) as dst:
                dst.write(smoothed_data, 1)