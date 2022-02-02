"""
Raster
------

Tools for raster I/o and manipulation

Some code originates from https://github.com/rwspicer/spicebox
which is licensed under the MIT License

"""
from osgeo import gdal
import numpy as np
from numba import njit


def load_raster (filename,  return_dataset = False):
    """Load a raster file and it's metadata

    TAKEN FROM SPICEBOX v0.5.0
    
    Parameters
    ----------
    filename: str
        path to raster file to read
    return_dataset: bool
        if true return gdal.dataset
        
    Returns 
    -------
    gdal.dataset
        or 
    np.array
        2d raster data
    RASTER_METADATA
        metadata on raster file read
    """
    dataset = gdal.Open(filename, gdal.GA_ReadOnly)
    # (X, deltaX, rotation, Y, rotation, deltaY) = dataset.GetGeoTransform()
    if return_dataset:
        return dataset

    metadata = {
        'transform': dataset.GetGeoTransform(),
        'projection': dataset.GetProjection(),
        'x_size': dataset.RasterXSize,
        'y_size': dataset.RasterYSize,
    }

    data = dataset.GetRasterBand(1).ReadAsArray()
    return data, metadata


def clip_polygon_raster (
    in_raster, out_raster, vector, **warp_options
    ):
    """clips raster from shape using gdal warp

    TAKEN FROM SPICEBOX v0.5.0

    Parameters
    ----------
    in_raster: path or gdal.Dataset
        input rater 
    out_raster: path
        file to save clipped data to
    vector: path
        path to vector file with shape to clip to
    warp_options:
        keyword options for gdal warp as formated for gdal.WarpOptions
        see https://gdal.org/python/osgeo.gdal-module.html#WarpOptions
        Default options use 'cropToCutline' = True, 'targetAlignedPixels' = True
        and xRes and yRes from input raster.

    Returns
    -------
    gdal.Dataset
    """
    if type(in_raster) is str:
        in_raster = load_raster(in_raster, True)
    gt = in_raster.GetGeoTransform()
     
    
    options = {
        'xRes': gt[1],'yRes': gt[5],
        'targetAlignedPixels':True,
        'cutlineDSName': vector,
        'cropToCutline':True
    }
    options.update(warp_options)
    
    options = gdal.WarpOptions(**options)
    
    rv = gdal.Warp(out_raster, in_raster, options=options )
    if not rv is None:
        rv.FlushCache()
    return rv


def is_bad_data(dataset, bad_value = np.nan, band = 1):
    """Test if all pixels are bad data

    Parameters
    ----------
    dataset: Gdal.Dataset
        input data.
    bad_value: any, default np.nan
        type of bad_value must be compatible with dataset type
    band: int, default 1
        band of dataset to use for testing.  
    

    Returns
    -------
    bool:
        True if all pixels equal bad_value, else false.
    """
    pixels = dataset.GetRasterBand(band).ReadAsArray()
    if np.isnan(bad_value):
        if np.isnan(pixels).all():
            return True
    else:
        if (pixels == bad_value).all():
            return True
    
    return False


def orthorectify_rpc(input, output, dem, crs):
    """orthorectify raster with RPC information using a dem 

    Parameters
    ----------
    input: path or gdal.Dataset
        in raster
    output: path or gdal.Dataset
        out raster 
    dem: path
        dem raster (this has to be a file path)
    crs: string
        WKT crs 

    Returns
    -------
    gdal.Dataset
    """

    warp_options = gdal.WarpOptions(
        dstSRS = crs, 
        srcNodata = 0, 
        dstNodata=0, 
        rpc=True, 
        transformerOptions='RPC_DEM=%s' % dem
    )  
    return gdal.Warp(output, input, options= warp_options)

@njit(parallel=True)
def absolute_radiometric_calibration(
        data, gain,offset, abs_cal_factor, effective_bandwidth, 
    ):
    """"""
    return gain*data*(abs_cal_factor/effective_bandwidth) + offset

@njit(parallel=True)
def calc_toa_reflectance(radiance, dist_earth_sun, irradiance, theta):
    """
    """
    ref = (radiance * (dist_earth_sun**2) * np.pi)/ (irradiance * np.cos(theta))
    return ref


def calc_norm_index(dataset, band_a_name, band_b_name):
    """
    """
    band_a = dataset.GetRasterBand(band_a_name).ReadAsArray()
    band_b = dataset.GetRasterBand(band_b_name).ReadAsArray()

    return (band_a - band_b) /  (band_b + band_a)


def save_raster(filename, data, transform, projection, 
    datatype = gdal.GDT_Float32):
    """Function Docs 
    Parameters
    ----------
    filename: path
        path to file to save
    data: np.array like
        2D array to save
    transform: tuple
        (origin X, X resolution, 0, origin Y, 0, Y resolution) 
    projection: string
        SRS projection in WTK format
    datatype:
        Gdal data type
    
    """
    write_driver = gdal.GetDriverByName('GTiff') 
    raster = write_driver.Create(
        filename, data.shape[1], data.shape[0], 1, datatype
    )
    raster.SetGeoTransform(transform)  
    outband = raster.GetRasterBand(1)  
    outband.WriteArray(data) 
    raster.SetProjection(projection) 
    outband.FlushCache()  
    raster.FlushCache()  
