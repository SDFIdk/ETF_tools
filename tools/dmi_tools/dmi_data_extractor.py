#should take a date, cellid and property. 
#first, search files for matching date, then file for matching tile with matching property. Return number

import glob
import sys
import os
import json
from datetime import datetime

class climate_data_searcher:
    """
    Tools for handling DMI gridded climate data. 
    Assumes filenames in format YYYY-MM-DD.txt

    While this will work on data directly from DMI, using the filter function ahead of time will speed up use.
    """

    def __init__(self, climate_data_dir, filter_params = False, filter_dates = False, filter_tiles = False):

        def build_climate_file_list(climate_data_dir):
            climate_files = []
            for climate_file in glob.glob(climate_data_dir + '*.txt'):
                date = os.path.basename(os.path.splitext(climate_file)[0])
                date = datetime.strptime(date, "%Y-%m-%d")

                climate_files.append((date, climate_file))

            return climate_files

        #TODO Implement the different filters
        params = [filter_params, filter_dates, filter_tiles]
        if all(param is False or param is None for param in params):
            pass
        
        self.climate_files = build_climate_file_list(climate_data_dir)


    def search_climate_parameters(self, param, date, tile, coordinates = False):

        """
        Takes a parameter, date and tile ID and returns the corresponding
        value from DMI Gridded Climate Data
        
        If coordinates == True, the script will also return corresponding bbox coordinates
        """
        #TODO maybe return a list of results if one or more parameters are unfilled?

        def find_climate_file(climate_files, search_date):
            for file_date, filename in climate_files:
                if datetime.strptime(search_date, "%Y-%m-%d") == file_date:
                    return filename
                
            print(f'{search_date} not in climate file list. Is the climate data filtered too aggressively?')
            return None

        def search_climate_file(climate_file, param, tile):
            with open(climate_file, 'r') as file:
                lines = [line.rstrip() for line in file]
                for json_str in lines:
                    data = json.loads(json_str)
                    if not tile == data['properties']['cellId']:
                        continue
                    if not param == data['properties']['parameterId']:
                        continue
                    
                    return data['properties']['value']
                
                print(f'Either {tile} or {param} not in {climate_file}. Is the climate data filtered too aggressively?')
                return None

        if not param or not date or not tile:
            raise ValueError("All inputs (param, date, tile) must be provided and cannot be None or False.")
        
        climate_file = find_climate_file(self.climate_files, date)
        if climate_file == None: return None
        value = search_climate_file(climate_file, param, tile)
        if value == None: return None
        return value
    

if __name__ == "__main__":
    climate_data_dir = "J:/javej/dmi_climate_grid/"
    output_file_dir = "/"
    parameter = "pot_evaporation_makkink"
    tile = '10km_615_66'
    date = '2023-05-07'


    parser = climate_data_searcher(climate_data_dir)
    filtered_climate_data = parser.search_climate_parameters(date = date, param = parameter, tile = tile)

    print(filtered_climate_data)
