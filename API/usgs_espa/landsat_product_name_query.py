import geopandas as gpd
import sys
import os 
from eodag import EODataAccessGateway
import geopandas as gpd


from plot_stats import plot_landsat_data


class landsat_query:

    def analyze_stats(query_results, shape_file, figure_name = None):

        def get_id_from_landsat_products(landsat_product):
            return [l.properties["id"] for l in landsat_product]

        def get_date_from_landsat_products(landsat_product):
            return [l.properties["id"][17:25] for l in landsat_product]
        
        def get_cloudcover_from_landsat_products(landsat_product):
            return [l.properties["cloudCover"] for l in landsat_product]

        ids = get_id_from_landsat_products(query_results)
        dates = get_date_from_landsat_products(query_results)
        cloudcover = get_cloudcover_from_landsat_products(query_results)

        stat_dict = {ids[i]: (dates[i], cloudcover[i]) for i in range(len(ids))}

        if figure_name is None: 
            figure_name = os.path.splitext(os.path.basename(shape_file))[0]
        plot_landsat_data(stat_dict, figure_name = figure_name)

        return stat_dict

    def query_landsat_eodag(
            start_date, 
            end_date, 
            shape_file, 
            cloudcover = 90, 
            product_type = 'LANDSAT_C2L2', 
            output_stats = False, 
            ):
        
        """
        Query for Landsat 8/9 files via EODAG. Please see EODAG documentation for 
        credentials configuration.
        https://eodag.readthedocs.io/en/stable/getting_started_guide/configure.html

        Takes a date range and a file with geometry (shp or gpkg).
        Geometry will be converted to bbox.

        Returns a list of product ids
        NOTE: This function does not download queried data, as ESPA only required a
        list of product names, not the products themselves.

        If output_stats == True the function will also output a histogram of product availability with 
        monthly average cloud cover percentages. 
        Stats will also be returned as a list of dates and cloud cover percentages.
        If a figure name is not provided, the name of the geometry file will be used instead
        and saved as .png

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

        filtered_products = [p for p in search_results if p.properties["cloudCover"] < cloudcover ]
        if not len(filtered_products) == 0:
            print(f"{len(search_results) - len(filtered_products)} products were filtered out by the property filter.")

        product_ids = [str(res)[13:53] for res in list(filtered_products)]

        if output_stats: 
            stats = landsat_query.analyze_stats(search_results, shape_file)
            return product_ids, stats
        
        return product_ids
            
    
if __name__ == "__main__":

    dag = EODataAccessGateway()
    dag.set_preferred_provider('usgs')

    names = landsat_query.query_landsat_eodag("2023-05-01", "2023-09-01", "shapes/skjern/POLYGON.shp", output_stats = True)

    import pprint

    pprint.pprint(names)


    