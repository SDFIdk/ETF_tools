import pandas as pd
import os
import sys

class DataTableUtils:

    def get_et_csv_data(csv_file):
        """
        Opens ET data csv files and returns a sorted and filtered dataframe
        """

        dataframe = pd.read_csv(csv_file, usecols=["filename", "date", "average_value"])

        try:
            dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
        except: 
            print(dataframe['date'])
            return

        dataframe = dataframe[dataframe['average_value'] >= 0]
        dataframe = dataframe.sort_values(by='date')

        return dataframe 

    def get_aux_csv_data(csv_file):
        """
        Opens auxilliary data csv files and returns a sorted and filtered dataframe
        Columns returned are id, date and value. 
        """

        dataframe = pd.read_csv(csv_file)
        dataframe.columns = ['id', 'date', 'value', *dataframe.columns[3:]]

        try:
            dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
        except: 
            print(dataframe['date'])
            return

        dataframe = dataframe[dataframe['value'] >= 0]
        dataframe = dataframe.sort_values(by='date')

        return dataframe   
    

    def get_aux_linestyles(auxtype):
        aux_styles = {
            'cloudcover': ('skyblue', ':', 'right', 'bar'),
            'groundtruth': ('black', ':', 'second_left', 'plot')
        }
        
        if auxtype not in aux_styles:
            raise ValueError(f"'{auxtype}' is not a valid auxiliary type. Valid types are: {', '.join(aux_styles.keys())}")
        
        return aux_styles[auxtype]


    def get_model(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[0]
    
    
    def get_adjustment(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[1]
    
    
    def get_location(self, csv_file):
        return os.path.splitext(os.path.basename(csv_file))[0].split('_')[2]
    

    def plot_auxiliary_data(self, ax1):
        """
        Plots auxiliary data (cloud cover, ground truth, etc.) onto an existing plot.

        Parameters:
        - ax1 (matplotlib.axes.Axes): The existing left y-axis (primary axis) to plot the main data.
        """

        ax2 = None  # This will be the right y-axis
        ax3 = None  # This will be the second left y-axis (for ground truth)

        for aux_file, aux_metadata in self.aux_data_table.items():

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

        # Handle legends for auxiliary axes
        ax1.legend(loc='upper left')
        if ax2:
            ax2.legend(loc='upper right')
        if ax3:
            ax3.legend(loc='lower left')
