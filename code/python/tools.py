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
    """get the date from a digital globe path
    
    Parameters
    ----------
    p: path 
        path to a image file with path format from digital globe compressed data
    pf: str
        use '%s'

    
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
    """Calculate the Julida dayys according to the fomula provided by
    DigitalGlobe. Found in section 4.1.2 
    here https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf

    Parameters
    ----------
    tlc_time: datetime.datetime

    Returns
    -------
    int:
        days since the beginning of the year -4712 
        Meuss, Jean. "Astronomical algorithms, 2nd Ed.." Richmond, VA: Willmann-Bell(1998). Pg 61
    """
    a = tlc_time.year // 100 
    b = 2 - a + (a // 4)
    UT = tlc_time.hour + tlc_time.minute/60 + \
        (tlc_time.second+tlc_time.microsecond)/3600
    jd = int(365.25*(tlc_time.year+4716)) + \
        int(30.6001*(tlc_time.month+1)) + \
        tlc_time.day + UT/24+b-1524.5
    return jd

def calc_dist_sun_earth_au(jd):
    """Calculate the earth sun distance in AU. Found in section 4.1.2 
    here https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf

    Parameters
    ----------
    jd: int 
        days in julian days

    Returns
    -------
    float
        earth sun distance  in AU
    """
    d = jd - 2451545.0
    g = 357.529 + 0.98560028 * d
    d_es = 1.00014 - 0.01671 * np.cos( np.radians(g) ) - \
        0.00014 * np.cos( np.radians(2*g) )
    return d_es

