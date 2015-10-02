# Rewrite the Node.js package "togeojson" in Python using xml.dom
def get(x, y):
    return x.getElementsByTagName(y)

def attr(x, y):
    return x.getAttribute(y)

def attrf(x, y): 
    return float(attr(x, y))

def get1(x, y):
    """
    Return the first y child of x, if it exists.
    Otherwise return None
    """
    s = get(x, y)
    if s:
        return s[0]
    else:
        return None

def norm(e): 
    e.normalize() 
    return e

def numarray(x):
    """
    Cast array x into numbers
    """
    return [float(xx) for xx in x]

def nodeVal(x):
    if x is None:
        return ''
    else: 
        return norm(x).firstChild.nodeValue
    
# def coord1(v):
#     return numarray(v.replace(removeSpace, '').split(',')) 

# def coord(v):
#     """ 
#     Get one coordinate from a coordinate array, if any
#     get all coordinates from a coordinate array as [[],[]]
#     """
#     coords = v.replace(trimSpace, '').split(splitSpace),
#     o = []
#     for ( i = 0 i < coords.length i++) 
#         o.push(coord1(coords[i]))
    
#     return o

# def coordPair(x):
#      ll = [attrf(x, 'lon'), attrf(x, 'lat')],
#         ele = get1(x, 'ele'),
#         """ handle namespaced attribute in browser
#         heartRate = get1(x, 'gpxtpx:hr') || get1(x, 'hr'),
#         time = get1(x, 'time'),
#         e
#     if (ele) 
#         e = parseFloat(nodeVal(ele))
#         if (!isNaN(e)) 
#             ll.push(e)
        
    
#     return 
#         coordinates: ll,
#         time: time ? nodeVal(time) : null,
#         heartRate: heartRate ? parseFloat(nodeVal(heartRate)) : null
    

