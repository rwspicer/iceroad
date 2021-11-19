"""
tools
-----

general utility functions
"""

from datetime import datetime
from glob import glob
import os
import bands

def digiglobe_find_date (p, pf):
    """get the data from a digital globe path
    
    Parameters
    ----------
    
    """
    return datetime.strptime(
        '20' + os.path.split(glob(pf % p)[0])[1].split('-')[0],
        '%Y%b%d%H%M%S'
    )

def get_band_num(color, satellite):
    """Get the image band # from the color and satellite

    Parameters
    ----------
    color: string
        color band name i.e. red, green, nir1
    satellite: string
        code for satellite (supports quickbird, geoeye 1 and worldview 2/3)

    Returns
    -------
    int 
        the band number 1 - N
    """
    print(satellite)
    if satellite in ['qb', 'ge1', "QB02", '"QB02"', '"GE01"']:
        return bands.qb_bands[color]
    else: #wv2 #wv3
        return bands.wv2_bands[color]
