import os
from landsat_product_name_query import landsat_query


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
        csv_file = os.path.basename(os.path.dirname(shape)) + '_cloudcover.csv'
        csv_dir = "test_dir/cloud_cover_data/"
        output_csv = os.path.join(csv_dir, csv_file)
        os.makedirs(csv_dir, exist_ok=True)

        landsat_query.get_cloud_cover(
            start_date, 
            end_date, 
            shape, 
            output_csv
            )