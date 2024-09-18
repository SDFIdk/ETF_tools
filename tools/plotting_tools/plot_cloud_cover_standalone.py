import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys
import os

def plot_cloudcover(csv_file, output_filename, location):
    """
    Reads a CSV file containing 'id', 'date', and 'cloudcover' columns, and plots a graph of cloud cover over time.

    Parameters:
    - csv_file (str): Path to the CSV file.

    Example:
    plot_cloudcover('output.csv')
    """
    df = pd.read_csv(csv_file)
    
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['cloudcover'], marker='o', linestyle='-', color='b')

    avg_cloudcover = df['cloudcover'].mean()
    title = f'{location} cloud cover, average = {avg_cloudcover:.2f}%'

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Cloud Cover (%)')
    
    plt.xticks(rotation=45)
    
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')


if __name__ == "__main__":

    cc_data_dir = 'test_dir/cloud_cover_data/'
    graph_output_dir = 'test_dir/cloud_cover_graphs/'

    os.makedirs(graph_output_dir, exist_ok = True)
    for cc_csv in glob.glob(cc_data_dir + '*.csv'):

        location = os.path.splitext(os.path.basename(cc_csv))[0].split('_')[0].capitalize()

        output_filename = os.path.splitext(os.path.basename(cc_csv))[0] + '.png'
        cc_output = os.path.join(graph_output_dir, output_filename)

        plot_cloudcover(cc_csv, cc_output, location)

