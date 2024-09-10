import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

from plot_table_tools import PlotTableTools
from plot_utils import PlotUtils

class ETPlotter:

    def __init__(self, et_data, graph_output_dir, ground_truth_data = None, cloud_cover_data = None):

        self.graph_output_dir = graph_output_dir
        os.makedirs(graph_output_dir, exist_ok=True)

        self.et_data_table = PlotTableTools.build_et_data_table(et_data)

        if not ground_truth_data == None:
            self.truth_data_table = PlotTableTools.build_truth_data_table(ground_truth_data)
        else: self.truth_data_table = None

        if not cloud_cover_data == None:
            self.cloud_data_table = PlotTableTools.build_cloud_data_table(cloud_cover_data)
        else: self.cloud_data_table = None

        self.location_style = {} 
        self.et_color_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.et_style_list = ['-', '--', '-.']


    def run_all_plots(self):
        # self.plot_all_data()
        self.plot_data_by_location()
        # self.plot_data_by_location_with_ratio()
        # self.plot_data_by_adjustment()
    

    def update_style_dict(self, csv_file):
        location = PlotUtils.get_location(csv_file)
        if not location in self.location_style:

            #position in color list is determined by number location entries
            color_position = len(self.location_style)    
            self.location_style[location] = [color_position, 0]

            line_color = self.et_color_list[color_position]
            line_style = self.et_style_list[0]
            return line_color, line_style
        
        self.location_style[location][1] += 1    #get new line style, keep same color

        line_color = self.et_color_list[self.location_style[location][0]]
        line_style = self.et_style_list[self.location_style[location][1]]

        return line_color, line_style
    

    def plot_all_data(self):

        plt.figure(figsize=(10, 6))

        for csv_file, metadata in self.et_data_table.items():
            
            data = PlotUtils.get_csv_data(csv_file)

            plt.plot(
                data['date'], 
                data['average_value'], 
                label = metadata.label, 
                color = self.et_color_list[metadata.color], 
                linestyle = self.et_style_list[metadata.style]
            )

        output_filename = os.path.join(self.graph_output_dir, 'all_data.png')

        plt.ylabel('Daily evaporation [mm]')
        plt.title('Daily average ET measurements')
        plt.legend(loc='best')
        plt.grid(True)

        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        # plt.show()


    def plot_data_by_adjustment(self):
        """
        Generates a separate plot for each adjustment, including all entries associated with that adjustment.
        """
        
        # Group data by adjustment
        grouped_by_adjustment = {}
        for csv_file, metadata in self.et_data_table.items():
            if metadata.adjustment not in grouped_by_adjustment:
                grouped_by_adjustment[metadata.adjustment] = []
            grouped_by_adjustment[metadata.adjustment].append((csv_file, metadata))

        for adjustment, data_list in grouped_by_adjustment.items():
            plt.figure(figsize=(10, 6))

            for csv_file, metadata in data_list:
                data = PlotUtils.get_csv_data(csv_file)

                plt.plot(
                    data['date'],
                    data['average_value'],
                    label=f"{metadata.location}",
                    color=self.et_color_list[metadata.color],
                    linestyle=self.et_style_list[metadata.style]
                )

            output_filename = os.path.join(self.graph_output_dir, f"{adjustment}_data.png")

            plt.ylabel('Daily evaporation [mm]')
            plt.title(f'Daily average ET measurements for adjustment {adjustment}')
            plt.legend(loc='best')
            plt.grid(True)

            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            plt.close()


    def plot_data_by_location(self, plot_cloud_cover = False, plot_ground_truth = False):
        """
        Generates a separate plot for each location, including all entries associated with that location.
        """

        grouped_by_location = {}
        for csv_file, metadata in self.et_data_table.items():
            if metadata.location not in grouped_by_location:
                grouped_by_location[metadata.location] = []
            grouped_by_location[metadata.location].append((csv_file, metadata))

        for location, data_list in grouped_by_location.items():
            plt.figure(figsize=(10, 6))

            for csv_file, metadata in data_list:
                data = PlotUtils.get_csv_data(csv_file)

                plt.plot(
                    data['date'],
                    data['average_value'],
                    label=f"{metadata.model} {metadata.adjustment}",
                    color=self.et_color_list[metadata.color],
                    linestyle=self.et_style_list[metadata.style]
                )

            #TODO GET THE RELEVANT CLOUD AND TRUTH DATA FROM THE TABLES AND PLOT THEM

            # print(csv_file)
            # print('AAAA')
            # sys.exit()

            if not self.cloud_cover_data == None and plot_cloud_cover:
                plt.plot(
                    self.cloud_data_table
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
        for csv_file, metadata in self.et_data_table.items():
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
                data = PlotUtils.get_csv_data(csv_file)

                ax1.plot(
                    data['date'],
                    data['average_value'],
                    label=f"{metadata.model} {metadata.adjustment}",
                    color=self.et_color_list[metadata.color],
                    linestyle=self.et_style_list[metadata.style]
                )

            ax1.set_ylabel('Daily evaporation [mm]')
            ax1.set_title(f'Daily average ET measurements for {location}')
            ax1.legend(loc='best')
            ax1.grid(True)

            # Second plot: Ratio between the two plots
            data1 = PlotUtils.get_csv_data(data_list[0][0])
            data2 = PlotUtils.get_csv_data(data_list[1][0])

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


et_csv_folder = 'test_dir/et_data/'
icos_csv_folder = 'test_dir/icos_data/'
cloud_cover_csv_folder = 'test_dir/cloud_cover_data/'
graph_output_dir = 'test_dir/et_graphs/'

et_plotter = ETPlotter(
    et_data = et_csv_folder,
    graph_output_dir = graph_output_dir, 
    ground_truth_data = icos_csv_folder,
    cloud_cover_data = cloud_cover_csv_folder)
et_plotter.run_all_plots()