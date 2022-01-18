"""
Bands
-----

Image Band numbers

"""
## Band number look up
numbers = {
    'worldview-3':{
        'red': 5,
        'green': 3,
        'blue': 2,
        'nir1': 7,
        'costal':1, ## TODO fix spelling
        'yellow':4,
        'rededge': 6,
        'nir2': 8,
    },
    'geoeye-1': {
        'red': 3,
        'green': 2,
        'blue': 1,
        'nir1': 4,
    },
    'worldview-1':{'pan':1}
}

numbers['worldview-2'] = numbers['worldview-3']
numbers['quickbird'] = numbers['geoeye-1']
