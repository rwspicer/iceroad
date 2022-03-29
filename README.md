# ice-road-project

Code and docs for the Ice Road project.

## Installtion instruuctions

Install packages in `reqirements.txt` 

I would reccomend doing this within an environment using the [conda package manager](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html):

`conda create -c conda-forge --name iceroad arosics gdal pandas numpy numba pyyaml` 


## Image Processing

Satellite images were processed according the following steps:

1. Conversion to top-of-atmosphere reflectance
2. Orthorectification
3. Clipping
4. Co-registration 
5. Calculating NDVI and NDWI

## Radiometric Calibration

Use `code/python/radiometric-calibration-utility.py` to preform absolute
radiometric calibration and conversion to top-of-atmosphere(TOA)  reflectance.

This utility supports input data in the format provided by Maxar/DigitalGlobe. The process used is described in the document [here](https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf). Further calibration values used were found [here](https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf).


The utility reads a config YAML file that contains the path to the input data, 
output directory, wether or not to calculate TOA reflectance and other settings. 
`example-calibration-config.yml` contains all settings and options that
can be used in this utility.

Run as:

    python code/python/radiometric-calibration-utility.py config.yml

## Orthorectification

Use `code/python/orthorectify-utility.py` This utility uses GDAL warp to 
orthorectify image data.

Inputs may either be raw data in the format provided by Maxar/DigitalGlobe, or reflectance outputs from `radiometric-calibration-utility.py` (**preferred**).
The utility requires a config YAML file the input/output directories, a path to 
the DEM, and the input format to operate. `example-orthorectification-config.yml`
contains all settings and options that can be used in this utility.

Run as:

    python code/python/orthorectify-utility.py config.yml

## Clipping

Use `code/python/clipping-utility.py` Takes output from orthorectification and 
clip data to areas of interest provided in a vector file. Process uses GDAL 
warp. 

Utility needs a config YAML file that contains the path to a csv file (as output
from `orthorectify-utility.py`), and a path to vector file along with various
other settings to preform the the clipping. `clipping-config-example.yml` 
describes all settings that may be used.

Run as: 

    python code/python/clipping-utility.py config.yml

## Co-registration

Use `code/python/co-register-utility.py`. To co-register data output from `clipping-utility.py`.  

Add a column to the report file provided by `clipping-utility.py` called 
`co-register` assign one row as the `reference` image, and other rows as 
`target`. Leave rows in this column blank to skip. See `example-co-register-in.csv` 
for an example of how this should look.

The utility takes a config YAML file with the input CSV file, output 
directory and other settings to operate. `co-registration-config-example.yml` describes describes all settings that may be used.

Run as: 

    python code/python/co-register-utility.py config.yml

## NDVI and NDWI

These indexes are calculated with `code/python/index-calculator-utility.py`

The utility takes a config YAML file which contains an input CSV file, output 
directory, Index to calculate and other settings to operate. 
`example-index-calculator-config.yml` contains and describes all possible 
options this utility may use.

Run as: 

    python code/python/index-calculator-utility.py config.yml
