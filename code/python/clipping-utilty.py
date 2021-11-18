"""
clipping-utility
----------------

Utility to clip data to shape

version 1.0.0
    first version of utility 
"""
import os
import sys
import glob
from datetime import datetime

import yaml
from pandas import read_csv, DataFrame

import tools
import raster

# load config
with open(sys.argv[1], 'r') as fd:
    config = yaml.load(fd, Loader=yaml.Loader)

table = read_csv(config['input-table-file'], index_col=False)
# inputs = table[config['input-column']]

out_dir = config['clipped-directory']
try:
    os.makedirs(out_dir)
except:
    pass

vector = config['vector-file']

def clip_and_check (in_raster, out_raster, vector, sql=None):
    ds = raster.clip_polygon_raster(
        in_raster, out_raster, vector, cutlineSQL = sql,
    )
    if raster.is_bad_data(ds, bad_value = 0):
        ds = None
        os.remove(out_raster)
    return ds

image_map = []

for row_num in table.index:
    row = table.loc[row_num]
    in_raster = row[config['input-column']]

    in_file = os.path.split(in_raster)[1]
    # img_type, date = in_file[:-4].split()
    if 'vector-select-sql' in config:
        for sql_rep in config['vector-select-replacements']:
            entry = row.to_dict()

            
            cl_sql = config['vector-select-sql'].format(**sql_rep)
            name = sql_rep[config['clipped-sub-dir-id']]

            try: 
                os.makedirs( os.path.join(out_dir, 'area-%s' % str(name)) )
            except:
                pass

            out_raster = os.path.join(
                out_dir, 
                'area-%s' % str(name),
                'area-%s-%s' % ( str(name),in_file)
            )
            print(in_raster, out_raster)

            ds = clip_and_check (in_raster,out_raster,vector,cl_sql)

            if ds:
                entry['clipped-area-id'] = sql_rep[config['clipped-sub-dir-id']]
                entry['clipped'] = out_raster
                image_map.append(entry)
                
    else: 
        out_raster = os.path.join(out_dir, 'clipped-%s' % in_file)
        ds = clip_and_check (in_raster,out_raster,vector,None)
        if ds is None:
            entry['clipped-area-id'] = None
            entry['clipped'] = out_raster
            image_map.append(entry)



## save report
print('Complete, saving report as %s' % config['report-file'])
DataFrame(image_map).to_csv(config['report-file'], index=False)
