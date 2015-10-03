import re
import xml.dom.minidom as md
import pathlib
import json

import click

# TODO: Change from camel case names to underscore names.

# Atomic KML geometry types supported.
# MultiGeometry is handled separately.
GEOTYPES = [
  'Polygon', 
  'LineString', 
  'Point', 
  'Track', 
  'gx:Track',
  ]

# Acceptable types of style dictionaries supported
STYLE_TYPES = [
  'leaflet',
  ]

SPACE = re.compile(r'\s+')

# ----------------
# Helper functions
# ----------------
def get(node, name):
    return node.getElementsByTagName(name)

def get1(node, name):
    """
    Return the first element of ``get(node, name)``, if it exists.
    Otherwise return ``None``.
    """
    s = get(node, name)
    if s:
        return s[0]
    else:
        return None

def attr(node, name):
    """
    Return the value of the attribute named by ``name`` as a string,
    if it exists.
    Otherwise, return an empty string.
    """
    return node.getAttribute(name)

def val(node):
    if node is not None:
        node.normalize()
        return node.firstChild.nodeValue
    else: 
        return ''

def valf(node):
    try:
        return float(val(node))
    except ValueError:
        return None
    
def numarray(a):
    """
    Cast the given list into floats.
    """
    return [float(aa) for aa in a]

def coord1(s):
    """
    Convert a KML string containing one coordinate into a list.

    EXAMPLE::

        >>> coord1(' -112.2,36.0,2357 ')
        [-112.2, 36.0, 2357]
    """
    return numarray(re.sub(SPACE, '', s).split(',')) 

def coords(s):
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
    s = s.split() #sub(TRIM_SPACE, '', v).split()
    return [coord1(ss) for ss in s]
     
def gx_coord(s):
    return numarray(s.split(' '))

def gx_coords(node):
    els = get(node, 'gx:coord')
    coordinates = []
    times = []
    coordinates = [gx_coord(val(el)) for el in els]
    timeEls = get(node, 'when')
    times = [val(t) for t in timeEls]
    return {
      'coords': coordinates,
      'times': times,
      }

# ---------------
# Main functions
# ---------------
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
    if not color:
        return '#000000', 1

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

def build_leaflet_style(node):
    """
    Given a DOM node, grab its top-level Style nodes, convert
    every one into a Leaflet style dictionary, put them in
    a master dictionary of the form

        #style ID -> Leaflet style dictionary,
        
    and return the result.

    The the possible keys of each Leaflet style dictionary,
    the style options, are
 
    - ``iconUrl``: URL of icon
    - ``weight``:  stroke width in pixels
    - ``color``: stroke color; RGB hex string
    - ``opacity``: stroke opacity
    - ``fillColor``: fill color; RGB hex string
    - ``fillOpacity``: fill opacity
    """
    d = {}
    for item in get(node, 'Style'):
        style_id = '#' + attr(item, 'id')
        # Create style properties
        props = {}
        for style in get(item, 'LineStyle'):
            rgb, opacity = build_rgb_and_opacity(
              val(get1(style, 'color')))
            width = valf(get1(style, 'width'))
            props['color'] = rgb
            props['opacity'] = opacity
            if width is not None:
                props['weight'] = width
        for style in get(item, 'PolyStyle'):
            rgb, opacity = build_rgb_and_opacity(
              val(get1(style, 'color')))
            props['fillColor'] = rgb
            props['fillOpacity'] = opacity
        for style in get(item, 'IconStyle'):
            icon = get1(style, 'Icon')
            if not icon:
                continue
            # Clear previous style properties
            props = {}
            props['iconUrl'] = val(get1(icon, 'href'))
            
        d[style_id] = props
        
    return d

def build_geometry(node):
    """
    Return a (decoded) GeoJSON geometry dictionary corresponding
    to this node.
    """
    geoms = []
    coordTimes = []
    if get1(node, 'MultiGeometry'):  
        return build_geometry(get1(node, 'MultiGeometry')) 
    if get1(node, 'MultiTrack'):
        return build_geometry(get1(node, 'MultiTrack')) 
    if get1(node, 'gx:MultiTrack'):
        return build_geometry(get1(node, 'gx:MultiTrack')) 
    for geoType in GEOTYPES: 
        geoNodes = get(node, geoType)
        if not geoNodes:
            continue 
        for geoNode in geoNodes:
            if geoType == 'Point': 
                geoms.append({
                  'type': 'Point',
                  'coordinates': coord1(val(get1(
                    geoNode, 'coordinates')))
                  })
            elif geoType == 'LineString':
                geoms.append({
                  'type': 'LineString',
                  'coordinates': coords(val(get1(
                    geoNode, 'coordinates')))
                  })
            elif geoType == 'Polygon':
                rings = get(geoNode, 'LinearRing')
                coordinates = [coords(val(get1(ring, 'coordinates')))
                  for ring in rings]
                geoms.append({
                  'type': 'Polygon',
                  'coordinates': coordinates,
                  })
            elif geoType in ['Track', 'gx:Track']: 
                track = gx_coords(geoNode)
                geoms.append({
                  'type': 'LineString',
                  'coordinates': track['coords'],
                  })
                if track['times']:
                    coordTimes.append(track['times'])
                
    return {'geoms': geoms, 'coordTimes': coordTimes}
    
