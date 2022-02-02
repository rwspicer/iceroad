"""
Index Calculator
----------------


version 1.0.0
    Utility Calculates the NDVI or NDWI for multispectral images
"""
import os
import sys
# import shutil
# from types import coroutine
# import glob
# from datetime import datetime

import yaml
# import gdal
from pandas import DataFrame, read_csv
import numpy as np

# import tools
import raster
# import imd_file
# import gain, offset 
# import irradiance
import satellites
import bands
# import gc


# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)

index_bands = {
    'NDVI': {
        'A': 'nir1', 'B': 'red'
    },
    'NDWI': {
        'A': 'green', 'B': 'nir1'
    }
}

image_table = read_csv(config['input-table-file'], index_col=False)
input_col = config['input-column']
index_name = config['index']

out_dir = config['output-directory']
try:
    os.makedirs(out_dir)
except:
    pass
out_img_tag = config['output-tag'] if 'output-tag' in config else index_name

image_table['%s-path' % index_name] = np.nan
for row_num in image_table.index:
    row = image_table.loc[row_num]
    in_raster = row[config['input-column']]
    print(in_raster)
    sat = satellites.name_lookup[row['satellite']]
    if row['type'] != 'multispectral':
        continue
    try:
        if not os.path.isfile(in_raster):
            continue
    except TypeError:
        pass
    if not type(in_raster) is str:
        continue

    ds = raster.load_raster(in_raster, True)


    a_band =  index_bands[index_name]['A']
    b_band =  index_bands[index_name]['B']

    index = raster.calc_norm_index(
        ds, bands.numbers[sat][a_band], bands.numbers[sat][b_band]
    )
    file_name = os.path.split(in_raster)[1].split('.')[0]
    out_file = os.path.join(out_dir, '%s-%s.tif' % (out_img_tag, file_name))
    # print(index.shape)
    raster.save_raster(
        out_file, index, ds.GetGeoTransform(), ds.GetProjection()
    )

    image_table.loc[row_num,'co-registered-path'] = out_file

print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_table).to_csv(config['report-file'], index=False)
