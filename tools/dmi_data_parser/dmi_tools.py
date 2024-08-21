from datetime import datetime
import os
import json
from shapely.geometry import Polygon
from shapely.geometry import box

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
        data = json.loads(json_str)
        return data['geometry']['coordinates']
    
    
    def get_overlapping_data(dmi_file, geotiff, param = None):
        """
        Takes a DMI climate grid file and a geotiff.
        Returns a list of the JSON strings which have overlapping bounds with the geotiff
        If no data overlaps, returns False
        If param is given only data of that parameter will be included
        """
        with open(dmi_file, 'r') as file:
            lines = [line.rstrip() for line in file]

        overlapping_data = []
        for line in lines:
            if not DMITools.check_bbox_intersection(geotiff, line):
                continue
            if param == None or line['properties']['parameterId'] != param:
                continue
            overlapping_data.append(line)

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
        print('a')
        print(bbox_str)
        bbox_polygon = Polygon(bbox_str)
        print('b')
        raster_bounds = src.bounds
        print('c')
        raster_box = box(raster_bounds.left, raster_bounds.bottom, raster_bounds.right, raster_bounds.top)
        print('d')
        return bbox_polygon.intersects(raster_box)


# if __name__ == '__main__':
#     ls = 'LC08_L2SP_196021_20230827_20230905_02_T1_ETA.tif'
#     d = DMIFileTools.datetime_from_landsat(ls)
#     print(d)
#     dmidir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_data/"
#     dmifile = DMIFileTools.dmi_file_from_datetime(d, dmidir)
#     print(dmifile)