import os
import glob
import sys

class USGSTools:
    """
    Tools for handling files from the USGS ESPA service
    """

    def get_et_ref_files(product_dir):
        """
        Takes a directory path containing other directories
        of individual SSEB-ET files from USGS ESPA
        """
        etf_files = []
        products = glob.glob(product_dir + '/*/')
        for product in products:
            etf_files.append(glob.glob(product + '*_ETF.tif')[0])
        return etf_files


if __name__ == '__main__':
    usgs_dir = 'J:/javej/drought/SSEB_files/095040'
    print(USGSTools.get_et_ref_files(usgs_dir))