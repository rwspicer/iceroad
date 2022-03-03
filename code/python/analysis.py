"""
Analysis
--------

Tools for analysis of satellite data
"""
from pandas import DataFrame
import numpy as np

def area_average (area):
    """Calculate the average pixel value

    Parameters
    ----------
    area: np.array
        area to calualte mean for
    
    Returns
    -------
    mean
    """
    return np.nanmean(area)

def area_stats (area):
    """Get common statistics as a dict

    Parameters
    ----------
    area: np.array
        area to calualte mean for
    
    Returns
    -------
    dict 
        statistics
    """
    return DataFrame(area.flatten()).describe().to_dict()

def area_average_timeseries(data, dates, mean_col_name='mean'):
    """

    Parameters
    ----------
    data: list of np.array
        list of images to calc average for
    dates: list of dates
        dates corresponding to images in data
    mean_col_name: string
        name of column for means

    Returns
    -------
    DataFrame
    """
    means = []
    for area in data:
        means.append(area_average(area))
    
    table = {
        'date': dates,
        mean_col_name: means,
    }
    return DataFrame(table)


def apply_threshold(img, threshold):
    """
    apply a threshold to an image ingnoring nan data

    Parameters
    ----------
    img: np.array
        image data
    threshold: Number
        the threshold
    
    Returns
    -------
    np.array
        thresholded image
    """
    result = (img > threshold).astype(float)

    result[np.isnan(img)] = np.nan
    return result

def calc_area_included(area):
    """
    Calculates percentage of pixels that are above threshold

    Parameters
    ----------
    area: np.array
        threshold image
    
    Returns
    -------
    float:
        percentage of area above threshold
    """
    # threshold area / 9total area - masked area)
    return len(area[area>0]) / (len(area.flatten()) - len(np.isnan(area)))
