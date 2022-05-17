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
import gc

import yaml
from osgeo import gdal
from pandas import DataFrame, read_csv
import numpy as np

import tools
import raster
import imd_file
import gain, offset 
import irradiance
import satellites
import bands


def process_bands(band_dict, imd_meta, out_dataset, theta):
    for band, num in band_dict.items():
        print(band,num)
        dn = in_dataset.GetRasterBand(num).ReadAsArray()
        shape = (in_dataset.RasterYSize, in_dataset.RasterXSize)
        loop_data = np.memmap('temp-rc-mempap.data', dtype=np.float32, shape=shape, mode='w+')
        # times = timedelta()
        for row in range(shape[0]):
            # start = datetime.now()
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
            # dur = datetime.now() - start
            # times += dur
            # print('row %s' % row, 'time:', dur,  'avg time:', times/(row+1))

            
            gc.collect(1)
            gc.collect(2)
            gc.collect(0)
            
    
        outband = out_dataset.GetRasterBand(num) 
        outband.WriteArray(loop_data)  
        outband.FlushCache()  
        
                



# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)


if config['input-data-source'] == 'digital-globe':
    raw_data_dir = config['input-directory'] if 'input-directory' in config else None
    format = config['input-sub-dir-format']
    swath_dirs = glob.glob(os.path.join(raw_data_dir,format,''))

    swath_dict = {
        tools.digiglobe_find_date('%s/GIS_FILES/*.shp' % p): 
            {"root-path": p} for p in swath_dirs
    }

    for swath, swath_obj in swath_dict.items():
        
        swath_obj['pan-tiffs-raw'] = sorted(glob.glob(
            '%s/[0-9]*/[0-9]*/*_PAN/*.TIF' % swath_obj['root-path']
        ))
        swath_obj['mul-tiffs-raw'] = sorted(glob.glob(
            '%s/[0-9]*/[0-9]*/*_MUL/*.TIF' % swath_obj['root-path']
        ))

elif config['input-data-source'] == 'manual-entry':
    
    

    for img_dict in config['image-data']:
        img_dict['date'] = datetime.strptime(
            img_dict['date'], config['manual-date-in-format']
        )
            

else:
    print ("'input-data-source' error, Only 'digital-globe' source is supported")   
    sys.exit()


## files to skip
try:
    with open(config['ignore-list'], 'r') as fd:
        ignore_list = fd.read().split('\n')
except:
    ignore_list =  []

# Set up output
out_dir = config['output-directory']


image_map = []

# # This could be improved
# config['output-sub-directories'] = 'no' if \
#     config['output-sub-directories'] == False else 'yes'
tif_ext = 'TIF'
imd_ext = 'IMD'
rpb_ext = 'RPB'
att_ext = 'ATT'

# Processing
print ('Starting')
if config['input-data-source'] == 'digital-globe':
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

                with open(tif.replace(tif_ext,imd_ext), 'r') as fd:
                    imd_meta = imd_file.load(fd)

                out_date = tools.digiglobe_find_date(tif)\
                                .strftime('%Y%m%dT%H%M%S')
                out_file = '%s-%s.tif' % (tif_type_short, out_date)
                print('  ',os.path.split(tif)[1], '->', out_file )
                
                out_dir_current = os.path.join(out_dir, out_date)
                try: 
                    os.makedirs(out_dir_current)
                except:
                    pass
                out_path = os.path.join(out_dir_current, out_file)
                if os.path.exists(out_path):
                    print('result file exists skipping!')
                    continue

                exts = [
                    # 'XML', 
                    att_ext,
                    # 'EPH',
                    # 'GEO',
                    imd_ext,
                    rpb_ext,
                    # 'TIL',
                ]
                for ext in exts:
                    in_temp = tif.replace(tif_ext, ext)
                    out_temp = out_path.replace('tif', ext)
                    shutil.copy(in_temp, out_temp)
                
                swath_obj['%s-tiffs-corrected' % tif_type_short].append(out_path)

                tlc_time = datetime.strptime(
                    imd_meta['IMAGE_1']['TLCTime'],
                    '%Y-%m-%dT%H:%M:%S.%f%z'
                )
                print(tlc_time)
                
                jd = tools.calc_julian_days_dg(tlc_time)
                dist_earth_sun = tools.calc_dist_sun_earth_au(jd)
                
                ## see https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf
                theta = 90-float(imd_meta['IMAGE_1']['meanSunEl']) # Function does radian conversion

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
                
                # from datetime import datetime, timedelta
                process_bands(band_dict, imd_meta, out_dataset, theta)
             
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

elif config['input-data-source'] == 'manual-entry':
    for img_dict in config['image-data']:
        print (img_dict['date'])
        if os.path.exists(img_dict['output-path']):
            print('result file exists skipping!')
            continue

        output_directory = os.path.split(img_dict['output-path'])[0]

        try:
            os.makedirs(output_directory)
        except:
            pass

        for mdf in img_dict['metadata-files']:
            ext = os.path.split(mdf)[1].split('.')[1]
            temp = os.path.split(img_dict['output-path'])[1].split('.')[0]
            # print(temp)
            # sys.exit()
            temp = temp + '.' + ext
            shutil.copy(mdf, os.path.join(output_directory, temp))
       
        jd = tools.calc_julian_days_dg(img_dict['date'])
        dist_earth_sun = tools.calc_dist_sun_earth_au(jd)
        # Function does radian conversion
        theta = 90-float(img_dict['sun-angle']) 

        in_dataset = gdal.Open(img_dict['input-path'], gdal.GA_ReadOnly)
        write_driver = gdal.GetDriverByName('GTiff') 
        temp = write_driver.CreateCopy('./temp-rcu.tif', in_dataset, 0)
        if config['calc-reflectance']:
            # print('h')
            gdal.Translate(
                img_dict['output-path'], 
                temp, 
                outputType=gdal.GDT_Float32
            )#, creationOptions=['COMPRESS=LZW',])
        else:
            shutil.copy('./temp-rcu.tif', img_dict['output-path'])
        del(temp)
        os.remove('./temp-rcu.tif')
        out_dataset = gdal.Open(img_dict['output-path'], gdal.GA_Update)


        ## creat 'imd_meta' object
        imd_meta = {}
        for key in img_dict['abs-cal-factor']:
            imd_meta[key] = {
                'absCalFactor': img_dict['abs-cal-factor'][key], 
                'effectiveBandwidth':  img_dict['effective-bandwidth'][key]
            }

        sat_name = satellites.name_lookup[img_dict['satellite']]

        band_dict  = bands.numbers[sat_name]
        if img_dict['type'] == 'pan':
            band_dict = {'pan': 1}
        

        process_bands(band_dict, imd_meta, out_dataset, theta)    
        out_dataset.FlushCache()
        del(out_dataset)
        gc.collect(1)
        gc.collect(2)
        gc.collect(0)




        out_col_name = 'reflectance' if config['calc-reflectance'] \
            else 'radiometric-calibrated'




        image_map.append({ 
            'date': img_dict['date'],
            'type': 'multispectral' if img_dict['type'] == 'mul' else 'panchromatic',
            'original': img_dict['input-path'],
            out_col_name: img_dict['output-path'],
            'satellite': img_dict['satellite'],
            # 'resolution': ps,
        }) 

else: 
    print("invalid 'input-data-source'")

## logging
# with open(config['errors-file'], 'w' ) as fd:
#     for item in unsuccessful:
#         fd.write(str(item) +'\n')

## save report
print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_map).to_csv(config['report-file'], index=False)

