"""
Bands
-----

Image Band numbers

"""
## Band numbers for multispectral Quickbird data
qb_bands = {
    'red': 3,
    'green': 2,
    'blue': 1,
    'nir1': 4,
}


## Band numbers for multispectral GeoEye data are the same as QuickBird
ge1_bands = qb_bands

## Band numbers for multispectral Worldview 2 data
wv2_bands = {
    'red': 5,
    'green': 3,
    'blue': 2,
    'nir1': 7,
    
    'coastal blue':1,
    'yellow':4,
    'red edge': 6,
    'nir2': 8,
    
}

## Band numbers for multispectral Worldview 3 data are the same as Worldview 2
wv3_bands = wv2_bands

