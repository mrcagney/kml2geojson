import xml.dom.minidom as md
import re
import pathlib
import json

import click


#: Atomic KML geometry types supported.
#: MultiGeometry is handled separately.
GEOTYPES = [
  'Polygon', 
  'LineString', 
  'Point', 
  'Track', 
  'gx:Track',
  ]

#: Supported style types
STYLE_TYPES = [
  'svg',
  'leaflet',
  ]

SPACE = re.compile(r'\s+')

# ----------------
# Helper functions
# ----------------
def get(node, name):
    """
    Given a KML Document Object Model (DOM) node, return a list
    of its sub-nodes that have the given tag name.
    """
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
    Return as a string the value of the given DOM node's attribute named 
    by ``name``, if it exists.
    Otherwise, return an empty string.
    """
    return node.getAttribute(name)

def val(node):
    """
    Normalize the given DOM node and return the value 
    of its first child (the string content of the node).
    """
    try:
        node.normalize()
        return node.firstChild.wholeText  # Handles CDATASection too
    except AttributeError:
        return ''

def valf(node):
    """
    Cast ``val(node)`` as a float.
    Return ``None`` if that does not work.
    """
    try:
        return float(val(node))
    except ValueError:
        return None
    
def numarray(a):
    """
    Cast the given list into a list of floats.
    """
    return [float(aa) for aa in a]

def coords1(s):
    """
    Convert the given KML string containing one coordinate tuple into a list
    of floats.

    EXAMPLE::

        >>> coords1(' -112.2,36.0,2357 ')
        [-112.2, 36.0, 2357.0]

    """
    return numarray(re.sub(SPACE, '', s).split(',')) 

def coords(s):
    """ 
    Convert the given KML string containing multiple coordinate tuples into
    a list of lists of floats.

    EXAMPLE::

        >>> coords('''
        ... -112.0,36.1,0
        ... -113.0,36.0,0 
        ... ''')
        [[-112.0, 36.1, 0.0], [-113.0, 36.0, 0.0]]

    """
    s = s.split() #sub(TRIM_SPACE, '', v).split()
    return [coords1(ss) for ss in s]
     
def gx_coords1(s):
    """
    Convert the given KML string containing one gx coordinate tuple
    into a list of floats.

    EXAMPLE::

        >>> gx_coords1('-113.0 36.0 0') 
        [-113.0, 36.0, 0.0]

    """
    return numarray(s.split(' '))

def gx_coords(node):
    """
    Given a KML DOM node, grab its <gx:coord> and <gx:timestamp><when>
    subnodes, and convert them into a dictionary with the keys and values

    - ``'coordinates'``: list of lists of float coordinates
    - ``'times'``: list of timestamps corresponding to the coordinates

    """
    els = get(node, 'gx:coord')
    coordinates = []
    times = []
    coordinates = [gx_coords1(val(el)) for el in els]
    time_els = get(node, 'when')
    times = [val(t) for t in time_els]
    return {
      'coordinates': coordinates,
      'times': times,
      }

# ---------------
# Main functions
# ---------------
def build_rgb_and_opacity(s):
    """
    Given a KML color string, return an equivalent
    RGB hex color string and an opacity float 
    rounded to 2 decimal places.
    
    EXAMPLE::

        >>> build_rgb_and_opacity('ee001122')
        ('#221100', 0.93)

    """
    # Set defaults
    color = '000000'
    opacity = 1
   
    if s.startswith('#'):
        s = s[1:]
    if len(s) == 8:
        color = s[6:8] + s[4:6] + s[2:4]
        opacity = round(int(s[0:2], 16)/256, 2)
    elif len(s) == 6:
        color = s[4:6] + s[2:4] + s[0:2]        
    elif len(s) == 3:
        color = s[::-1]
    
    return '#' + color, opacity

def build_svg_style(node):
    """
    Given a DOM node, grab its top-level Style nodes, convert
    every one into a SVG style dictionary, put them in
    a master dictionary of the form

        #style ID -> SVG style dictionary,
        
    and return the result.

    The possible keys and values of each SVG style dictionary,
    the style options, are
 
    - ``iconUrl``: URL of icon
    - ``stroke``: stroke color; RGB hex string
    - ``stroke-opacity``: stroke opacity
    - ``stroke-width``:  stroke width in pixels
    - ``fill``: fill color; RGB hex string
    - ``fill-opacity``: fill opacity
    """
    d = {}
    for item in get(node, 'Style'):
        style_id = '#' + attr(item, 'id')
        # Create style properties
        props = {}
        for x in get(item, 'LineStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['stroke'] = rgb
                props['stroke-opacity'] = opacity
            width = valf(get1(x, 'width'))
            if width is not None:
                props['stroke-width'] = width
        for x in get(item, 'PolyStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['fill'] = rgb
                props['fill-opacity'] = opacity
            fill = valf(get1(x, 'fill'))
            if fill: 
                properties['fill-opacity'] = fill 
            outline = valf(get1(x, 'outline'))
            if outline: 
                properties['stroke-opacity'] = outline
        for x in get(item, 'IconStyle'):
            icon = get1(x, 'Icon')
            if not icon:
                continue
            # Clear previous style properties
            props = {}
            props['iconUrl'] = val(get1(icon, 'href'))
            
        d[style_id] = props
        
    return d

def build_leaflet_style(node):
    """
    Given a DOM node, grab its top-level Style nodes, convert
    every one into a Leaflet style dictionary, put them in
    a master dictionary of the form

        #style ID -> Leaflet style dictionary,
        
    and return the result.

    The the possible keys and values of each Leaflet style dictionary,
    the style options, are
 
    - ``iconUrl``: URL of icon
    - ``color``: stroke color; RGB hex string
    - ``opacity``: stroke opacity
    - ``weight``:  stroke width in pixels
    - ``fillColor``: fill color; RGB hex string
    - ``fillOpacity``: fill opacity
    """
    d = {}
    for item in get(node, 'Style'):
        style_id = '#' + attr(item, 'id')
        # Create style properties
        props = {}
        for x in get(item, 'LineStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['color'] = rgb
                props['opacity'] = opacity
            width = valf(get1(x, 'width'))
            if width is not None:
                props['weight'] = width
        for x in get(item, 'PolyStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['fillColor'] = rgb
                props['fillOpacity'] = opacity
        for x in get(item, 'IconStyle'):
            icon = get1(x, 'Icon')
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
    to the given KML node.
    """
    geoms = []
    times = []
    if get1(node, 'MultiGeometry'):  
        return build_geometry(get1(node, 'MultiGeometry')) 
    if get1(node, 'MultiTrack'):
        return build_geometry(get1(node, 'MultiTrack')) 
    if get1(node, 'gx:MultiTrack'):
        return build_geometry(get1(node, 'gx:MultiTrack')) 
    for geotype in GEOTYPES: 
        geonodes = get(node, geotype)
        if not geonodes:
            continue 
        for geonode in geonodes:
            if geotype == 'Point': 
                geoms.append({
                  'type': 'Point',
                  'coordinates': coords1(val(get1(
                    geonode, 'coordinates')))
                  })
            elif geotype == 'LineString':
                geoms.append({
                  'type': 'LineString',
                  'coordinates': coords(val(get1(
                    geonode, 'coordinates')))
                  })
            elif geotype == 'Polygon':
                rings = get(geonode, 'LinearRing')
                coordinates = [coords(val(get1(ring, 'coordinates')))
                  for ring in rings]
                geoms.append({
                  'type': 'Polygon',
                  'coordinates': coordinates,
                  })
            elif geotype in ['Track', 'gx:Track']: 
                track = gx_coords(geonode)
                geoms.append({
                  'type': 'LineString',
                  'coordinates': track['coordinates'],
                  })
                if track['times']:
                    times.append(track['times'])
                
    return {'geoms': geoms, 'times': times}
    
