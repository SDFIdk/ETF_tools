import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import sys
from pprint import pprint

from data_table_functions.build_data_tables import DataTableBuilder
from data_table_functions.data_table_utils import DataTableUtils
from plot_functions.main_data_plot import MainDataPlot
from plot_functions.plot_utils import PlotUtils
from aux_functions.aux_plotting_tools import AuxPlottingTools

class PlotFunctions:
    """
    This class contains the general framework for the graphs,
    whilst leaving most of the execution to plot and aux utils
    """

    def __init__(self, et_data, graph_output_dir, aux_data = None, date_range = None):
        self.graph_output_dir = graph_output_dir
        os.makedirs(graph_output_dir, exist_ok=True)

        if not date_range is None:
            self.date_range = DataTableUtils.convert_date_range(date_range)
        else:
            self.date_range = None

        self.et_data_table = DataTableBuilder.build_et_data_table(et_data)

        self.aux_data_table = {}
        if not aux_data == None:
            self.aux_data_table = DataTableBuilder.build_aux_table(aux_data)

        self.location_style = {} 
        self.et_color_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self.et_style_list = ['-', '--', '-.']


    def plot_all_data(self):
        plt.figure(figsize=(10, 6))

        for csv_file, metadata in self.et_data_table.items():
            
            data = DataTableUtils.get_et_csv_data(csv_file)

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


    def plot_data_by_location(
            self, 
            plot_cloud_cover=True, 
            plot_ground_truth=True, 
            cloud_resample=None, 
            gtruth_resample=None
    ):
        """
        Generates a separate plot for each location, including all entries associated with that location.
        """

        grouped_by_location = {}
        for csv_file, metadata in self.et_data_table.items():
            if metadata.location not in grouped_by_location:
                grouped_by_location[metadata.location] = []
            grouped_by_location[metadata.location].append((csv_file, metadata))

        for location, data_list in grouped_by_location.items():
            fig, ax1 = plt.subplots(figsize=(10, 6))

            MainDataPlot.plot_csv_list(
                ax1, 
                data_list, 
                data_tag='average_value',
                color_list=self.et_color_list, 
                style_list=self.et_style_list,
                date_range = self.date_range
            )

            ax2, ax3 = None, None
            if plot_cloud_cover:
                ax2 = AuxPlottingTools.plot_cloudcover(
                    ax1,
                    self.aux_data_table,
                    location=location,
                    resample_time=cloud_resample,
                    date_range = self.date_range
                )

            if plot_ground_truth:
                ax3 = AuxPlottingTools.plot_groundtruth(
                    ax1,
                    self.aux_data_table,
                    location=location,
                    resample_time=gtruth_resample,
                    date_range = self.date_range
                )

            PlotUtils.combine_legends(ax1, ax2, ax3, location='upper right')

            ax1.set_ylabel('Daily evaporation [mm]')
            ax1.set_title(f'Daily average ET measurements for {location}')
            ax1.grid(True)

            output_filename = os.path.join(self.graph_output_dir, f"{location}_data.png")
            fig.savefig(output_filename, dpi=300, bbox_inches='tight')

            plt.close(fig)


    def plot_data_by_location_with_ratio(
        self,
        plot_cloud_cover=True, 
        plot_ground_truth=True, 
        cloud_resample=None, 
        gtruth_resample=None
    ):
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
            MainDataPlot.plot_csv_list(
                ax1, 
                data_list, 
                data_tag='average_value',
                color_list=self.et_color_list, 
                style_list=self.et_style_list,
                date_range=self.date_range
            )

            ax1.set_ylabel('Daily evaporation [mm]')
            ax1.set_title(f'Daily average ET measurements for {location}')
            ax1.legend(loc='best')
            ax1.grid(True)

            # Second plot: Ratio between the two plots
            data1 = DataTableUtils.get_et_csv_data(data_list[0][0])
            data2 = DataTableUtils.get_et_csv_data(data_list[1][0])

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


    def plot_data_by_adjustment(
        self, 
        plot_cloud_cover=True, 
        plot_ground_truth=True, 
        cloud_resample=None, 
        gtruth_resample=None
    ):
        """
        Generates a separate plot for each adjustment, including all entries associated with that adjustment.
        This function also adds auxiliary data (cloud cover, ground truth, etc.) to the plot if available.
        """

        grouped_by_adjustment = DataTableUtils.assemble_adjustment_data(self.et_data_table)

        for adjustment, data_list in grouped_by_adjustment.items():
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot the ET data for each location
            MainDataPlot.plot_csv_list(
                ax1, 
                data_list, 
                data_tag='average_value',
                color_list=self.et_color_list, 
                style_list=self.et_style_list,
                date_range=self.date_range
            )
            
            ax1.set_ylabel('Daily evaporation [mm]')
            ax1.set_title(f'Daily average ET measurements for adjustment {adjustment}')
            ax1.grid(True)

            ax2, ax3 = None, None
            if plot_cloud_cover:
                ax2 = AuxPlottingTools.plot_cloudcover(
                    ax1, 
                    self.aux_data_table, 
                    date_range=self.date_range, 
                    resample_time=cloud_resample
                )
            if plot_ground_truth:
                ax3 = AuxPlottingTools.plot_groundtruth(
                    ax1, 
                    self.aux_data_table, 
                    date_range=self.date_range, 
                    resample_time=gtruth_resample
                )

            PlotUtils.combine_legends(ax1, ax2, ax3, location='upper right')

            plt.grid(True)
            output_filename = os.path.join(self.graph_output_dir, f"{adjustment}_data.png")
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            plt.close()