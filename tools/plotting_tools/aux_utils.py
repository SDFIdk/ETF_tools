import pandas as pd

class AuxUtils:

    # def resample_dataframe(df, resample_time):
    #     """
    #     Resamples the given DataFrame to the specified time interval using Pandas-compatible resampling keywords.
    #     """
    #     try:
    #         return df.resample(resample_time, on='date').mean().reset_index()
    #     except Exception as e:
    #         raise ValueError(f"Invalid resampling period '{resample_time}': {e}")


    #TODO find out why this resampler doesnt work now. There are obviously inconsistencies between the aux data and et data tables.

    def resample_dataframe(df, resample_time):
        """
        Resamples the given DataFrame to the specified time interval using Pandas-compatible resampling keywords.
        If the 'date' column is not in datetime format, it attempts to convert it from either 'yyyymmdd' or 'yyyy-mm-dd'.
        """
        # Check if 'date' column is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            # Attempt to parse 'yyyymmdd' or 'yyyy-mm-dd' formats
            try:
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            except ValueError:
                try:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                except ValueError as e:
                    raise ValueError(f"Date format not recognized. Ensure 'date' is in 'yyyymmdd' or 'yyyy-mm-dd' format: {e}")

        # Perform resampling
        try:
            return df.resample(resample_time, on='date').mean().reset_index()
        except Exception as e:
            raise ValueError(f"Invalid resampling period '{resample_time}': {e}")

        
        
    def build_avg_cloud_dataframe(aux_data_table):
        """
        Combines data from all cloudcover data CSVs into a single average cloudcover dataframe
        """
        cloudfiles = []
        for aux_file, aux_metadata in aux_data_table.items():
            if not aux_metadata.auxtype == 'cloudcover':
                continue

            cloudfiles.append(aux_file)
            cc_metadata = aux_metadata
        return AuxUtils.average_csv_data(cloudfiles), cc_metadata
    
    
    def average_csv_data(csv_files):
        """
        Reads multiple CSV files, computes the average values for each date,
        and returns a combined DataFrame.

        Parameters:
        - csv_files (list): List of paths to CSV files

        Returns:
        - combined_df (pd.DataFrame): DataFrame containing averaged values per date
        """

        all_data = []
        for file in csv_files:

            df = pd.read_csv(file)
            df['date'] = df['date'].astype(str)
            df_grouped = df.groupby('date', as_index=False)['cloudcover'].mean()
            all_data.append(df_grouped)

        combined_df = pd.concat(all_data).groupby('date', as_index=False)['cloudcover'].mean()
        combined_df['id'] = range(1, len(combined_df) + 1)
        combined_df = combined_df[['id', 'date', 'cloudcover']]
        combined_df['date'] = pd.to_datetime(combined_df['date'], format='%Y%m%d')

        return combined_df