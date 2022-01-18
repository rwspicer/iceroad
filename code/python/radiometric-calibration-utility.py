"""
--------------------


version 1.0.0
    Utility ccalibrates data based on a config file
"""
import os
import sys
import shutil
# from types import coroutine
import glob
from datetime import datetime

import yaml
import gdal
from pandas import DataFrame, read_csv
import numpy as np

import tools
import raster
import imd_file
import gain, offset 
import irradiance
import satellites
import bands
import gc


# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)

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


## files to skip
with open(config['ignore-list'], 'r') as fd:
    ignore_list = fd.read().split('\n')

# Set up output
out_dir = config['output-directory']


image_map = []

# # This could be improved
# config['output-sub-directories'] = 'no' if \
#     config['output-sub-directories'] == False else 'yes'


# Processing
print ('Starting')
for swath, swath_obj in swath_dict.items():
    print (swath.isoformat())
    for tif_type in ['mul-tiffs-raw', 'pan-tiffs-raw']:
        # print(' ', tif_type)
        tif_type_short = tif_type.split('-')[0]
        
        swath_obj['%s-tiffs-corrected' % tif_type_short] = []
        for tif in swath_obj[tif_type]:

            if tif in ignore_list:
                print('File is on ignore list .... skipping')
                continue

            with open(tif.replace('TIF','IMD'), 'r') as fd:
                imd_meta = imd_file.load(fd)

            out_date = tools.digiglobe_find_date(
                tif, '%s'
            ).strftime('%Y%m%dT%H%M%S')
            out_file = '%s-%s.tif' % (tif_type_short, out_date)
            print('  ',os.path.split(tif)[1], '->', out_file )
            
            out_dir_current = os.path.join(out_dir, out_date)
            try: 
                os.makedirs(out_dir_current)
            except:
                pass
            out_path = os.path.join(out_dir_current, out_file)
            if os.path.exists(out_path):
                continue

            exts = [
                # 'XML', 
                'ATT',
                # 'EPH',
                # 'GEO',
                'IMD',
                'RPB',
                # 'TIL',
            ]
            for ext in exts:
                in_temp = tif.replace('TIF', ext)
                out_temp = out_path.replace('tif', ext)
                shutil.copy(in_temp, out_temp)
            
            swath_obj['%s-tiffs-corrected' % tif_type_short].append(out_path)
            
            jd = tools.calc_julian_days_dg(imd_meta['IMAGE_1']['TLCTime'])
            dist_earth_sun = tools.calc_dist_sun_earth_au(jd)
            
        
            theta = np.radians(90-float(imd_meta['IMAGE_1']['meanSunEl']))

            in_dataset = gdal.Open(tif, gdal.GA_ReadOnly)
            write_driver = gdal.GetDriverByName('GTiff') 
            temp = write_driver.CreateCopy('./temp-rcu.tif', in_dataset, 0)
            if config['calc-reflectance']:
                # print('h')
                gdal.Translate(out_path, temp, outputType=gdal.GDT_Float32)#, creationOptions=['COMPRESS=LZW',])
            else:
                shutil.copy('./temp-rcu.tif', out_path)
            del(temp)
            os.remove('./temp-rcu.tif')
            out_dataset = gdal.Open(out_path, gdal.GA_Update)
            
            sat = imd_meta['IMAGE_1']['satId'].replace('"','')
            sat_name = satellites.name_lookup[sat]

            band_dict  = bands.numbers[sat_name]
            if tif_type_short == 'pan':
                band_dict = {'pan': 1}
            
            for band, num in band_dict.items():
                print(band,num)
                dn = in_dataset.GetRasterBand(num).ReadAsArray()
                shape = (in_dataset.RasterYSize, in_dataset.RasterXSize)
                loop_data = np.memmap('temp-rc-mempap.data', dtype=np.float32, shape=shape, mode='w+')
                for row in range(shape[0]):
                    loop_data[row] = raster.absolute_radiometric_calibration(
                        dn[row], 
                        gain.values[sat_name][band], 
                        offset.values[sat_name][band],
                        float(imd_meta[band]['absCalFactor']), 
                        float(imd_meta[band]['effectiveBandwidth'])
                    )
                    if config['calc-reflectance']:
                        loop_data[row] = raster.calc_toa_reflectance(
                            loop_data[row], 
                            dist_earth_sun, 
                            irradiance.thuilier_2003[sat_name][band], 
                            theta
                        )
                    # print(loop_data[row])
                    gc.collect(1)
                    gc.collect(2)
                    gc.collect(0)
                    # radiance = raster.absolute_radiometric_calibration(
                    #     dn, 
                    #     gain.values[sat_name][band], 
                    #     offset.values[sat_name][band],
                    #     float(imd_meta[band]['absCalFactor']), 
                    #     float(imd_meta[band]['effectiveBandwidth'])
                    # )
                    # if config['calc-reflectance']:
                    #     reflectance = raster.calc_toa_reflectance(
                    #         radiance, 
                    #         dist_earth_sun, 
                    #         irradiance.thuilier_2003[sat_name][band], 
                    #         theta
                    #     )
            
                outband = out_dataset.GetRasterBand(num) 
                outband.WriteArray(loop_data)  
                # if config['calc-reflectance']:
                #     outband.WriteArray(reflectance) 
                # else:
                #     outband.WriteArray(radiance) 
                outband.FlushCache()  
                
            out_dataset.FlushCache()
            # print (out_dataset.GetDescription())
            del(out_dataset)
            gc.collect(1)
            gc.collect(2)
            gc.collect(0)

            # ps = gdal.Info(
            #     out_path, options=gdal.InfoOptions(format='json')
            # )['geoTransform'][1]

            out_col_name = 'reflectance' if config['calc-reflectance'] \
                else 'radiometric-calibrated'

            image_map.append({ 
                'date': datetime.strptime(out_date, '%Y%m%dT%H%M%S'),
                'type': 'multispectral' if tif_type_short == 'mul' else 'panchromatic',
                'original': tif,
                'out_col_name': out_path,
                'satellite': sat,
                # 'resolution': ps,
            }) 




## logging
# with open(config['errors-file'], 'w' ) as fd:
#     for item in unsuccessful:
#         fd.write(str(item) +'\n')

## save report
print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_map).to_csv(config['report-file'], index=False)

