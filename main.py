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
import shutil
import rasterio as rio
import sys
import time

from tools.dmi_data_parser.dmi_tools import DMITools
from tools.et_adjustment.raster_tools import RasterTools

class ETAdjuster():
    """
    This script uses ETF rasters and local Danish PET climate data
    from the DMI climate grid to produce locally adjusted ET data

    Parameters:
     - et_files (list): list of geotiffs of evaporative fraction (ETF)
     - output_dir (str path): path to output directory
     - dmi_data_dir (str path): path to directory with DMI climate grid files
     - dmi_param (str, optional): parameter in DMI climate data to apply to ETF data. Defaults to "pot_evaporation_makkink"
     - crs (crs str, optional): crs of output rasters. Defaults to EPSG:4326
    """
    def __init__(self, et_files, output_dir, dmi_data_dir, dmi_param = "pot_evaporation_makkink", crs = 'EPSG:4326'):
        if type(et_files) == list:
            self.et_files = et_files
        elif type(et_files) == str:
            self.et_files = glob.glob(et_files + '/*/*._EFT.tif')

        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok = True)
        self.dmi_data = dmi_data_dir
        self.dmi_param = dmi_param
        self.crs = crs


    def run(self):
        for i, et_file in enumerate(self.et_files):
            rastertools = RasterTools(et_file, self.output_dir)
            t = time.time()

            dmi_file = DMITools.file_from_datetime(DMITools.datetime_from_landsat(et_file), self.dmi_data)
            overlapping_data = DMITools.get_overlapping_data(
                dmi_file, 
                et_file, 
                self.dmi_param
                )

            for j, overlap_line in enumerate(overlapping_data):
                t2 = time.time()
                rastertools.process_geotiff_within_bbox(overlap_line)

                # print(f'Raster {i} / {len(self.et_files)}; Tile {j} / {len(overlapping_data)}, t = {time.time() - t2}', end = '\r')
                # print(f'{i} / {len(overlapping_data)}')

            rastertools.constrict_dynamic_range((0, 10))
            rastertools.smooth_nodata_pixels()


if __name__ == '__main__':
    
    et_dirs = [
        'J:/javej/drought/drought_et/SSEB_files/095040',
        'J:/javej/drought/drought_et/SSEB_files/soroe',
        'J:/javej/drought/drought_et/SSEB_files/095218',
        'J:/javej/drought/drought_et/SSEB_files/095116'
    ]

    dmi_data_dir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_et_files/"
    output_base_dir = "J:/javej//drought/drought_et/adjusted_SSEB/"
    crs = 'EPSG_4329'

    for et_dir in et_dirs:
        et_files = glob.glob(et_dir + '/**/*_ETF.tif')
        output_dir = os.path.join(output_base_dir, os.path.basename(et_dir))

        ETAdjuster(et_files, output_dir, dmi_data_dir).run()




    # et_dir ='J:/javej/drought/drought_et/SSEB_files/soroe'
    # et_files = glob.glob(et_dir + '/**/*_ETF.tif')

    # dmi_data_dir = "J:/javej/drought/drought_et/dmi_climate_grid/sorted_et_files/"

    # ETAdjuster(et_files, output_dir, dmi_data_dir).run()









    

