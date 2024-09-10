import glob
import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

class dmi_climate_data_parser:

    """
    Filter a list of JSON strings based on given criteria.
    If a parameter given is None, it will include everything from that parameter

    Example JSON string:
    {
    "geometry":{
        "coordinates":[[[8.3683,55.4046],[8.5262,55.4053],[8.5252,55.4952],[8.3669,55.4945],[8.3683,55.4046]]],
        "type":"Polygon"
        },
        "properties":{
            "calculatedAt":"2023-01-06T15:11:37.734000",
            "cellId":"10km_614_46",
            "created":"2023-05-21T01:44:07.604917+00:00",
            "from":"2023-01-04T23:00:00+00:00",
            "parameterId":"mean_radiation",
            "qcStatus":"manual",
            "timeResolution":"hour",
            "to":"2023-01-05T00:00:00+00:00",
            "value":0
        },
    "type":"Feature",
    "id":"00c8a95f-4a8b-efe5-bce2-6b2290afb70f"
    }


    Parameters:
    - json_strings (list of str): List of JSON strings to filter. Each string should represent a JSON object 
      with a structure similar to the provided example.
    
    - **kwargs: Keyword arguments representing the filtering criteria. These can include:

        - parameterId (list of str): The ID of the parameter being measured. Example: ["mean_radiation"]
        
        - timeResolution (list of str): The temporal resolution of the data. Valid options might include:
            - "hour"
            - "day"
            - "week"
            - "month"
            Example: ["hour", "day"]
        
        - value (list of float or int): The measured value(s) for the parameter. Example: [0, 1.4]
        
        - calculatedAt (list of str or datetime): The timestamp when the value was calculated. 
          Example: ["2023-01-06T15:11:37.734000", datetime(2023, 1, 6, 15, 11, 37, 734000)]
        
        - cellId (list of str): The identifier for the grid cell where the measurement was taken.
          Example: ["10km_614_46"]
          See the spatial resolutions section of DMIs documentation for how to obtain valid grid IDs
          https://opendatadocs.dmi.govcloud.dk/en/Data/Climate_Data
        
        - created (list of str or datetime): The timestamp when the record was created. 
          Example: ["2023-05-21T01:44:07.604917+00:00", datetime(2023, 5, 21, 1, 44, 7, 604917)]
        
        - from (list of str or datetime): The start of the time range for which the data is valid.
          Example: ["2023-01-04T23:00:00+00:00", datetime(2023, 1, 4, 23, 0, 0)]
        
        - to (list of str or datetime): The end of the time range for which the data is valid.
          Example: ["2023-01-05T00:00:00+00:00", datetime(2023, 1, 5, 0, 0, 0)]
        
        - qcStatus (list of str): The quality control status of the data. Example: ["manual"]
        
        - type (list of str): The type of the GeoJSON object. Example: ["Feature"]
          For a list of valid features, see the paramenters section of the DMI climate data API documentation
          https://opendatadocs.dmi.govcloud.dk/en/Data/Climate_Data
        
        - id (list of str): The unique identifier for the JSON object. Example: ["00c8a95f-4a8b-efe5-bce2-6b2290afb70f"]
        
        - geometry (dict): A dictionary representing the geometry of the feature, including:
            - coordinates (list of lists of floats): The coordinates that define the polygon.
              Example: [[[8.3683, 55.4046], [8.5262, 55.4053], [8.5252, 55.4952], [8.3669, 55.4945], [8.3683, 55.4046]]]
            - type (str): The type of the geometry. Typically, "Polygon".
              Example: "Polygon"

    Returns:
    - filtered_json_strings (list of str): List of filtered JSON strings that match all the specified criteria.
    """

    def __init__(self, climate_data_dir, output_dir, **kwargs):

        self.climate_data_files = glob.glob(climate_data_dir + '*.txt')
        self.output_dir = output_dir

        self.criteria = {k: v for k, v in kwargs.items() if v is not None}


    # def parse_files(self):
    #     return [self.file_parser(cf) for cf in self.climate_data_files]

    def parse_files(self):
      with ThreadPoolExecutor(max_workers=10) as executor:
          results = list(executor.map(self.file_parser, self.climate_data_files))
      return results


    def file_parser(self, climate_file):
        with open(climate_file) as file: lines = [line.rstrip() for line in file]

        filtered_data = [self.json_parser(json_string) for json_string in lines if self.json_parser(json_string) is not None]

        os.makedirs(self.output_dir, exist_ok=True)
        filename = os.path.basename(climate_file)
        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, 'w') as file:
            for json_str in filtered_data:
                file.write(json_str + '\n')


    def json_parser(self, json_str):
        """
        Filter a list of JSON strings based on the initialized criteria.

        Parameters:
        - json_strings (list): List of JSON strings to filter.
        """
        
        data = json.loads(json_str)
        properties = data.get("properties", {})
        
        match = True
        for key, allowed_values in self.criteria.items():
            if properties.get(key) is None: continue
            if properties.get(key) not in allowed_values:
                match = False
                break

        # sys.exit()
        if match:
            return json_str

if __name__ == "__main__":
    climate_data_dir = "J:/javej/drought/drought_et/dmi_climate_grid/raw_files/"
    output_dir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_et_files/"
    parameterId = ["pot_evaporation_makkink"]
    # cellId = ['10km_615_66', '10km_621_51', '10km_619_46', '10km_621_52']
    cellId = None


    parser = dmi_climate_data_parser(climate_data_dir, output_dir, parameterId = parameterId, cellId = cellId)
    filtered_climate_data = parser.parse_files()

    print(len(filtered_climate_data))
