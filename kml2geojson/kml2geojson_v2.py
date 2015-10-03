import re

# Atomic KML geometry types supported.
# MultiGeometry is handled separately.
GEOTYPES = [
  'Polygon', 
  'LineString', 
  'Point', 
  'Track', 
  'gx:Track',
  ]

SPACE = re.compile(r'\s+')
# TRIM_SPACE = re.compile(r'^\s*|\s*$')

# ----------------
# Helper functions
# ----------------
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
    
def coord1(v):
    """
    Convert a KML string containing one coordinate into a list.

    EXAMPLE::

        >>> coord1(' -112.2,36.0,2357 ')
        [-112.2, 36.0, 2357]
    """
    return numarray(re.sub(SPACE, '', v).split(',')) 

def coords(v):
    """ 
    Convert a KML string containing multiple coordinates into
    a list of lists.

    EXAMPLE::

        >>> coords('''
         -112.0,36.1,0
         -113.0,36.0,0 
         ''')
        [[-112.0, 36.1, 0], [-113.0, 36.0, 0]]
    """
    w = v.split() #sub(TRIM_SPACE, '', v).split()
    return [coord1(ww) for ww in w]
     
def build_rgb_and_opacity(kml_color_str):
    """
    Given a KML color string, return an equivalent
    RGB hex color string and an opacity float 
    rounded to 2 decimal places.
    
    EXAMPLE::

        >>> build_rgb_and_opacity('ee001122')
        ('#221100', 0.93)

    """
    color = kml_color_str
    opacity = 1

    if color[0] == '#':
        color = color[1:]
    if len(color) == 8:
        opacity = round(int(color[0:2], 16)/256, 2)
        color = color[6:8] + color[4:6] + color[2:4]
    elif len(color) == 6:
        color = color[4:6] + color[2:4] + color[0:2]        
    elif len(color) == 3:
        color = reversed(color)
    else:
        color = '000000'
    color = '#' + color    
    return color, opacity

def gxCoord(v):
    return numarray(v.split(' '))

def gxCoords(root):
    elems = get(root, 'coord', 'gx')
    coordinates = []
    times = []
    if not len(elems): 
        elems = get(root, 'gx:coord')
    coordinates = [gxCoord(nodeVal(e)) for e in elems]
    timeElems = get(root, 'when')
    times = [nodeVal(t) for t in timeElems]
    return {
      'coords': coordinates,
      'times': times,
      }

# --------------
# Main functions 
# --------------
def getGeometry(root):
    """
    """
    geoms = []
    coordTimes = []
    if get1(root, 'MultiGeometry'):  
        return getGeometry(get1(root, 'MultiGeometry')) 
    if get1(root, 'MultiTrack'):
        return getGeometry(get1(root, 'MultiTrack')) 
    if get1(root, 'gx:MultiTrack'):
        return getGeometry(get1(root, 'gx:MultiTrack')) 
    for geoType in GEOTYPES: 
        geoNodes = get(root, geoType)
        if geoNodes: 
            for geoNode in geoNodes:
                if geoType == 'Point': 
                    geoms.append({
                      'type': 'Point',
                      'coordinates': coord1(nodeVal(get1(
                        geoNode, 'coordinates')))
                      })
                elif geoType == 'LineString':
                    geoms.append({
                      'type': 'LineString',
                      'coordinates': coords(nodeVal(get1(
                        geoNode, 'coordinates')))
                      })
                elif geoType == 'Polygon':
                    rings = get(geoNode, 'LinearRing')
                    coords = [coords(nodeVal(get1(ring, 'coordinates')))
                      for ring in rings]
                    geoms.append({
                      'type': 'Polygon',
                      'coordinates': coords,
                      })
                elif geoType in ['Track', 'gx:Track']: 
                    track = gxCoords(geoNode)
                    geoms.append({
                      'type': 'LineString',
                      'coordinates': track.coords,
                      })
                    if track.times:
                        coordTimes.append(track.times)
                
    return {'geoms': geoms, 'coordTimes': coordTimes}
    
def getPlacemark(root):
    """
    """
    geomsAndTimes = getGeometry(root)
    properties = {}
    name = nodeVal(get1(root, 'name'))
    styleUrl = nodeVal(get1(root, 'styleUrl'))
    description = nodeVal(get1(root, 'description'))
    timeSpan = get1(root, 'TimeSpan')
    extendedData = get1(root, 'ExtendedData')
    lineStyle = get1(root, 'LineStyle')
    polyStyle = get1(root, 'PolyStyle')

    if not geomsAndTimes['geoms']:
        return []
    if name:
        properties['name'] = name
    if styleUrl : 
        if styleUrl[0] != '#': 
            styleUrl = '#' + styleUrl
        properties['styleId'] = styleUrl
    if description: 
        properties['description'] = description
    if timeSpan: 
        begin = nodeVal(get1(timeSpan, 'begin'))
        end = nodeVal(get1(timeSpan, 'end'))
        properties['timespan'] = {'begin': begin, 'end': end}
    if lineStyle:
        color, opacity = build_rgb_and_opacity(nodeVal(get1(
          lineStyle, 'color')))
        width = float(nodeVal(get1(lineStyle, 'width')))
        properties['color'] = color
        properties['opacity'] = opacity
        if width is not None:
            properties['weight'] = width 
    if polyStyle:
        color, opacity = build_rgb_and_opacity(nodeVal(get1(
          polyStyle, 'color'))),
        fill = nodeVal(get1(polyStyle, 'fill'))
        outline = nodeVal(get1(polyStyle, 'outline'))
        properties['fillColor'] = color
        properties['opacity'] = opacity
        if fill: 
            properties['fillOpacity'] = fill 
        if outline: 
            properties['weight'] = outline
    if extendedData:
        datas = get(extendedData, 'Data'),
        simpleDatas = get(extendedData, 'SimpleData')
        for data in datas:
            properties[data.getAttribute('name')] = nodeVal(get1(
              data, 'value'))
        for simpleData in simpleDatas:
            properties[simpleData.getAttribute('name')] = nodeVal(simpleData) 
    if geomsAndTimes['coordTimes']:
        ct = geomsAndTimes['coordTimes']
        if len(ct) == 1:
            properties['coordTimes'] = ct[0]
        else:
            properties['coordTimes'] = ct
    
    feature = {
      'type': 'Feature',
      'properties': properties,
      }
    geoms = geomsAndTimes['geoms']
    if len(geoms) == 1:
        feature['geometry'] = geoms[0]
    else:
        feature['geometry'] = {
          'type': 'GeometryCollection',
          'geometries': geoms,
          }
    
    if attr(root, 'id'):
        feature['id'] = attr(root, 'id')

    return [feature]      

def create_feature_collection():
    """
    Create an empty feature collection.
    """
    return {
      'type': 'FeatureCollection',
      'features': []
      }

def build_geojson(kml_obj):
    root = kml_obj
    geojson = create_feature_collection()
    placemarks = get(root, 'Placemark')
    styles = get(root, 'Style')
    styleMaps = get(root, 'StyleMap')

    for placemark in placemarks:
        geojson['features'].extend(getPlacemark(placemark))

    return geojson   