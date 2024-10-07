import sys
from pprint import pprint

from plot_functions.plot_frameworks import PlotFunctions

def run_all_plots():
    plot_functions.plot_all_data()
    plot_functions.plot_by_location(cloud_resample='M', gtruth_resample = 'W')
    plot_functions.plot_by_location_with_ratio()
    plot_functions.plot_by_adjustment(cloud_resample='M', gtruth_resample = 'W')


if __name__ == '__main__':
    
    et_csv_folder = 'test_dir/et_data/'
    aux_csv_folder = 'test_dir/aux_data/'
    graph_output_dir = 'test_dir/et_graphs/'

    #list of two YYYYMMDD 
    # date_range = ['20230501', '20230901']
    date_range = None

    plot_functions = PlotFunctions(
        et_data = et_csv_folder,
        graph_output_dir = graph_output_dir, 
        aux_data = aux_csv_folder,
        date_range = date_range,
    )

    run_all_plots()