from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os
import json
from shapely.geometry import Polygon
from shapely.geometry import box
from pyproj import Transformer
import sys

class DMITools:
    def get_dmi_contents(dmi_file):
        with open(dmi_file, 'r') as file:
            lines = [line.rstrip() for line in file]
        return lines
    
    def datetime_from_landsat(landsat_file):
        """
        Extracts the date from a landsat file with landsat
        standard naming convention
        Example: LC08_L2SP_196021_20230827_20230905_02_T1_ETA.tif
        Returns a datetime object
        """

        landsat_file = os.path.basename(landsat_file)
        landsat_date = landsat_file.split('_')[3]
        return datetime.strptime(landsat_date, '%Y%m%d')


    def file_from_datetime(date, dmi_dir):
        """
        Takes a datetime object and a directory containing DMI gridded climate data
        and returns the file corresponding to the date
        """

        return os.path.join(dmi_dir, date.strftime('%Y-%m-%d') + '.txt')
    
    
    def get_bbox(json_str):
        """
        Takes json string from a DMI climate grid file
        Returns bbox
        """
        return json_str['geometry']['coordinates']
    

    def get_overlapping_data(dmi_file, geotiff, param=None):
        """
        Takes a DMI climate grid file and a geotiff.
        Returns a list of the JSON strings which have overlapping bounds with the geotiff.
        If no data overlaps, returns False.
        If param is given, only data of that parameter will be included.
        """
        def process_line(line):
            line = json.loads(line)
            if param is not None and line['properties']['parameterId'] != param:
                return None
            if not DMITools.check_bbox_intersection(geotiff, line):
                return None
            return str(line).replace("'", '"')
            #string formatting required to return what would otherwise be a dict object to json readable string
        
        with open(dmi_file, 'r') as file:
            lines = [line.rstrip() for line in file]

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_line, lines))

        overlapping_data = [result for result in results if result is not None]

        if not overlapping_data:
            return False

        return overlapping_data
    
    
    def check_bbox_intersection(src, json_str):
        """
        Check if a bounding box intersects with a GeoTIFF raster.

        Parameters:
        - geotiff_file (str): Path to the GeoTIFF file.
        - bbox_str (str): Bounding box coordinates in the format 
                        '[[[lng1, lat1], [lng2, lat2], ..., [lng1, lat1]]]'.

        Returns:
        - bool: True if the bounding box intersects with the raster, False otherwise.
        """

        bbox_str = DMITools.get_bbox(json_str)[0]
        bbox_4326 = DMITools.convert_bbox_to_geotiff_crs(src, bbox_str)
        bbox_polygon = Polygon(bbox_4326)
        raster_bounds = src.bounds
        raster_box = box(raster_bounds.left, raster_bounds.bottom, raster_bounds.right, raster_bounds.top)
        return bbox_polygon.intersects(raster_box)

    def convert_bbox_to_geotiff_crs(src, bbox_4326):
        """
        Converts a bounding box from EPSG:4326 to the CRS of a given GeoTIFF file.

        Parameters:
        - input_file (str): Open rasterio object
        - bbox_4326 (list): List of coordinates representing a bounding box in EPSG:4326.
                            Example: [[12.2837, 55.0025], [12.4397, 54.9982], [12.4474, 55.0879], [12.291, 55.0922], [12.2837, 55.0025]]

        Returns:
        - converted_bbox (list): List of coordinates representing the bounding box in the GeoTIFF's CRS.
        """

        src_crs = src.crs
        transformer = Transformer.from_crs("EPSG:4326", src_crs, always_xy=True)
        return [list(transformer.transform(lon, lat)) for lon, lat in bbox_4326]

