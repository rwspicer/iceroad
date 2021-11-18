"""
at_file
-------

tools for digital globe attribute file

"""


def loads(text):
    """Load digital globe attributes text

    Parameters
    ----------
    text: string

    Returns
    -------
    dict
    """

    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    
    att_dict = {}
    lidx = -1
    while True:
        lidx += 1 
        line = lines[lidx]
        # print(line)
        if 'END;' == line:
            break
        if '=' in line:
            key, value = [i.strip() for i in line.split('=')]
            att_dict[key] = value[:-1] if ';' in value else value
            last_key = key
            continue

        
        if last_key == 'attList':
            if att_dict['attList'] == '(':
                att_dict['attList'] = []

            line = line[:-1] if ';' in line else line
            line = line[1:-2] # remove '(' and ')'
            items = [float(i) for i in line.split(',')]
            items[0] = int(items[0])

            att_dict['attList'].append(items)
            continue

    return att_dict


def load(fd):
    """Load digital globe attributes file
    Parameters
    ----------
    fd: filed escriptor

    Returns
    -------
    dict
    
    """
    return loads(fd.read())
