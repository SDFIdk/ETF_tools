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

import os
import glob
import sys
import numpy as np
import rasterio as rio
from rasterio.mask import geometry_mask
from rasterio.windows import from_bounds
from pyproj import Transformer
from shapely.geometry import Point

def sample_geotiffs_in_radius(folder, location, model, radius=100):
    """
    Samples GeoTIFFs in a specified folder within a radius around a given lat/lon point,
    calculates the average value, and logs the result to a list.

    Parameters:
    - folder (str): Path to the folder containing GeoTIFF files.
    - location (tuple): (longitude, latitude) of the point to sample.
    - model (string): Which naming scheme should be followed to extract date.
    - radius (float): Radius in meters around the point to sample. Default is 100 meters.

    Returns:
    - list: List of dictionaries with filename, date (extracted from filename), and average value.
    """

    option_dict = {
        'sseb_unadj': ('/**/*_ETA.tif', 0.001, -9999),
        'sseb_adj': ('*.tif', False, -9999),
        'metric': ('*_ETA.tif', False, -9999),
        'SenET2018': ('*ET-day-gf.tif', False, 0),
        'SenET2023': ('*ET-day-gf.tif', False, 0),
    }

    try:
        et_extension, scale_factor, nodata = option_dict[model]
    except KeyError as e:
        e.args += (f"'{model}' not available as model. Script currently supports: sseb_unadj, sseb_adj, metric, SenET2018, SenET2023.",)
        raise

    et_files = glob.glob(os.path.join(folder, et_extension), recursive=True)
    if et_files == []:
        print(f'No files matching {et_extension} in {folder}')
        sys.exit()
        return

    results = []
    for i, filename in enumerate(et_files):
        print(f'Extrating ET values: {i} / {len(et_files) + 1}')

        if not '_2023' in filename:
            continue

        file_path = os.path.join(folder, filename)

        with rio.open(file_path) as src:
            transform = src.transform

            # Correctly transform from EPSG:4326 to the raster's CRS
            transformer = Transformer.from_crs('EPSG:4326', src.crs, always_xy=True)
            point_transformed = transformer.transform(location[0], location[1])

            # Check if the point is within the raster bounds
            if not (src.bounds.left <= point_transformed[0] <= src.bounds.right and
                    src.bounds.bottom <= point_transformed[1] <= src.bounds.top):
                print(f'LOCATION DOES NOT OVERLAP {file_path}')
                continue

            minx = point_transformed[0] - radius
            miny = point_transformed[1] - radius
            maxx = point_transformed[0] + radius
            maxy = point_transformed[1] + radius

            window = from_bounds(minx, miny, maxx, maxy, transform=transform)
            data = src.read(1, window=window)

        try:
            # Adjust the mask creation to match the window's dimensions
            window_transform = src.window_transform(window)
            mask = geometry_mask(
                [Point(point_transformed)],
                transform=window_transform,
                invert=True,
                out_shape=(data.shape[0], data.shape[1])
            )
            masked_data = np.ma.masked_array(data, mask=mask)
        except Exception as e:
            print(f'Error processing file {filename}: {e}')
            continue

        if np.all(masked_data == nodata):
            continue

        masked_data = np.ma.masked_equal(masked_data, nodata)

        if masked_data.count() == 0:
            continue

        if scale_factor:
            masked_data = masked_data * scale_factor

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
        
    def extract_senet(filename):
        match = re.search(r'\((\d{8})\)', os.path.basename(filename))
        if match:
            return match.group(1)
        else:
            raise ValueError("Input does not match SenET naming convention")

    extraction_functions = {
        "sseb_unadj": extract_sseb,
        "sseb_adj": extract_sseb,
        "metric": extract_metric,
        "SenET2018": extract_senet,
        "SenET2023": extract_senet,
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
        'SenET2018': 'SenET-2018',
        'SenET2023': 'SenET-2023',
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
    # model = 'metric_unadj'

    # et_file_dir = "J:/javej/drought/drought_et/adjusted_SSEB/"
    # model = 'sseb_adj'

    # et_file_dir = "J:/javej/drought/drought_et/SSEB_files/"
    # model = 'sseb_unadj'

    # et_file_dir = 'J:/javej/drought/drought_et/dhi_data/data_2018/'
    # model = 'SenET2018'

    et_file_dir = 'J:/javej/drought/drought_et/dhi_data/data_2023/ET/output/20m/denmark/'
    model = 'SenET2023'

    # output_dir = "J:/javej/drought/drought_et/time_series/"
    output_dir = 'DHI_CSV/'

    #lon, lat and directory in the et_file dir
    et_sample_points = [
        ([55.484757, 11.642088], 'soroe'),
        ([56.038813, 9.160688], 'voulund'),
        ([55.913856, 8.401428], 'skjern'),
        ([56.075209, 9.333798], 'gludsted')
    ]

    #if the et_file_dir contains seperate folders named like the et_sample_points, set to True
    location_specific_folder = False

    # --------

    os.makedirs(output_dir, exist_ok=True)
    for data in et_sample_points:
        location, location_name = data

        folder = et_file_dir
        if location_specific_folder:
            folder = os.path.join(et_file_dir, location_name + '/'), 

        csv_name = build_csv_name(model, location_name)

        results = sample_geotiffs_in_radius(
            folder,
            location, 
            model, 
        )

        save_results_to_csv(results, csv_name)
