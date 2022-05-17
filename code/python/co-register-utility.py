"""
co-register-utility
--------------------

Utility to co-register image dataf

version 1.0.0
    Utility co-registers data based on a config file
"""
import os
import sys
import shutil
# import glob
# from datetime import datetime

import yaml
# import gdal
from pandas import DataFrame, read_csv
import numpy as np

import tools
# import raster

import coreg 
import gc


# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)


## configure options 
image_table = read_csv(config['input-table-file'], index_col=False)
input_col = config['input-column']


dest_path = config['output-directory']
dest_img_tag = config['output-tag'] if 'output-tag' in config else 'cr'
try:
    os.makedirs(dest_path)
except:
    pass

target_idx = image_table['co-register'] == 'target'
target_images = image_table[target_idx][input_col].tolist()

reference_idx = image_table['co-register'] == 'reference' 
refs = image_table[reference_idx][input_col].tolist()

if len(refs) > 1:
    print('Error: only specify at most 1 reference image')
    sys.exit()

if 'reference-override' in config:
    reference = config['reference-override']
else:
    reference = refs[0] if len(refs) == 1 else target_images[0]

print('Reference Image:', reference)

print('Target images:')
for i in target_images:
    print('\t-', i)


cr_band = config['use-band'] if 'use-band' in config else 'nir1'

window_size =  config['window-size'] if 'window-size' in config else 256
max_shift = config['max-shift'] if 'max-shift' in config else 10
align_grids = config['align_grids'] if 'align_grids' in config else True
max_iter = config['max-iterations'] if 'max-iterations' in config else 1000

print(image_table)
if 'reference-override' in config:
    
    img_type = config['reference-override-type']
    img_sat = config['reference-override-satellite']
else:
    idx = image_table[input_col] == reference
    img_type = image_table['type'][idx].values[0]
    img_sat = image_table['satellite'][idx].values[0]

print(img_sat)
if img_type == 'multispectral':
    target_band = tools.get_band_num(cr_band,  img_sat)
else:
    target_band = 1
## co-register dem 

image_table['co-registered-path'] = np.nan
if config['reference-dem']:
    gc.collect(0),gc.collect(2),gc.collect(2)
    print('Coregistering reference to DEM')
    idx = image_table[input_col] == reference
    dem = config['dem']
    file_name = os.path.split(reference)[1].split('.')[0]
    out_path = os.path.join(dest_path, '%s-%s.tif' % (dest_img_tag, file_name))
    
    gc.collect(0),gc.collect(2),gc.collect(2)

    print(out_path)
    if not os.path.exists(out_path):
        # print('dne')
        crl = coreg.coregister_local(
                dem, reference, out_path, 
                1, target_band,
                ws = window_size, max_shift = max_shift,
                align_grids = align_grids , max_iter = max_iter
        )
    else:
        print ('Outfile file exists, Skipping')
    
    image_table.loc[idx,'co-registered-path'] = out_path
    reference = out_path
    

else:
    try:
        shutil.copy(reference, dest_path)
        reference = os.path.split(reference)[-1]
        reference = os.path.join(dest_path, reference)
    except shutil.SameFileError:
        pass

gc.collect(0),gc.collect(2),gc.collect(2)   
## get band no.      
reference_band = target_band
unsuccessful = set()


## coregister all
for target in target_images:
    print('starting:', target)
    gc.collect(0),gc.collect(2),gc.collect(2)

    idx = image_table[input_col] == target
    img_type = image_table['type'][idx].values[0]
    img_sat = image_table['satellite'][idx].values[0]
    # print(img_sat)
    if img_type == 'multispectral':
        target_band = tools.get_band_num(cr_band,  img_sat)
    else:
        target_band = 1
    print(target_band)

    file_name = os.path.split(target)[1].split('.')[0]
    print('target file: ', target)
    if file_name == os.path.split(reference)[-1].split('.')[0]:
        print ('Target == Reference, skipping...')
        continue
    target_path =  target
    out_path = os.path.join(dest_path, '%s-%s.tif' % (dest_img_tag, file_name))
    print('out file:', out_path)
    if os.path.exists(out_path):
        print('out file exitsts, skipping...')
        image_table.loc[idx,'co-registered-path'] = out_path
        continue
    gc.collect(0),gc.collect(2),gc.collect(2)
    try:
        crl = coreg.coregister_local(
            reference, target_path, out_path, 
            reference_band, target_band, 
            ws = window_size, max_shift = max_shift,
            align_grids = align_grids , max_iter = max_iter
        )
        image_table.loc[idx,'co-registered-path'] = out_path

    except:
        unsuccessful.add(file_name) 
        print('coregister_local function failed:', file_name)
        image_table.loc[idx,'co-registered-path']  = 'ERROR: coregister_local function failed'

        continue
    if not crl.coreg_info[ 'success' ]:
        unsuccessful.add(file_name) 
        image_table.loc[idx,'co-registered-path']  = 'ERROR: coregistration process failed'
        print('coregistration process failed', file_name)
    gc.collect(0),gc.collect(2),gc.collect(2)

## logging
with open(config['errors-file'], 'w' ) as fd:
    for item in unsuccessful:
        fd.write(str(item) +'\n')

## save report
print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_table).to_csv(config['report-file'], index=False)

