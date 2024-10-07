from datetime import datetime
import os
import json
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.ops import transform as shapely_transform
from pyproj import Transformer
import numpy as np
import rasterio as rio
from rasterio import features
from rasterio.transform import from_bounds
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
    

    def get_value(json_data):
        """
        Takes a JSON object from a DMI climate grid file
        Returns the 'value' parameter
        """
        return json_data['properties']['value']
    

    def get_overlapping_data(dmi_file, et_file, param):
        """
        Takes a DMI climate grid file,  an open rasterio object and a parameter string corresponging to a DMI climate grid parameter.
        Returns a list of the JSON strings which have overlapping bounds with the geotiff.
        If no data overlaps, returns False.
        """

        def process_line(line, raster_bounds, param):
            if not param in line: return

            line = json.loads(line)
            if DMITools.check_bbox_intersection(raster_bounds, line):
                return str(line).replace("'", '"')
                #string formatting required to return what would otherwise be a dict object to json readable string
        
        def convert_src_bounds_to_4326(src):
            """
            Converts the bounds of the GeoTIFF (src) to EPSG:4326.

            Parameters:
            - src: Open rasterio object.

            Returns:
            - bbox_4326: The bounding box of the GeoTIFF in EPSG:4326 coordinates.
            """
            transformer = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
            bounds = src.bounds
            bbox_4326 = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            return Polygon([transformer.transform(x, y) for x, y in bbox_4326.exterior.coords])


        with open(dmi_file, 'r') as file:
               lines = [line.rstrip() for line in file]

        with rio.open(et_file) as src:
            raster_bounds = convert_src_bounds_to_4326(src)

        overlapping_data = []
        for line in lines:
            result = process_line(line, raster_bounds, param)
            if not result == None: overlapping_data.append(result)

        return overlapping_data
    

    def get_parameter_specific_data(dmi_file, param):
        """
        Takes a DMI climate grid file,  an open rasterio object and a parameter string corresponging to a DMI climate grid parameter.
        Returns a list of the JSON strings which have overlapping bounds with the geotiff.
        If no data overlaps, returns False.
        """

        def check_param(line, param):
            if not param in line: 
                return False
            
            return True

        with open(dmi_file, 'r') as file:
               lines = [line.rstrip() for line in file]

        param_data = []
        for line in lines:

            if not check_param(line, param): continue

            line = json.loads(line)
            line = str(line).replace("'", '"')

            param_data.append(line)

        return param_data
    

    def get_all_data(dmi_file, param):
        """
        Takes a DMI climate grid file,  an open rasterio object and a parameter string corresponging to a DMI climate grid parameter.
        Returns a list of the JSON strings which have overlapping bounds with the geotiff.
        If no data overlaps, returns False.
        """

        def process_line(line, param):
            if not param in line: return
            return str(json.loads(line)).replace("'", '"')
            #string formatting required to return what would otherwise be a dict object to json readable string

        with open(dmi_file, 'r') as file:
               lines = [line.rstrip() for line in file]

        param_data = []
        for line in lines:
            result = process_line(line, param)

            if not result == None: param_data.append(result)

        return param_data
    
    
    def check_bbox_intersection(raster_bounds, json_str):
        """
        Check if a bounding box intersects with a GeoTIFF raster.

        Parameters:
        - raster bounds (str): bounds of a raster file. Must match crs of bbox
        - json_str (str): json string from DMI with bounding box coordinates in the format 
                        '[[[lng1, lat1], [lng2, lat2], ..., [lng1, lat1]]]'.

        Returns:
        - bool: True if the bounding box intersects with the raster, False otherwise.
        """

        bbox_str = DMITools.get_bbox(json_str)[0]
        return Polygon(bbox_str).intersects(raster_bounds)


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
    
    def convert_jsons_to_bbox_val(dmi_jsons):
        dmi_tuples = []
        for dmi_json in dmi_jsons:
            dmi_json = json.loads(dmi_json)
            bbox = DMITools.get_bbox(dmi_json)
            value = DMITools.get_value(dmi_json)
            dmi_tuples.append((bbox, value))

        return dmi_tuples


    def json_lines_to_raster(param_filtered_data, output_path):
        """
        Converts a list of GeoJSON-like features into a raster.

        Parameters:
        - param_filtered_data: list of GeoJSON-like features (dictionaries)
        - output_path: path to the output raster file
        """
        # Prepare lists for geometries and values
        geometries = []
        values = []

        for feature in param_filtered_data:
            geom = feature['geometry']
            value = feature['properties']['value']
            shapely_geom = shape(geom)
            geometries.append(shapely_geom)
            values.append(value)

        # Transform geometries to projected CRS (EPSG:25832)
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)

        def project_geom(geom):
            return shapely_transform(transformer.transform, geom)

        projected_geometries = [project_geom(geom) for geom in geometries]

        # Compute the total bounds
        all_geometries = unary_union(projected_geometries)
        minx, miny, maxx, maxy = all_geometries.bounds

        # Define resolution
        pixel_size = 100  # 100 meters

        # Compute raster dimensions
        width = int(np.ceil((maxx - minx) / pixel_size))
        height = int(np.ceil((maxy - miny) / pixel_size))

        # Adjust maxx and maxy to match the computed width and height
        maxx = minx + width * pixel_size
        maxy = miny + height * pixel_size

        transform = from_bounds(minx, miny, maxx, maxy, width, height)

        # Prepare shapes for rasterization
        shapes = ((geom, value) for geom, value in zip(projected_geometries, values))

        # Rasterize
        raster_data = features.rasterize(
            shapes=shapes,
            out_shape=(height, width),
            fill=0,  # Assuming nodata value is 0
            transform=transform,
            dtype=np.float32,
            all_touched=False
        )

        # Write the raster
        with rio.open(
            output_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=raster_data.dtype,
            crs='EPSG:25832',
            transform=transform,
            nodata=0
        ) as dst:
            dst.write(raster_data, 1)