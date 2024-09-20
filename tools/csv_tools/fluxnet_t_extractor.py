import pandas as pd
import pytz
import glob 
import os

def extract_temperature_data(input_csv, output_csv, date_range=None, time=None):
    df = pd.read_csv(input_csv)

    # Convert TIMESTAMP_START to datetime and then to CET timezone
    utc = pytz.utc
    cet = pytz.timezone('CET')
    df['datetime'] = pd.to_datetime(df['TIMESTAMP_START'], format='%Y%m%d%H%M')
    df['datetime_cet'] = df['datetime'].dt.tz_localize(utc).dt.tz_convert(cet)
    df['date'] = df['datetime_cet'].dt.strftime('%Y%m%d')
    df['time'] = df['datetime_cet'].dt.strftime('%H%M')

    if date_range:
        from_date, to_date = date_range
        df = df[(df['date'] >= from_date) & (df['date'] <= to_date)]

    # Filter out invalid TA_F values (-9999)
    df = df[df['TA_F'] != -9999]

    if time:
        # Filter the data to the specified time
        df = df[df['time'] == time]
    else:
        print("Warning: Time parameter is not specified.")
        return

    if df.empty:
        print(f"Warning: No data available for {date_range[0]} to {date_range[1]} at time {time} in {output_csv}")
        return

    # Prepare the result DataFrame
    result_df = df[['date', 'TA_F']].copy()
    result_df.reset_index(drop=True, inplace=True)
    result_df['id'] = result_df.index
    result_df.rename(columns={'TA_F': 'T_air'}, inplace=True)
    result_df = result_df[['id', 'date', 'T_air']]

    result_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    
    icos_dir = 'J:/javej/drought/drought_et/icos-etc-l2-fluxnet_data/'
    output_dir = 'test_dir/aux_data/'

    auxdata_type = 'air-temperature'
    product = 'ICOS-ETC-L2'

    os.makedirs(output_dir, exist_ok=True)


    name_table = {
        'DK-Vng': 'voulund',
        'DK-Sor': 'soroe',
        'DK-Skj': 'skjern',
        'DK-Gds': 'gludsted',
        }

    for icos_csv in glob.glob(icos_dir + '*.csv'):

        if '!TOC.csv' in icos_csv: 
            continue

        location = name_table[(os.path.basename(icos_csv).split('_')[1])]
        output_filename = f'{auxdata_type}_{product}_{location}.csv'
        output_csv = os.path.join(output_dir, output_filename)

        date_range = ['20230101', '20240101']

        extract_temperature_data(icos_csv, output_csv, date_range, time='1000')
