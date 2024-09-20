import pandas as pd
import pytz
import glob 
import os

def standardize_icos_data(input_csv, output_csv, date_range=None):

    df = pd.read_csv(input_csv)

    df['id'] = range(len(df))

    # Convert TIMESTAMP_START to datetime and then to CET timezone, extract the date part
    utc = pytz.utc
    cet = pytz.timezone('CET')
    df['date'] = pd.to_datetime(df['TIMESTAMP_START'], format='%Y%m%d%H%M')
    df['date'] = df['date'].apply(lambda x: utc.localize(x).astimezone(cet).strftime('%Y%m%d'))

    if date_range:
        from_date, to_date = date_range
        df = df[(df['date'] >= from_date) & (df['date'] <= to_date)]

    df = df[df['LE'] != -9999]

    # Convert H to ET using the formula: 
    # ET = (LE * 30 * 60) / (2.45 * 1000000)
    # LE = Latent heat [W/m^2], L_v = latent heat of vaporization [MJ/kg]
    L_v = 2.45
    df['ET'] = (df['LE'] * 30 * 60) / (L_v * 1000000)
    # Set negative ET values to 0
    df['ET'] = df['ET'].apply(lambda x: max(x, 0))

    # Group by 'date' and sum the ET values to get daily totals and aggregate to daily total
    daily_totals = df.groupby('date')['ET'].sum().reset_index()
    daily_totals['id'] = range(len(daily_totals))

    result_df = daily_totals[['id', 'date', 'ET']]
    if result_df.empty:
        print(f"Warning: No data available for {date_range[0]} to {date_range[1]} in {output_csv}")
        return
    
    result_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    
    icos_dir = 'J:/javej/drought/drought_et/icos-etc-l2_data/'
    output_dir = 'test_dir/aux_data/'

    auxdata_type = 'groundtruth'
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

        standardize_icos_data(icos_csv, output_csv, date_range)
