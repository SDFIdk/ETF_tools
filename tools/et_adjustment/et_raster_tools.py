import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import Polygon
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
            

    def process_geotiff_within_bbox(src, output_geotiff, json_str, multiplier):
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
            data = json.loads(json_str)
            return data['geometry']['coordinates']

        bbox_str = get_bbox(json_str)
        bbox_coords = json.loads(bbox_str)
        bbox_polygon = [Polygon(bbox_coords[0]).bounds]
        
        with rio.open(output_geotiff) as src:
            out_image, out_transform = mask(src, bbox_polygon, crop=True)
            
            out_image = out_image * multiplier
            
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform})
            
            with rio.open(output_geotiff, "w", **out_meta) as dst:
                dst.write(out_image)

