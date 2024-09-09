import pandas as pd
import glob 

def open_csv(file_path):
    """
    Opens a CSV file and returns it as a pandas DataFrame.
    
    Parameters:
    - file_path (str): Path to the CSV file.
    
    Ret
    urns:
    - pd.DataFrame: DataFrame containing the CSV data.
    """
    return pd.read_csv(file_path, parse_dates=True, index_col='timestamp')  # Assuming 'timestamp' is the time column


def resample_to_24hr(df):
    """
    Resamples the data to 24-hour timesteps via addition.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing the half-hourly data.
    
    Returns:
    - pd.DataFrame: Resampled DataFrame with 24-hour timesteps.
    """
    return df.resample('24H').sum()


def save_to_csv(df, original_file_path):
    """
    Saves the resampled DataFrame to a new CSV file with '_24hr' appended to the filename.
    
    Parameters:
    - df (pd.DataFrame): Resampled DataFrame with 24-hour timesteps.
    - original_file_path (str): The original CSV file path.
    """
    new_file_path = original_file_path.replace('.csv', '_24hr.csv')
    df.to_csv(new_file_path)


def process_csv(file_path):
    df = open_csv(file_path)
    df_24hr = resample_to_24hr(df)
    save_to_csv(df_24hr, file_path)



fluxnet_data = 'path to J drive'
output_folder = 'another path to J drive'

for file_path in glob.glob(fluxnet_data + '*.csv'):

    process_csv(file_path, output_folder)
