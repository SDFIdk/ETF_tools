import matplotlib.pyplot as plt
from pprint import pprint
import pandas as pd
import sys

from data_table_utils import DataTableUtils
from aux_utils import AuxUtils

class AuxPlottingTools:

    def plot_all_aux(ax1, aux_data_table):
        """
        Plots auxiliary data (cloud cover, ground truth, etc.) onto an existing plot.

        Parameters:
        - ax1 (matplotlib.axes.Axes): The existing left y-axis (primary axis) to plot the main data.
        """

        ax2 = None  #right y-axis
        ax3 = None  #second left y-axis
        for aux_file, aux_metadata in aux_data_table.items():

            aux_data = DataTableUtils.get_aux_csv_data(aux_file)
            color, style, axis, plot_type = DataTableUtils.get_aux_linestyles(aux_metadata.auxtype)

            if aux_metadata.auxtype == 'groundtruth':
                ax1.plot(aux_data['date'], aux_data['value'], label=aux_metadata.label, color=color, linestyle=style)

            elif aux_metadata.auxtype == 'cloudcover':
                if not ax2:
                    ax2 = ax1.twinx()
                    ax2.set_ylabel('Cloud cover (%)')  # Adjust as necessary for the auxiliary type
                if plot_type == 'bar':
                    ax2.bar(aux_data['date'], aux_data['value'], label=aux_metadata.label, color=color)
                else:
                    ax2.plot(aux_data['date'], aux_data['value'], label=aux_metadata.label, color=color, linestyle=style)

        return ax2, ax3
    

    def plot_cloudcover(ax1, aux_data_table, location = None, resample_time = None):

        for aux_file, aux_metadata in aux_data_table.items():

            if not location == None and location == aux_metadata.location:
                continue

            if not aux_metadata.auxtype == 'cloudcover':
                continue

            aux_cloud_data = DataTableUtils.get_aux_csv_data(aux_file)
            color, style, axis, plot_type = DataTableUtils.get_aux_linestyles(aux_metadata.auxtype)

            if not resample_time == None:
                aux_cloud_data = AuxUtils.resample_dataframe(aux_cloud_data, resample_time)

            style = 'plot'

            ax2 = ax1.twinx()
            ax2.set_ylabel('Cloud cover (%)')
            words = aux_metadata.label.split()
            label = ' '.join(words[:-2])

            if plot_type == 'bar':
                ax2.bar(aux_cloud_data['date'], aux_cloud_data['value'], label=label, color=color)
            else:
                ax2.plot(aux_cloud_data['date'], aux_cloud_data['value'], label=label, color=color, linestyle=style)

        return ax2
    

    def plot_avg_cloudcover(ax1, aux_data_table, resample_time = None):
        """
        Plots auxiliary data (cloud cover, ground truth, etc.) onto an existing plot.

        Parameters:
        - ax1 (matplotlib.axes.Axes): The existing left y-axis (primary axis) to plot the main data.
        """

        avg_cloud_data, aux_metadata = AuxUtils.build_avg_cloud_dataframe(aux_data_table)

        if resample_time:
            avg_cloud_data = AuxUtils.resample_dataframe(avg_cloud_data, resample_time)

        color, style, axis, plot_type = DataTableUtils.get_aux_linestyles(aux_metadata.auxtype)

        ax2 = ax1.twinx()
        ax2.set_ylabel('Cloud cover (%)')
        words = aux_metadata.label.split()
        label = ' '.join(words[:-2])

        if plot_type == 'bar':
            ax2.bar(avg_cloud_data['date'], avg_cloud_data['cloudcover'], label=label, color=color)
        else:
            ax2.plot(avg_cloud_data['date'], avg_cloud_data['cloudcover'], label=label, color=color, linestyle=style)

        return ax2
