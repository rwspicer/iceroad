"""
orthorectify-utility
--------------------

Utility to orthorectify raster data, see readme for documentation

version 1.0.0
    Utility can orthorectify data from digital-globe
"""
import os
import sys
import glob
from datetime import datetime

import yaml
import gdal
from pandas import DataFrame

import tools
import raster
import att_file

# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)

## set up input
raw_data_dir = config['input-directory']
format = config['input-sub-dir-format']
if config['input-data-source'] == 'digital-globe':
    swath_dirs = glob.glob(os.path.join(raw_data_dir,format,''))

    swath_dict = {
        tools.digiglobe_find_date(p, '%s/GIS_FILES/*.shp'): 
            {"root-path": p} for p in swath_dirs
    }

    for swath, swath_obj in swath_dict.items():
        
        swath_obj['pan-tiffs-raw'] = sorted(glob.glob(
            '%s/[0-9]*/[0-9]*/*_PAN/*.TIF' % swath_obj['root-path']
        ))
        swath_obj['mul-tiffs-raw'] = sorted(glob.glob(
            '%s/[0-9]*/[0-9]*/*_MUL/*.TIF' % swath_obj['root-path']
        ))

else:
    print ("'input-data-source' error, Only 'digital-globe' source is supported")   
    sys.exit()

## DEM set up
dem = config['dem']
out_crs = config['crs']
if out_crs.upper() == 'DEM_CRS':
    out_crs = gdal.Info(
        dem, options=gdal.InfoOptions(format='json')
    )['coordinateSystem']['wkt']


# Set up output
out_dir= config['orthorectified-directory']

try:
    os.makedirs(out_dir)
except:
    pass

image_map = []

# This could be improved
config['output-sub-directories'] = 'no' if \
    config['output-sub-directories'] == False else 'yes'


# Processing
print ('Starting')
for swath, swath_obj in swath_dict.items():
    print (swath.isoformat())
    for tif_type in ['mul-tiffs-raw', 'pan-tiffs-raw']:
        # print(' ', tif_type)
        tif_type_short = tif_type.split('-')[0]
        
        swath_obj['%s-tiffs-corrected' % tif_type_short] = []
        for tif in swath_obj[tif_type]:
            with open(tif.replace('TIF','ATT'), 'r') as fd:
                att = att_file.load(fd)



            
            out_date = tools.digiglobe_find_date(
                tif, '%s'
            ).strftime('%Y%m%dT%H%M%S')
            out_file = '%s-%s.tif' % (tif_type_short, out_date)
            print('  ',os.path.split(tif)[1], '->', out_file )
            if config['output-sub-directories'].lower() == 'no':
                # print('no')
                out_path = os.path.join(out_dir, out_file)
            else:
                # print('yes')
                try: 
                    os.makedirs(os.path.join(out_dir, out_date))
                except:
                    pass
                out_path = os.path.join(out_dir, out_date, out_file)
            swath_obj['%s-tiffs-corrected' % tif_type_short].append(out_path)
            
            
            raster.orthorectify_rpc(tif, out_path, dem, out_crs)

            ps = gdal.Info(
                out_path, options=gdal.InfoOptions(format='json')
            )['geoTransform'][1]

            image_map.append({ 
                'date': datetime.strptime(out_date, '%Y%m%dT%H%M%S'),
                'type': 'multispectral' if tif_type_short == 'mul' else 'panchromatic',
                'original': tif,
                'orthorectified':out_path,
                'satellite': att['satId'],
                'resolution': ps,
            }) 
            

## save report
print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_map).to_csv(config['report-file'], index=False)
