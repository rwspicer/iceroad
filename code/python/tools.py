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


# def find(name, paths = ortho_paths):
#     for path in ortho_paths:
#         if name in path:
#             return path
#     return None

def get_band_num(color, img_type):
    print(img_type)
    if img_type in ['qb', 'ge1', "QB02", '"QB02"', '"GE01"']:
        return bands.qb_bands[color]
    else: #wv2 #wv3
        return bands.wv2_bands[color]
