import matplotlib.pyplot as plt
import pandas as pd
# from collections import Counter
# from datetime import datetime
import sys

def plot_landsat_data(data_dict, figure_name = 'figure.png'):
    # Convert the dictionary into a DataFrame for easier manipulation
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df.columns = ['date', 'cloudcover']
    
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M')
    df['week_year'] = df['date'].dt.to_period('W')
    entry_counts = df['month_year'].value_counts().sort_index()
    avg_cloudcover = df.groupby('month_year')['cloudcover'].mean()
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for entry counts
    ax1.bar(entry_counts.index.astype(str), entry_counts.values, label='Landsat 8+9 scenes, >90% cloud colver')
    ax1.set_xlabel('Month-Year')
    ax1.set_ylabel('Landsat images')
    ax1.set_title('Monthly Entries and Cloud Cover')
    
    # Line chart for average cloud cover
    ax2 = ax1.twinx()
    ax2.plot(avg_cloudcover.index.astype(str), avg_cloudcover.values, color='orange', label='Weekly Avg. Cloud Cover')
    ax2.set_ylabel('Average Cloud Cover (%)')

    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.show()
    plt.savefig(figure_name)