def build_feature(node):
    """
    Return the (decoded) GeoJSON feature dictionary corresponding to this node,
    if it exists.
    Otherwise, return ``None``.
    """
    geomsAndTimes = build_geometry(node)
    properties = {}
    name = val(get1(node, 'name'))
    styleUrl = val(get1(node, 'styleUrl'))
    description = val(get1(node, 'description'))
    timeSpan = get1(node, 'TimeSpan')
    extendedData = get1(node, 'ExtendedData')
    lineStyle = get1(node, 'LineStyle')
    polyStyle = get1(node, 'PolyStyle')

    if not geomsAndTimes['geoms']:
        return None
    if name:
        properties['name'] = name
    if styleUrl : 
        if styleUrl[0] != '#': 
            styleUrl = '#' + styleUrl
        properties['styleId'] = styleUrl
    if description: 
        properties['description'] = description
    if timeSpan: 
        begin = val(get1(timeSpan, 'begin'))
        end = val(get1(timeSpan, 'end'))
        properties['timespan'] = {'begin': begin, 'end': end}
    if lineStyle:
        rgb, opacity = build_rgb_and_opacity(val(get1(
          lineStyle, 'color')))
        width = valf(get1(lineStyle, 'width'))
        properties['color'] = rgb
        properties['opacity'] = opacity
        if width is not None:
            properties['weight'] = width 
    if polyStyle:
        rgb, opacity = build_rgb_and_opacity(val(get1(
          polyStyle, 'color'))),
        fill = val(get1(polyStyle, 'fill'))
        outline = val(get1(polyStyle, 'outline'))
        properties['fillColor'] = rgb
        properties['opacity'] = opacity
        if fill: 
            properties['fillOpacity'] = fill 
        if outline: 
            properties['weight'] = outline
    if extendedData:
        datas = get(extendedData, 'Data'),
        simpleDatas = get(extendedData, 'SimpleData')
        for data in datas:
            properties[data.getAttribute('name')] = val(get1(
              data, 'value'))
        for simpleData in simpleDatas:
            properties[simpleData.getAttribute('name')] = val(simpleData) 
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
    
    if attr(node, 'id'):
        feature['id'] = attr(node, 'id')

    return feature     

def build_geojson(node):
    """
    Convert the given DOM node into a (decoded) GeoJSON FeatureCollection.
    """
    geojson = {
      'type': 'FeatureCollection',
      'features': []
      }
    for placemark in get(node, 'Placemark'):
        feature = build_feature(placemark)
        if feature is not None:
            geojson['features'].append(feature)
    return geojson   

def build_geojson_layers(node):
    """
    Return a list of dictionaries, one for each folder in 
    the given DOM node that contains geodata.
    Each dictionary has the form::

        {
          'name': folder name,
          'geojson': (decoded) GeoJSON FeatureCollection 
        }

    The GeoJSON part is created using :func:`build_geojson`.
    """
    layers = []
    for folder in get(node, 'Folder'):
        geojson = build_geojson(folder) 
        if not geojson['features']:
            continue
        layer = {}
        layer['name'] = val(get1(folder, 'name'))
        layer['geojson'] = geojson
        layers.append(layer)
    return layers

@click.command()
@click.option('--output_dir', type=str, default=None)
@click.option('--style_type', type=str, default=None)
@click.option('--separate_layers', type=bool, default=True)
@click.argument('kml_path', type=str)
def kml2geojson(kml_path, output_dir=None, separate_layers=True, 
  style_type=None):
    """
    Given a path to a KML file, convert the file into multiple 
    GeoJSON FeatureCollections, one for each top-level KML folder 
    containing geodata (if ``separate_layers == True``, the default), 
    or convert the file into a single GeoJSON FeatureCollection 
    (if ``separate_layers == False``).
    Write the resulting file(s) to the given
    output directory (the default is the parent directory of ``kml_path``).
    
    If ``style_type`` is not ``None`` (default is ``None``), 
    then also build and write a JSON style file of the given style type
    to the output directory.
    Acceptable style types are listed in ``STYLE_TYPES``.
    """
    # Create absolute paths
    kml_path = pathlib.Path(kml_path).resolve()
    if output_dir is None:
        output_dir = kml_path.parent
    else:
        output_dir = pathlib.Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    output_dir = output_dir.resolve()

    # Parse KML
    with kml_path.open('r') as src:
        kml_str = src.read()
    root = md.parseString(kml_str)

    # Build and export GeoJSON layers
    if separate_layers:
        layers = build_geojson_layers(root)
    else:
        name = kml_path.name.replace('.kml', '')
        layers = [{'name': name, 'geojson': build_geojson(root)}]
    for layer in layers:
        file_name = layer['name'].lower().replace(' ', '_') + '.geojson'
        path = pathlib.Path(output_dir, file_name)
        with path.open('w') as tgt:
            json.dump(layer['geojson'], tgt)

    # Build and export style file if desired
    if style_type in STYLE_TYPES:
        builder_name = 'build_{!s}_style'.format(style_type)
        style_dict = globals()[builder_name](root)
        path = pathlib.Path(output_dir, 'style.json')
        with path.open('w') as tgt:
            json.dump(style_dict, tgt)