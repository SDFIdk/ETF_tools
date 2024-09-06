import pandas as pd
import matplotlib.pyplot as plt
from collections import namedtuple
import glob
import os
import sys

class ETPlotter:

    def __init__(self, csv_folder, graph_output_dir):
        self.csv_files = csv_folder
        self.csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))

        self.graph_output_dir = graph_output_dir
        os.makedirs(graph_output_dir, exist_ok=True)

        self.data_table = self.build_data_table()

        self.location_style = {} 
        self.color_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.style_list = ['-', '--', '-.', ':']


    def build_data_table(self):
        """
        Builds a lookup table using data from CSV files.

        This method processes a list of CSV files, extracts relevant metadata (such as model, adjustment, and location)
        from the filenames, assigns a unique color and line style to each location, and stores the data in a namedtuple.
        It returns a lookup table where each key corresponds to a CSV file and its value is a namedtuple containing the 
        following fields:
        
        - `model`: (str) ET model name
        - `adjustment`: (str) Data source for adjusting ET fraction to  ETA
        - `location`: (str) Measurement location
        - `color`: (int) Color index in self.color_list
        - `style`: (int) Style index in self.line_styles
        - `label`: (str) Plot label for legends

        Returns:
        --------
        - `lookup_table`: A dictionary where keys are CSV file paths and values are namedtuples.
        """

        ntuple = namedtuple('Dataset', ['model', 'adjustment', 'location', 'color', 'style', 'label'])

        lookup_table = {}
        location_styles = {}

        for csv_file in self.csv_files:

            model, adjustment, location = os.path.basename(csv_file).split('_')
            label = self.build_label(csv_file)

            if location in location_styles:
                color, current_style = location_styles[location]
                style = current_style + 1
            else:
                color = len(location_styles)
                style = 0
                location_styles[location] = (color, style)

            lookup_table[csv_file] = ntuple(model, adjustment, location, color, style, label)

        return lookup_table
    

    def run_all_plots(self):
        self.plot_all_data(self)
        # self.


    def build_label(self, csv_file):

        csv_file = os.path.splitext(os.path.basename(csv_file))[0]
        model, adjustment, location = csv_file.split('_')

        return f'{adjustment} adjusted {model}, {location}'
    

    def get_model(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[0]
    
    
    def get_adjustment(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[1]
    
    
    def get_location(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[2]
    

    def update_style_dict(self, csv_file):
        location = self.get_location(csv_file)
        if not location in self.location_style:

            #position in color list is determined by number location entries
            color_position = len(self.location_style)    
            self.location_style[location] = [color_position, 0]

            line_color = self.color_list[color_position]
            line_style = self.style_list[0]
            return line_color, line_style
        
        self.location_style[location][1] += 1    #get new line style, keep same color

        line_color = self.color_list[self.location_style[location][0]]
        line_style = self.style_list[self.location_style[location][1]]

        return line_color, line_style
    
    
    def get_csv_data(self, csv_file):
        """
        Opens ET data csv files and returns a sorted and filtered dataframe
        """

        df = pd.read_csv(csv_file, usecols=["filename", "date", "average_value"])

        try:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        except: 
            print(df['date'])
            return

        df = df[df['average_value'] >= 0]
        df = df.sort_values(by='date')

        return df    


    def plot_all_data(self):

        plt.figure(figsize=(10, 6))

        for csv_file, metadata in self.data_table.items():
            
            data = self.get_csv_data(csv_file)

            plt.plot(
                data['date'], 
                data['average_value'], 
                label = metadata.label, 
                color = self.color_list[metadata.color], 
                linestyle = self.style_list[metadata.style]
            )

        output_filename = os.path.join(self.graph_output_dir, 'all_data.png')

        plt.ylabel('Daily evaporation [mm]')
        plt.title('Daily average ET measurements')
        plt.legend(loc='best')
        plt.grid(True)

        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.show()



csv_folder = 'test_dir/'
graph_output_dir = 'test_dir/graphs'

et_plotter = ETPlotter(csv_folder, graph_output_dir)
# et_plotter.run_all_plots()

et_plotter.plot_all_data()
 