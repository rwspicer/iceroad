


def loads(text):
    
    band_table = {
        "BAND_B": 'blue',
        "BAND_G": 'green',
        "BAND_R": 'red',
        "BAND_N": 'nir1',
        'BAND_C': 'coastal',
        'BAND_Y': 'yellow',
        'BAND_RE': 'rededge',
        'BAND_N2': 'nir2',
        'BAND_P': 'pan'
    }
    
    lines = text.split('\n')
#     return lines
    imd = {}
    group = imd
    line_no = 0
    while True:
        line = lines[line_no]
#         print(line)
        if line == 'END;':
            break
            
        if 'TLCList' in line:
            t = '('
            while True:
                line_no +=1
                line = lines[line_no]
                t += line
                if ';' in line:
                    break
            group['TLCList']= t
            line_no +=1
            continue
                
                
            
        
        key, value = [l.strip() for l in line.split('=')]
        value = value[:-1] if ';' == value[-1] else value
        if 'BEGIN_GROUP' in line:
            group = {}
            line_no+=1
            continue
        if 'END_GROUP' in line:
#             print(value)
            if value in band_table:
                value = band_table[value]
            imd[value] = group 
            group = imd
            line_no+=1
            continue
        
        group[key] = value.strip()
        line_no+=1
    return imd


def load(fd):
    """Load digital globe imd file
    Parameters
    ----------
    fd: filed escriptor

    Returns
    -------
    dict
    
    """
    return loads(fd.read())