def build_feature(node):
    """
    Build and return a (decoded) GeoJSON Feature corresponding to
    this KML node (typically a KML Placemark).
    Return ``None`` if no Feature can be built.
    """
    geoms_and_times = build_geometry(node)
    if not geoms_and_times['geoms']:
        return None

    properties = {}
    for x in get(node, 'name')[:1]:
        properties['name'] = val(x)
    for x in get(node, 'description')[:1]:
        description = val(x)
        if description:
            properties['description'] = val(x)
    for x in get(node, 'styleUrl')[:1]:
        style_url = val(x)
        if style_url[0] != '#': 
            style_url = '#' + style_url
        properties['styleUrl'] = style_url
    for x in get(node, 'LineStyle')[:1]:
        color = val(get1(x, 'color'))
        if color:
            rgb, opacity = build_rgb_and_opacity(color)
            properties['stroke'] = rgb
            properties['stroke-opacity'] = opacity
        width = valf(get1(x, 'width'))
        if width:
            properties['stroke-width'] = width 
    for x in get(node, 'PolyStyle')[:1]:
        color = val(get1(x, 'color'))
        if color:
            rgb, opacity = build_rgb_and_opacity(color)
            properties['fill'] = rgb
            properties['fill-opacity'] = opacity
        fill = valf(get1(x, 'fill'))
        if fill: 
            properties['fill-opacity'] = fill 
        outline = valf(get1(x, 'outline'))
        if outline: 
            properties['stroke-opacity'] = outline
    for x in get(node, 'ExtendedData')[:1]:
        datas = get(x, 'Data')
        for data in datas:
            properties[attr(data, 'name')] = val(get1(
              data, 'value'))
        simple_datas = get(x, 'SimpleData')
        for simple_data in simple_datas:
            properties[attr(simple_data, 'name')] = val(simple_data) 
    for x in get(node, 'TimeSpan')[:1]:
        begin = val(get1(x, 'begin'))
        end = val(get1(x, 'end'))
        properties['timeSpan'] = {'begin': begin, 'end': end}
    if geoms_and_times['times']:
        times = geoms_and_times['times']
        if len(times) == 1:
            properties['times'] = times[0]
        else:
            properties['times'] = times
    
    feature = {
      'type': 'Feature',
      'properties': properties,
      }

    geoms = geoms_and_times['geoms']
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

