import rasterio as rio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from shapely.geometry import Polygon
from pyproj import Transformer
import json

class ETRasterTools:

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
            

    def process_geotiff_within_bbox(src, output_geotiff, json_str):
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
        bbox_polygon = [Polygon(bbox_str).bounds]
        
        with rio.open(output_geotiff) as src:
            out_image, out_transform = mask(src, bbox_polygon, crop=True)
            
            out_image = out_image * get_value(json_str)
            
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform})
            
            with rio.open(output_geotiff, "w", **out_meta) as dst:
                dst.write(out_image)


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

