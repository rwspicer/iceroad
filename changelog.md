# CHANEGLOG

## [0.6.0] - 2022-05-17
### adds
- orthorectifcation utility can read input data from csv output by
maunal input correction now

### chnages
- order of operations in manual input method to regenerate metadata files 
if needed when out tiffs exist

### fixes
- fixes bug where metadata files are not renamed when copying in manual input
radio corection utility

## [0.5.2] - 2022-04-20
### fixed
- bug in saving dates

## [0.5.1] - 2022-04-15
### fixed
-  fixes'_' that should have been '-' in code

## [0.5.0] - 2022-04-15
### added
- manual inputs methods for radiometric calibration 

### changed
- moved all radian conversion to functions
- updates readme

## [0.4.2] - 2022-03-29
### added
- License
- Installation instructions 

## [0.4.1] - 2022-03-29
### fixed  
- spelling of coastal in radiometric-calibration-utility.py
- gdal imports

## [0.4.0] - 2022-03-28
### added
- clamping of reflectance values for index calculations
- tools for calculation stats on a raster

### fixed
- bug in julian calculation caused by missing brackets
- bug in earth sun distance calculation caused by using degrees instead
of radians in np.cos() calls
- spelling of coastal in lookup table python files

## [0.2.0] - 2022-02-15
### Added
- Added changelog and versioning info
- Added additional example files
example-calibration-config-manual-input.yml
### Changed
- names of example files
- updated readme to reflect added utilities
- added/updated various code documentation 

### Fixed 
- name of index-calculator-utility.py

## [0.1.0]
Initial version





