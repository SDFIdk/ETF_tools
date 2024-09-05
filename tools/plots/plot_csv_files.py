import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime

def read_and_plot_csv_files(csv_folder, output_filename):
    csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))
    
    plt.figure(figsize=(10, 6))  # Set up the plot size

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, usecols=["filename", "date", "average_value"])
        
        try:
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        except: 
            print()
            print(df['date'])
            continue

        df = df[df['average_value'] != -9999]
        df = df.sort_values(by='date')

        plt.plot(df['date'], df['average_value'], label=os.path.basename(csv_file))  # Use the filename as the label

    # plt.xlabel('Date')
    plt.ylabel('Daily evaporation [mm]')
    plt.title('CSV Data Plot')
    plt.legend(loc='best')  # Display a legend with file names
    plt.grid(True)

    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    
    plt.show()

csv_folder = 'test_dir/'
output_filename = 'test_dir/graph.png'
read_and_plot_csv_files(csv_folder, output_filename)
 