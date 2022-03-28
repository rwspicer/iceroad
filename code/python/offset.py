

# offset value look up for radiometric calibration
# source: https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf
values = {
    'worldview-3': {
        'pan':      -3.629,
        'coastal':   -8.604,
        'blue':     -5.809,
        'green':    -4.996,
        'yellow':   -3.649,
        'red':      -3.021,
        'rededge':  -4.521,
        'nir1':     -5.522,
        'nir2':     -2.992,
        'swir1':    -5.546,
        'swir2':    -2.600,
        'swir3':    -2.309,
        'swir4':    -1.676,
        'swir5':    -0.705,
        'swir6':    -0.669,
        'swir7':    -0.512,
        'swir8':    -0.372,
    },
        'worldview-2': {
        'pan':      -2.704,
        'coastal':   -7.478,
        'blue':     -5.736,
        'green':    -3.546,
        'yellow':   -3.564,
        'red':      -2.512,
        'rededge':  -4.120,
        'nir1':     -3.300,
        'nir2':     -2.891,
    },
    'geoeye-1': {
        'pan':      -1.926, 
        'blue':     -4.537, 
        'green':    -4.175, 
        'red':      -3.754, 
        'nir1':     -3.87,
    },
    'quickbird': {
        'pan':      -1.491, 
        'blue':     -2.820, 
        'green':    -3.338, 
        'red':      -2.954, 
        'nir1':     -4.722,
    },
    'worldview-1': {
        'pan':      -1.824,
    }, 
    'ikonos': {
        'pan':      -4.461, 
        'blue':     -9.699, 
        'green':    -7.937, 
        'red':      -4.767, 
        'nir1':     -8.869,
    },
}
