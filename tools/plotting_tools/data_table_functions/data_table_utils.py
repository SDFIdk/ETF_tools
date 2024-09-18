import pandas as pd
import os
from datetime import datetime
import sys

class DataTableUtils:

    # def get_et_csv_data(csv_file, date_range=None):
    #     """
    #     Opens ET data csv files and returns a sorted and filtered dataframe
    #     """

    #     dataframe = pd.read_csv(csv_file, usecols=["filename", "date", "average_value"])

    #     try:
    #         dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
    #     except: 
    #         print(dataframe['date'])
    #         return

    #     dataframe = dataframe[dataframe['average_value'] >= 0]
    #     dataframe = dataframe.sort_values(by='date')

    #     return dataframe 
    

    def get_et_csv_data(csv_file, date_range=None):
        """
        Opens ET data csv files and returns a sorted and filtered dataframe.

        Parameters:
        - csv_file (str): Path to the CSV file.
        - date_range (list): Optional list of two datetime objects [start_date, end_date] for filtering.

        Returns:
        - dataframe (pd.DataFrame): A filtered dataframe.

        Raises:
        - ValueError: If no data remains after filtering or date range is invalid.
        """

        dataframe = pd.read_csv(csv_file, usecols=["filename", "date", "average_value"])

        try:
            dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
        except Exception as e: 
            print(f"Error converting dates in {csv_file}: {e}")
            return

        dataframe = dataframe[dataframe['average_value'] >= 0]

        if date_range:
            start_date, end_date = date_range
            
            if start_date > end_date:
                raise ValueError("Start date cannot be later than end date.")

            dataframe = dataframe[(dataframe['date'] >= start_date) & (dataframe['date'] <= end_date)]

        dataframe = dataframe.sort_values(by='date')
        if dataframe.empty:
            raise ValueError(f"No data found for the specified date range in {csv_file}.")

        return dataframe


    # def get_aux_csv_data(csv_file, set_negative_to_zero=False, date_range=None):
    #     """
    #     Opens auxiliary data CSV files and returns a sorted and filtered DataFrame.
    #     Ensures the columns 'id', 'date', and keeps the original name of the third column.
        
    #     Parameters:
    #     - csv_file (str): Path to the CSV file.
    #     - set_negative_to_zero (bool): Whether to set values below zero to zero. Default is False.
        
    #     Returns:
    #     - DataFrame: Sorted DataFrame with 'id', 'date', and the original third column name.
    #     """

    #     dataframe = pd.read_csv(csv_file)

    #     original_third_column = dataframe.columns[2]
    #     dataframe.columns = ['id', 'date', original_third_column, *dataframe.columns[3:]]

    #     try:
    #         dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
    #     except:
    #         print(f"Error converting date format in file: {csv_file}")
    #         return None

    #     if set_negative_to_zero:
    #         dataframe[original_third_column] = dataframe[original_third_column].apply(lambda x: max(0, x))

    #     dataframe = dataframe.sort_values(by='date')
    #     return dataframe


    def get_aux_csv_data(csv_file, set_negative_to_zero=False, date_range=None):
        """
        Opens auxiliary data CSV files and returns a sorted and filtered DataFrame.
        Ensures the columns 'id', 'date', and keeps the original name of the third column.
        
        Parameters:
        - csv_file (str): Path to the CSV file.
        - set_negative_to_zero (bool): Whether to set values below zero to zero. Default is False.
        - date_range (list): Optional list of two datetime objects [start_date, end_date] for filtering.
        
        Returns:
        - DataFrame: Sorted DataFrame with 'id', 'date', and the original third column name.
        
        Raises:
        - ValueError: If no data remains after filtering or date range is invalid.
        """
        
        dataframe = pd.read_csv(csv_file)

        original_third_column = dataframe.columns[2]
        dataframe.columns = ['id', 'date', original_third_column, *dataframe.columns[3:]]

        try:
            dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y%m%d')
        except Exception as e:
            print(f"Error converting date format in file: {csv_file}. Error: {e}")
            return None

        if set_negative_to_zero:
            dataframe[original_third_column] = dataframe[original_third_column].apply(lambda x: max(0, x))

        if date_range:
            start_date, end_date = date_range
            
            dataframe = dataframe[(dataframe['date'] >= start_date) & (dataframe['date'] <= end_date)]

        dataframe = dataframe.sort_values(by='date')
        if dataframe.empty:
            raise ValueError(f"No data found for the specified date range in {csv_file}.")

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
    

    def assemble_adjustment_data(et_data_table):

        adjustment_table = {}
        for csv_file, metadata in et_data_table.items():
            if metadata.adjustment not in adjustment_table:
                adjustment_table[metadata.adjustment] = []
            adjustment_table[metadata.adjustment].append((csv_file, metadata))

        return adjustment_table
    

    def convert_date_range(date_strings):
        """
        Converts a list of YYYYMMDD date strings to a list of datetime objects.

        Parameters:
        - date_strings (list of str): List of dates in YYYYMMDD format.

        Returns:
        - List of datetime objects.

        Raises:
        - ValueError: If the second date is earlier than the first.
        """
        try:
            dates = [datetime.strptime(date_str, '%Y%m%d') for date_str in date_strings]

            if len(dates) > 1 and dates[1] < dates[0]:
                raise ValueError("The second date cannot be before the first date.")

            return dates
        except ValueError as e:
            raise ValueError(f"Error converting dates: {e}")