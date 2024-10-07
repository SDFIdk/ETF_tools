# function for checking bbox overlap
# function for bandmath with overlap
# json_string_tools class for extracting stuff from strings
# climate_grid_file_tools class for finding strings

# give script some files
# loop over them
# CRS to DMIs
# find corresponging grid_file
# filter all ET parameters from that file
# loop filtered json strings
# extract bbox, check overlap
# if overlap, bandmath window

#in the future the process could be sped up a lot by figureing out which tiles are overlapped to begin with and then presorting the DMI stuff
import glob
import os
import sys
import time

from dmi_tools import DMITools
from et_tools.raster_tools import RasterTools

class ETRasterBuilder:
    """
    Tools for making and localizing ET data

    Parameters:
     - et_files (list): list of geotiffs of evaporative fraction (ETF)
     - output_dir (str path): path to output directory
     - dmi_data_dir (str path): path to directory with DMI climate grid files
     - dmi_param (str, optional): parameter in DMI climate data to apply to ETF data. Defaults to "pot_evaporation_makkink"
     - crs (crs str, optional): crs of output rasters. Defaults to EPSG:4326
    """

    def __init__(self, output_dir, dmi_data_dir, dmi_param = "pot_evaporation_makkink"):

        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok = True)
        self.dmi_data = dmi_data_dir
        self.dmi_param = dmi_param


    def build_dmi_data_raster(self):
        """
        This script converts the DMI climate grid data from txt description to raster
        """

        for i, et_file in enumerate(self.et_files):
            rastertools = RasterTools(et_file, self.output_dir, ext = ['_ETF.tif', '_DMIPET.tif'])

            dmi_file = DMITools.file_from_datetime(DMITools.datetime_from_landsat(et_file), self.dmi_data)
            param_filtered_data = DMITools.get_parameter_specific_data(
                dmi_file, 
                self.dmi_param
            )

            for j, dmi_json in enumerate(param_filtered_data):
                t2 = time.time()
                rastertools.overwrite_geotiff_within_bbox(dmi_json)

                print(f'Raster {i} / {len(self.et_files)}; Tile {j} / {len(param_filtered_data)}, t = {time.time() - t2}', end = '\r')
                # print(f'{i} / {len(overlapping_data)}')

            # rastertools.constrict_dynamic_range((0, 10))
            # rastertools.smooth_nodata_pixels()



if __name__ == '__main__':

    """
    Function takes dmi CSVs and rasterizes them.
    """
    
    dmi_data_dir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_et_files/"

    dmi_raster_output = "test_files/PET/"
    crs = 'EPSG_4329'


    ETRasterBuilder(dmi_raster_output, dmi_data_dir).build_dmi_data_raster()






    

