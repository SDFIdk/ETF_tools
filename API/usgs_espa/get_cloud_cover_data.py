import os
from datetime import datetime
import geopandas as gpd
from eodag import EODataAccessGateway
import csv

def get_cloud_cover(
        start_date, 
        end_date, 
        shape_file, 
        output_path,
        product_type = 'LANDSAT_C2L2', 
        ):
    
    """
    Query for Landsat 8/9 files via EODAG. Please see EODAG documentation for 
    credentials configuration.
    https://eodag.readthedocs.io/en/stable/getting_started_guide/configure.html

    Takes a date range and a file with geometry (shp or gpkg).
    Geometry will be converted to bbox.

    Saves data as CSV at output_path

    """

    dag = EODataAccessGateway()
    dag.set_preferred_provider("usgs")

    search_criteria = {
        'productType': product_type,
        'start': start_date,
        'end': end_date,
        'geom': gpd.read_file(shape_file).total_bounds.tolist()
    }

    search_results = dag.search_all(**search_criteria)

    cloud_data = []
    for result in search_results:

        filename = result.properties["id"]
        date = result.properties["completionTimeFromAscendingNode"]
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d')

        cloud_cover = result.properties["cloudCover"]

        cloud_data.append((filename, date, cloud_cover))

    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'date', 'cloudcover'])
        writer.writerows(cloud_data)


if __name__ == "__main__":

    start_date = "2023-01-01"
    end_date = "2024-01-01"

    shapes = [
        "shapes/gludsted/POLYGON.shp",
        "shapes/skjern/POLYGON.shp",
        "shapes/soroe/POLYGON.shp",
        "shapes/voulund/POLYGON.shp",
    ]

    for shape in shapes:
        product_type = 'LANDSAT_C2L2'

        location =  os.path.basename(os.path.dirname(shape))
        source, product = product_type.split('_')
        csv_file = f'{source}_{product}_{location}.csv'
        csv_dir = "test_dir/cloud_cover_data/"
        output_csv = os.path.join(csv_dir, csv_file)
        os.makedirs(csv_dir, exist_ok=True)

        get_cloud_cover(
            start_date, 
            end_date, 
            shape, 
            output_csv,
            product_type = product_type
            )