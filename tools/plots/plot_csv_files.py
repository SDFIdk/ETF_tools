import pandas as pd
import matplotlib.pyplot as plt
from collections import namedtuple
import glob
import os
import sys
import numpy as np

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

            model, adjustment, location = os.path.splitext(os.path.basename(csv_file))[0].split('_')
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
        # self.plot_all_data()
        # self.plot_data_by_location()
        self.plot_data_by_location_with_ratio()


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
        # plt.show()


    def plot_data_by_location(self):
        """
        Generates a separate plot for each location, including all entries associated with that location.
        """

        grouped_by_location = {}
        for csv_file, metadata in self.data_table.items():
            if metadata.location not in grouped_by_location:
                grouped_by_location[metadata.location] = []
            grouped_by_location[metadata.location].append((csv_file, metadata))

        for location, data_list in grouped_by_location.items():
            plt.figure(figsize=(10, 6))

            for csv_file, metadata in data_list:
                data = self.get_csv_data(csv_file)

                plt.plot(
                    data['date'],
                    data['average_value'],
                    label=f"{metadata.model} {metadata.adjustment}",
                    color=self.color_list[metadata.color],
                    linestyle=self.style_list[metadata.style]
                )

            output_filename = os.path.join(self.graph_output_dir, f"{location}_data.png")

            plt.ylabel('Daily evaporation [mm]')
            plt.title(f'Daily average ET measurements for {location}')
            plt.legend(loc='best')
            plt.grid(True)

            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            # plt.show()
            plt.close()
            
    def plot_data_by_location_with_ratio(self):
        """
        Generates two subplots for each location:
        1. The top plot shows the original data.
        2. The bottom plot shows the ratio of the two data sets with a center line at y=0.
        """
        
        grouped_by_location = {}
        for csv_file, metadata in self.data_table.items():
            if metadata.location not in grouped_by_location:
                grouped_by_location[metadata.location] = []
            grouped_by_location[metadata.location].append((csv_file, metadata))

        for location, data_list in grouped_by_location.items():
            if len(data_list) != 2:
                print(f"Skipping {location} - requires exactly two plots for the ratio calculation.")
                continue

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

            # First plot: Original data
            for csv_file, metadata in data_list:
                data = self.get_csv_data(csv_file)

                ax1.plot(
                    data['date'],
                    data['average_value'],
                    label=f"{metadata.model} {metadata.adjustment}",
                    color=self.color_list[metadata.color],
                    linestyle=self.style_list[metadata.style]
                )

            ax1.set_ylabel('Daily evaporation [mm]')
            ax1.set_title(f'Daily average ET measurements for {location}')
            ax1.legend(loc='best')
            ax1.grid(True)

            # Second plot: Ratio between the two plots
            data1 = self.get_csv_data(data_list[0][0])
            data2 = self.get_csv_data(data_list[1][0])

            data1['date'] = pd.to_datetime(data1['date'])
            data2['date'] = pd.to_datetime(data2['date'])

            df1 = pd.DataFrame({'date': data1['date'], 'average_value': data1['average_value']})
            df2 = pd.DataFrame({'date': data2['date'], 'average_value': data2['average_value']})

            merged_df = pd.merge(df1, df2, on='date', how='inner', suffixes=('_1', '_2'))

            merged_df['ratio'] = np.divide(merged_df['average_value_1'], merged_df['average_value_2'],
                                        out=np.zeros_like(merged_df['average_value_1']),
                                        where=merged_df['average_value_2'] != 0)

            ax2.plot(
                merged_df['date'],
                merged_df['ratio'],
                label=f"Ratio: {data_list[0][1].model} / {data_list[1][1].model}",
                color="blue",
                linestyle="-"
            )

            ax2.axhline(1, color="red", linestyle="--")  # Center line at y=1
            ax2.set_ylabel('Ratio')
            ax2.set_xlabel('Date')
            ax2.legend(loc='best')
            ax2.grid(True)

            output_filename = os.path.join(self.graph_output_dir, f"{location}_data_with_ratio.png")

            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            plt.close()


csv_folder = 'test_dir/'
graph_output_dir = 'test_dir/graphs'

et_plotter = ETPlotter(csv_folder, graph_output_dir)
et_plotter.run_all_plots()
 