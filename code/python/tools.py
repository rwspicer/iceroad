"""
tools
-----

general utility functions
"""

from datetime import datetime
from glob import glob
import os
import bands
import satellites
import numpy as np

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
    name = satellites.name_lookup[satellite]
    return bands.numbers[name][color]
    # if satellite in ['qb', 'ge1', "QB02", '"QB02"', '"GE01"']:
    #     return bands.qb_bands[color]
    # else: #wv2 #wv3
    #     return bands.wv2_bands[color]


def calc_julian_days_dg(tlc_time):
    tlc_time = datetime.strptime(
        tlc_time,
        '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    print(tlc_time)
    a = tlc_time.year//100 
    b = 2 - a + a // 4
    UT = tlc_time.hour + tlc_time.minute/60 + (tlc_time.second+tlc_time.microsecond)/3600
    jd = int(365.25*tlc_time.year+4716) + \
        int(30.6001*(tlc_time.month+1)) + \
        tlc_time.day + UT/24+b-1524.5
    return jd

def calc_dist_sun_earth_au(jd):
    d = jd - 2451545.0
    g = 357.529 + 0.98560028 * d
    d_es = 1.00014 - 0.01671 * np.cos(g) - 0.00014*np.cos(2*g)
    return d_es

