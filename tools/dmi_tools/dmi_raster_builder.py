import rasterio
from rasterio import features
from shapely.geometry import Polygon
import numpy as np
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from shapely.ops import unary_union
import os
import glob
import sys

from dmi_tools import DMITools


import rasterio
from rasterio import features
from shapely.geometry import Polygon
import numpy as np
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from shapely.ops import unary_union

def bboxes_to_raster(bbox_value_list, pixel_size=0.0001, nodata_value=0, output_file=None):
    """
    Converts a list of bounding boxes (as lists of coordinate pairs) and associated values
    into a raster with EPSG:4326.

    Parameters:
    - bbox_value_list: List of tuples [(bbox, value), ...] where bbox is a list of rings,
      and each ring is a list of coordinate pairs [[x, y], [x, y], ...].
    - pixel_size: Resolution of the raster in degrees (default: 0.0001)
    - nodata_value: Value for pixels not covered by any bbox (default: 0)
    - output_file: Optional. If provided, the raster will be saved to this file.

    Returns:
    - raster_data: Numpy array of the rasterized data (if output_file is None)
    - transform: Affine transform for the raster data
    """

    polygons = []
    values = []

    for bbox, value in bbox_value_list:
        outer_ring = bbox[0]
        polygon = Polygon(outer_ring)
        polygons.append(polygon)
        values.append(value)

    all_polygons = unary_union(polygons)
    minx, miny, maxx, maxy = all_polygons.bounds

    width = int(np.ceil((maxx - minx) / pixel_size))
    height = int(np.ceil((maxy - miny) / pixel_size))

    maxx = minx + width * pixel_size
    maxy = miny + height * pixel_size

    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    shapes = ((geom, val) for geom, val in zip(polygons, values))

    raster_data = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        fill=nodata_value,
        transform=transform,
        dtype=np.float32,
        all_touched=False
    )

    if output_file is not None:
        with rasterio.open(
            output_file,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=raster_data.dtype,
            crs=CRS.from_epsg(4326),
            transform=transform,
            nodata=nodata_value
        ) as dst:
            dst.write(raster_data, 1)
    else:
        return raster_data, transform



if __name__ == '__main__':

    dmi_data_dir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_et_files/"
    # dmi_raster_dir = "J:/javej//drought/drought_et/dmi_PET_raster/"
    dmi_param = "pot_evaporation_makkink"
    dmi_raster_output = 'dmi_rasters/pet/'

    localized_output = "test_files/localized/"
    crs = 'EPSG_4329'

    print(os.environ.get('PROJ_DATA'))
    # print(os.environ.get())
    sys.exit()

    for dmi_file in glob.glob(dmi_data_dir + '*.txt'):

        dmi_jsons = DMITools.get_all_data(dmi_file, dmi_param)
        dmi_data = DMITools.convert_jsons_to_bbox_val(dmi_jsons)

        dmi_raster_output = os.path.join(dmi_raster_output, os.path.basename(dmi_file))
        bboxes_to_raster(dmi_data, output_file = dmi_raster_output)

        # bboxes_to_raster(bbox_value_list, pixel_size=0.0001, nodata_value=0, output_file=None)

        sys.exit()






    

