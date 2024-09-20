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

def sample_geotiffs_in_radius(aux_files, location, auxdata_type, radius=100, data_tag = 'average_value', nodata = -9999):
    """
    Samples GeoTIFFs in a specified folder within a radius around a given lat/lon point,
    calculates the average value, and logs the result to a list.

    Parameters:
    - folder (str): Path to the folder containing GeoTIFF files.
    - lat (float): Latitude of the point to sample.
    - lon (float): Longitude of the point to sample.
    - auxdata_type (string): Which naming scheme should be followed to extract date
    - radius (float): Radius in meters around the point to sample. Default is 25 meters.

    Returns:
    - list: List of dictionaries with filename, date (extracted from filename), and average value.
    """

    results = []
    for filename in aux_files:

        with rio.open(filename) as src:
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
        
        average_value = masked_data.mean()

        date = extract_date_from_filename(filename, auxdata_type)

        results.append({
            'filename': filename,
            'date': date,
            data_tag: average_value
        })

    return results


def extract_date_from_filename(filename, auxdata_type):
    """
    Extracts date string from filenames

    Parameters:
    - filename: (string) filename on a usgs product
    - model: (string) source of filename. Determines how funcion extracts date string

    Returns:
    - date string: YYYYMMDD date string
    """

    def extract_dmi(filename):
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
        "dmi-pet": extract_dmi,
        "metric_albedo": extract_metric,
        # "metric": extract_metric,
    }
    
    if auxdata_type in extraction_functions:
        return extraction_functions[auxdata_type](filename)
    else:
        raise ValueError(f"Extraction option for {auxdata_type} does not exist.")


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


if __name__ == "__main__":

    """
    This script takes a folder of rasters and produces a standardizet AUX csv 
    for plotting

    Important! auxdata_type, product and location may not contain underscores!

    Takes
    aux_files: list of files to process
    output_dir: path to output CSVs
    auxdata_type: string with name of the data type
    product: string with name of data product from distributor
    et_sample_points: location coordinates and location name string   
    data_tag: label for data column in CSV, defaults to 'average_value'
    """

    # et_file_dir = "J:/javej/drought/drought_et/METRIC/"
    # model = 'metric'

    # et_file_dir = "J:/javej/drought/drought_et/adjusted_SSEB/"
    # model = 'sseb_adj'

    aux_dir = "J:/javej/drought/drought_et/dmi_PET_raster/"
    
    auxdata_type = 'dmi-pet'
    product = 'pot-evaporation-makkink'
    data_tag = 'PET_ET'

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

        csv_name = f'{auxdata_type}_{product}_{location}.csv'

        aux_files = glob.glob(os.path.join(aux_files, location_name + '/') + '*.tif')

        results = sample_geotiffs_in_radius(
            aux_files, 
            location, 
            auxdata_type, 
            data_tag = data_tag
        )

        save_results_to_csv(results, csv_name)
