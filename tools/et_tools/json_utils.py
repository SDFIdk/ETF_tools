import json

class JSONUtils:
    
    def get_bbox(json_str):
        """
        Takes json string from a DMI climate grid file
        Returns bbox coordinates
        """
        return json.loads(json_str)['geometry']['coordinates']
    
    def get_value(json_str):
        """
        Takes json string from a DMI climate grid file
        Returns the value associated with the parameter
        """
        return json.loads(json_str)['properties']['value']