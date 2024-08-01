from cdsetool.query import query_features, shape_to_wkt
import geopandas as gpd
import sys
from eodag import EODataAccessGateway
import geopandas as gpd

class landsat_query:

    def get_bbox_list(shapefile):
        aoi = gpd.read_file(shapefile)
        return aoi.total_bounds.tolist()

    def query_landsat_cdse(start_date, end_date, geometry):

        features = query_features(
            "Landsat8",
            {
                "startDate": start_date,
                "completionDate": end_date,
                "geometry": shape_to_wkt(geometry),
                # "productType": "L1TP"
            },
        )

        product_names = []
        for f in features:

            product = f.get('properties').get('productIdentifier')
            product_names.append(product.split('/')[-1])

        return product_names
    

    def query_landsat_eodag(start_date, end_date, shape_file, product_type = 'LANDSAT_C2L2'):

        dag = EODataAccessGateway()
        dag.set_preferred_provider("usgs")

        search_criteria = {
            'productType': product_type,
            'start': start_date,
            'end': end_date,
            'geom': landsat_query.get_bbox_list(shape_file),
        }

        results = dag.search_all(**search_criteria)

        return [str(res)[13:53] for res in list(results)]


    
if __name__ == "__main__":

    dag = EODataAccessGateway()
    dag.set_preferred_provider('usgs')

    names = landsat_query.query_landsat_eodag("2023-05-01", "2023-09-01", "skjern/POLYGON.shp")

    import pprint

    pprint.pprint(names)


    