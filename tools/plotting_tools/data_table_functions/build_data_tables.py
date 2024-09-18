from collections import namedtuple
import os
import glob
from pprint import pprint
import sys

class DataTableBuilder:
    def build_et_data_table(csv_files):
        """
        Builds a lookup table using data from CSV files.

        This method processes a list of CSV files, extracts relevant metadata (such as model, adjustment, and location)
        from the filenames, assigns a unique color and line style to each location, and stores the data in a namedtuple.
        It returns a lookup table where each key corresponds to a CSV file and its value is a namedtuple containing the 
        following fields:
        
        - `model`: (str) ET model name
        - `adjustment`: (str) Data source for adjusting ET fraction to  ETA
        - `location`: (str) Measurement location
        - `color`: (int) Color index in color_list
        - `style`: (int) Style index in line_styles
        - `label`: (str) Plot label for legends

        Returns:
        --------
        - `lookup_table`: A dictionary where keys are CSV file paths and values are namedtuples.
        """

        def build_label(csv_file):

            csv_file = os.path.splitext(os.path.basename(csv_file))[0]
            model, adjustment, location = csv_file.split('_')

            return f'{adjustment} adjusted {model}, {location}'

        ntuple = namedtuple('Dataset', ['model', 'adjustment', 'location', 'color', 'style', 'label'])

        lookup_table = {}
        location_styles = {}
        for csv_file in  glob.glob(os.path.join(csv_files, "*.csv")):

            model, adjustment, location = os.path.splitext(os.path.basename(csv_file))[0].split('_')
            label = build_label(csv_file)

            if location in location_styles:
                color, current_style = location_styles[location]
                style = current_style + 1
            else:
                color = len(location_styles)
                style = 0
                location_styles[location] = (color, style)

            lookup_table[csv_file] = ntuple(model, adjustment, location, color, style, label)

        return lookup_table


    def build_aux_table(csv_files):
        """
        Builds a lookup table for ground truth data using data from CSV files.
        
        - `auxtype`: (str) Type of aux data, either cloudcover or groundtruth
        - `product`: (str) Product label from source
        - `location`: (str) Measurement location
        - `label`: (str) Plot label for legends

        Returns:
        --------
        - `lookup_table`: A dictionary where keys are CSV file paths and values are namedtuples.
        """

        ntuple = namedtuple('Dataset', ['auxtype', 'product', 'location', 'label'])
        aux_data_table = {}
        for csv_file in glob.glob(os.path.join(csv_files, "*.csv")):

            auxtype, product, location = os.path.splitext(os.path.basename(csv_file))[0].split('_')

            #could probably reduce to some label lookup dict 
            if auxtype == 'cloudcover':
                label = f'{product} derived cloud cover for {location}'
            elif auxtype == 'groundtruth':
                label = f'{product} derived ground truth for {location}'
            elif auxtype == 'dmi_pet':
                label = f'{product} derived potential ET (DMI) for {location}'
            elif auxtype == 'metric_pet':
                label = f'{product} derived potential ET (METRIC) for {location}'
            elif auxtype == 'albedo':
                label = f'{product} derived albedo for {location}'

            aux_data_table[csv_file] = ntuple(auxtype, product, location, label)

        return aux_data_table
    


            
    # def build_cloud_data_table(csv_files, aux_data_table):
    #     """
    #     Builds a lookup table using data from CSV files.

    #     This method processes a list of CSV files, extracts relevant metadata (such as model, adjustment, and location)
    #     from the filenames, assigns a unique color and line style to each location, and stores the data in a namedtuple.
    #     It returns a lookup table where each key corresponds to a CSV file and its value is a namedtuple containing the 
    #     following fields:
        
    #     - `source`: (str) Distributor of the data
    #     - `product`: (str) Product label from source
    #     - `location`: (str) Measurement location
    #     - `color`: (int) Color (always blue)
    #     - `style`: (int) Style (always dotted)
    #     - `label`: (str) Plot label for legends

    #     Returns:
    #     --------
    #     - `lookup_table`: A dictionary where keys are CSV file paths and values are namedtuples.
    #     """

    #     ntuple = namedtuple('Dataset', ['source', 'product', 'location', 'color', 'style', 'label'])

    #     for csv_file in glob.glob(os.path.join(csv_files, "*.csv")):
    #         source, product, location = os.path.splitext(os.path.basename(csv_file))[0].split('_')
    #         label = f'{source}_{product} scene cloud cover for {location}'

    #         color = 'skyblue'
    #         style = ':'

    #         aux_data_table[csv_file] = ntuple(source, product, location, color, style, label)

    #     return aux_data_table