def build_feature_collection(node):
    """
    Build and return a (decoded) GeoJSON FeatureCollection
    corresponding to this KML DOM node (typically a KML Folder).
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

def build_layers(node):
    """
    Return a list of dictionaries, one for each folder in 
    the given KML DOM node that contains geodata.
    Each dictionary has the keys and values

    - ``'name'``: folder name
    - ``'geojson'``: (decoded) GeoJSON FeatureCollection 

    The GeoJSON part is created using :func:`build_feature_collection`.

    Warning: this can produce layers with the same geodata in case 
    the KML node has nested folders with geodata.
    """
    def default_name(n=None):
        if n is not None:
            return 'Untitled_{:02d}'.format(i)
        else:
            return 'Untitled'

    layers = []

    for i, folder in enumerate(get(node, 'Folder')):
        geojson = build_feature_collection(folder) 
        if not geojson['features']:
            continue
        layer = {}
        layer['name'] = val(get1(folder, 'name')) or default_name(i)
        layer['geojson'] = geojson
        layers.append(layer)
    if not layers:
        # No folders, so use the root node
        geojson = build_feature_collection(node) 
        if geojson['features']:
            layers.append({
              'name': default_name(),
              'geojson': geojson, 
              })

    return layers

@click.command()
@click.option('-f', '--separate-folders', is_flag=True, 
  default=False)
@click.option('-st', '--style_type', type=click.Choice(STYLE_TYPES), 
  default=None)
@click.option('-sf', '--style_filename', 
  default='style.json')
@click.argument('kml_path')
@click.argument('output_dir')
def main(kml_path, output_dir, separate_folders=False, 
  style_type=None, style_filename='style.json'):
    """
    Given a path to a KML file, convert it to one or several GeoJSON 
    FeatureCollection files and save the result(s) to the given 
    output directory.

    If ``separate_folders == False`` (the default), then create one
    GeoJSON file.
    If ``separate_folders == True``, then create several GeoJSON
    files, one for each folder in the KML file 
    that contains geodata or that has a descendant node that contains geodata.
    Warning: this can produce GeoJSON files with the same geodata in case 
    the KML file has nested folders with geodata.

    If a ``style_type`` is given (default is ``None``), 
    then also build a JSON style 
    file of the given style type and save it to the output directory
    under the name given by ``style_filename`` 
    (which defaults to 'style.json')
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
    if separate_folders:
        layers = build_layers(root)
    else:
        name = kml_path.name.replace('.kml', '')
        layers = [{
          'name': name, 
          'geojson': build_feature_collection(root),
          }]
    for layer in layers:
        file_name = layer['name'].lower().replace(' ', '_') + '.geojson'
        path = pathlib.Path(output_dir, file_name)
        with path.open('w') as tgt:
            json.dump(layer['geojson'], tgt)

    # Build and export style file if desired
    if style_type in STYLE_TYPES:
        builder_name = 'build_{!s}_style'.format(style_type)
        style_dict = globals()[builder_name](root)
        path = pathlib.Path(output_dir, style_filename)
        with path.open('w') as tgt:
            json.dump(style_dict, tgt)