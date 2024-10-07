import os
import re
import csv
import sys
import glob
import rasterio as rio
import numpy as np
from shapely.geometry import Point
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from pyproj import Transformer

def sample_geotiffs_in_radius(folder, location, model, radius=100):
    """
    Samples GeoTIFFs in a specified folder within a radius around a given lat/lon point,
    calculates the average value, and logs the result to a list.

    Parameters:
    - folder (str): Path to the folder containing GeoTIFF files.
    - lat (float): Latitude of the point to sample.
    - lon (float): Longitude of the point to sample.
    - model (string): Which naming scheme should be followd to extract date
    - radius (float): Radius in meters around the point to sample. Default is 25 meters.

    Returns:
    - list: List of dictionaries with filename, date (extracted from filename), and average value.
    """

    option_dict = {
        'sseb_unadj': ('/**/*_ETA.tif', 0.001, -9999),
        'sseb_adj': ('*.tif', False, -9999),
        'metric': ('*_ETA.tif', False, -9999),
    }

    try:
        et_extension, scale_factor, nodata = option_dict[model]
    except Exception as e:
        e.add_note(f'{model} not available as model, script currently supperts:')
        e.add_note('    sseb_unadj, sseb_adj, metric')
        raise

    results = []
    for filename in glob.glob(folder + et_extension):
        if not filename.endswith(".tif"):
            print(f'No files in {folder}')
            continue

        file_path = os.path.join(folder, filename)

        with rio.open(file_path) as src:
            transform = src.transform

            transformer = Transformer.from_crs("EPSG:4326", 'EPSG:32632', always_xy=True)
            point_transformed = transformer.transform(location[0], location[1])
            point_geometry = Point(point_transformed)

            minx = point_transformed[0] - radius
            miny = point_transformed[1] - radius
            maxx = point_transformed[0] + radius
            maxy = point_transformed[1] + radius

            window = from_bounds(minx, miny, maxx, maxy, transform=transform)
            data = src.read(1, window=window)
            
        try:
            mask = geometry_mask([point_geometry], transform=transform, invert=True, out_shape=(data.shape[0], data.shape[1]))
            masked_data = np.ma.masked_array(data, mask=mask)
        except:
            print(f'{filename}')
            continue

        if np.all(masked_data == nodata):
            continue

        masked_data = np.ma.masked_equal(masked_data, nodata)

        if masked_data.count() == 0:
            continue

        if scale_factor: masked_data = masked_data * scale_factor
        
        average_value = masked_data.mean()

        date = extract_date_from_filename(filename, model)

        results.append({
            'filename': filename,
            'date': date,
            'average_value': average_value
        })

    return results


def extract_date_from_filename(filename, model):
    """
    Extracts date string from filenames

    Parameters:
    - filename: (string) filename on a usgs product
    - model: (string) source of filename. Determines how funcion extracts date string

    Returns:
    - date string: YYYYMMDD date string
    """

    def extract_sseb(filename):
        match = re.search(r'\d{8}', os.path.basename(filename))
        if match:
            return match.group(0)
        else:
            raise ValueError("Input does not match SSEB naming convention")

    def extract_metric(filename):
        match = re.search(r'\((\d{8})\)', filename)
        if match:
            return match.group(1)
        else:
            raise ValueError("Input does not match METRIC naming convention")

    extraction_functions = {
        "sseb_unadj": extract_sseb,
        "sseb_adj": extract_sseb,
        "metric": extract_metric,
    }
    
    if model in extraction_functions:
        return extraction_functions[model](filename)
    else:
        raise ValueError(f"Extraction option for {model} does not exist.")


def save_results_to_csv(results, output_csv):
    """
    Saves the sampling results to a CSV file.

    Parameters:
    - results (list): List of dictionaries containing filename, date, and average value.
    - output_csv (str): Path to the output CSV file.
    """
    with open(output_csv, mode='w', newline='') as csv_file:
        fieldnames = ['filename', 'date', 'average_value']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)


def build_csv_name(model, location_name):

    csv_label = {
        'sseb_unadj': 'SSEB_USGS',
        'sseb_adj': 'SSEB_DMI',
        'metric': 'METRIC',
    }[model]

    return os.path.join(output_dir, f'{csv_label}_{location_name}.csv')

if __name__ == "__main__":

    """
    This script takes a folder of rasters and produces a standardized ET csv 
    for plotting

    Takes
    et_file_dir: path to directory with ET rasters
    output_dir: path to output CSVs
    model: name of the ET model that produced the files
    et_sample_points: location coordinates and location name string   
    """

    # et_file_dir = "J:/javej/drought/drought_et/METRIC/"
    # model = 'metric'

    # et_file_dir = "J:/javej/drought/drought_et/adjusted_SSEB/"
    # model = 'sseb_adj'

    et_file_dir = "J:/javej/drought/drought_et/SSEB_files/"
    model = 'sseb_unadj'

    # output_dir = "J:/javej/drought/drought_et/time_series/"
    output_dir = 'test_dir/et_data/'

    #lon, lat and directory in the et_file dir
    et_sample_points = [
        ([55.484757, 11.642088], 'soroe'),
        ([56.038813, 9.160688], 'voulund'),
        ([55.913856, 8.401428], 'skjern'),
        ([56.075209, 9.333798], 'gludsted')
    ]

    os.makedirs(output_dir, exist_ok=True)

    for data in et_sample_points:
        location, location_name = data

        csv_name = build_csv_name(model, location_name)

        results = sample_geotiffs_in_radius(
            os.path.join(et_file_dir, location_name + '/'), 
            location, 
            model, 
        )

        save_results_to_csv(results, csv_name)
