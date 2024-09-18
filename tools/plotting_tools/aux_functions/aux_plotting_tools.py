from pprint import pprint
import sys

from data_table_functions.data_table_utils import DataTableUtils
from aux_functions.aux_utils import AuxUtils

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
                ax1.plot(aux_data['date'], aux_data['ET'], label=aux_metadata.label, color=color, linestyle=style)

            elif aux_metadata.auxtype == 'cloudcover':
                if not ax2:
                    ax2 = ax1.twinx()
                    ax2.set_ylabel('Cloud cover (%)')  # Adjust as necessary for the auxiliary type
                if plot_type == 'bar':
                    ax2.bar(aux_data['date'], aux_data['cloudcover'], label=aux_metadata.label, color=color)
                else:
                    ax2.plot(aux_data['date'], aux_data['cloudcover'], label=aux_metadata.label, color=color, linestyle=style)

        return ax2, ax3
    

    def plot_cloudcover(ax1, aux_data_table, date_range, location=None, resample_time=None):
        """
        Plots the cloud cover data on the secondary axis (right Y-axis).

        Parameters:
        - ax1 (matplotlib.axes.Axes): The primary axis for the main data.
        - aux_data_table (dict): A dictionary containing auxiliary data (like cloud cover).
        - location (str, optional): If provided, only plots cloud cover for the matching location. Defaults to None.
        - resample_time (str, optional): Time resampling frequency (e.g., 'W' for weekly, 'M' for monthly). Defaults to None.
        
        Returns:
        - ax2 (matplotlib.axes.Axes or None): The secondary axis for cloud cover, or None if no data is plotted.
        """

        ax2 = None
        for aux_file, aux_metadata in aux_data_table.items():
            # If location is provided, check that it matches the metadata location
            if location is not None and location != aux_metadata.location:
                continue

            if aux_metadata.auxtype != 'cloudcover':
                continue
            aux_cloud_data = DataTableUtils.get_aux_csv_data(aux_file, date_range=date_range)

            if resample_time is not None:
                aux_cloud_data = AuxUtils.resample_dataframe(aux_cloud_data, resample_time)

            color, style, axis, plot_type = DataTableUtils.get_aux_linestyles(aux_metadata.auxtype)

            ax2 = ax1.twinx()
            ax2.set_ylabel('Cloud cover (%)')

            words = aux_metadata.label.split()
            label = ' '.join(words[:-2])

            ax1.set_zorder(2)
            ax1.patch.set_visible(False)

            if plot_type == 'bar':
                if resample_time == 'M':
                    bar_width = 25  # Approximate width for monthly resampling
                elif resample_time == 'W':
                    bar_width = 7  # Approximate width for weekly resampling
                else:
                    # Calculate based on the time delta between the first two dates in the data
                    time_deltas = (aux_cloud_data['date'].iloc[1:] - aux_cloud_data['date'].iloc[:-1]).dt.days
                    bar_width = time_deltas.median() if not time_deltas.empty else 7  # Default width is 7 days

                ax2.bar(
                    aux_cloud_data['date'],
                    aux_cloud_data['cloudcover'],
                    label=label,
                    color=color,
                    width=bar_width,
                    zorder=0  # drawn in the background
                )
            else:
                ax2.plot(
                    aux_cloud_data['date'],
                    aux_cloud_data['cloudcover'],
                    label=label,
                    color=color,
                    linestyle=style,
                    zorder=1  # drawn on top of bars
                )

        if ax2 is None:
            print(f'No data for {location}. Check input data or plot_cloudcover function')

        return ax2


    def plot_groundtruth(ax1, aux_data_table, date_range, location=None, resample_time=None):
        """
        Plots the ground truth data on the secondary axis (left Y-axis, shared with ax1).

        Parameters:
        - ax1 (matplotlib.axes.Axes): The primary axis for the main data.
        - aux_data_table (dict): A dictionary containing auxiliary data (like ground truth).
        - location (str, optional): If provided, only plots ground truth for the matching location. If None, will plot all ground truth data
        - resample_time (str, optional): Time resampling frequency (e.g., 'W' for weekly, 'M' for monthly). Defaults to None.
        
        Returns:
        - ax1 (matplotlib.axes.Axes): The shared axis for ground truth and main data.
        """

        for aux_file, aux_metadata in aux_data_table.items():
            # If location is provided, check that it matches the metadata location
            if location is not None and location != aux_metadata.location:
                continue

            if aux_metadata.auxtype != 'groundtruth':
                continue

            aux_gtruth_data = DataTableUtils.get_aux_csv_data(aux_file, date_range=date_range)
            if resample_time is not None:
                aux_gtruth_data = AuxUtils.resample_dataframe(aux_gtruth_data, resample_time)

            color, style, axis, plot_type = DataTableUtils.get_aux_linestyles(aux_metadata.auxtype)

            # Ensure the ground truth shares the same axis and scale as ax1 (main data)
            if axis == 'second_left':  # Sharing the axis with ax1
                label = aux_metadata.label

                ax1.plot(
                    aux_gtruth_data['date'],
                    aux_gtruth_data['ET'],
                    label=label,
                    color=color,
                    linestyle=style,
                    zorder=1  # Drawn behind model ET data
                )

                ax1.set_zorder(2)  # Keep ax1 (main data) on top
                ax1.patch.set_visible(False)

        return ax1