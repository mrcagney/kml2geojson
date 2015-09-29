import json
import subprocess
import tempfile
from copy import deepcopy

import xmltodict


def build_rgb_and_opacity(kml_color_str):
    """
    Given a KML color string, return an equivalent
    RGB hex color string and an opacity float value.
    For example::

        >>> to_rgb_and_opacity('ff009911')
        '#119900', 1.0

    """
    s = kml_color_str
    if isinstance(s, str):
        b = s[-6:-4]
        g = s[-4:-2]
        r = s[-2:]
        rgb = '#' + r + g + b
        opacity = s[0:2]        
    else:
        rgb = '#000000'
        opacity = 'ff'
        
    # Convert opacity to int
    opacity = round(int(opacity, 16)/256, 2)
    
    return rgb, opacity

def build_leaflet_styles(kml_str):
    """
    Given a KML string, grab its kml > Document > Style node,
    convert it to a dictionary of the form
    
        #style ID -> Leaflet style dictionary
        
    and return the result.
    """
    # Convert to JSON dict and grab style list only
    x = xmltodict.parse(kml_str)
    x = json.loads(json.dumps(x))
    style_list = x['kml']['Document']['Style']
    
    # Convert to dict keyed by @id
    d = {}
    for item in style_list:
        style_id = '#' + item.pop('@id')
        # Create style properties
        props = {}
        if 'LineStyle' in item:
            x = item['LineStyle']
            if 'color' in x:
                rgb, opacity = build_rgb_and_opacity(x['color'])
                props['color'] = rgb
                props['opacity'] = opacity
            if 'width' in x:
                props['weight'] = float(x['width'])
        if 'PolyStyle' in item:
            x = item['PolyStyle']
            if 'color' in x:
                rgb, opacity = build_rgb_and_opacity(x['color'])
                props['fillColor'] = rgb
                props['fillOpacity'] = opacity
        if 'IconStyle' in item:
            # Clear previous style properties
            props = {}
            x = item['IconStyle']
            props['iconUrl'] = x['Icon']['href']
            
        d[style_id] = props
        
    return d

def build_geojson(kml_str):
    """
    Convert the given KML string to a (decoded) GeoJSON FeatureCollection.
    To do so, use the Node package ``togeojson``.
    Assume the Node package is installed.
    Throw a ``subprocess.CalledProcessError`` if Node call fails.
    """
    # Write to a temporary file, then call togeojson
    with tempfile.NamedTemporaryFile(mode='wt') as f:
        f.write(kml_str)
        x = subprocess.check_output(['togeojson', f.name])
    
    # Decode output into dict
    return json.loads(str(x, 'UTF-8'))

def build_geojson_layers(kml_str):
    """
    Return a list of dictionaries, one for each folder in 
    the given KML string that contains geodata.
    Each dictionary has the form::

        {
          'id': folder ID,
          'name': folder name,
          'layer': (decoded) GeoJSON FeatureCollection 
        }

    """
    x = xmltodict.parse(kml_str)
    y = deepcopy(x)

    layers = []
    for folder in x['kml']['Document']['Folder'][1:]:
        y['kml']['Document']['Folder'] = [folder]
        kml_str = xmltodict.unparse(y)
        try:
            g = build_geojson(kml_str)
        except subprocess.CalledProcessError:
            continue
        d = {
          'id': folder['@id'],
          'name': folder['name'],
          'layer': g,
          }            
        layers.append(d)

    return layers

# def run_togeojson(kml_path, geojson_path):
#     """
#     Convert the KML file located at ``kml_path`` to a GeoJSON file
#     located at ``geojson_path``.
#     To do so, use the Node package ``togeojson``.
#     Assume the Node package is installed.
#     Throw an ``CalledProcessError`` if the command fails. 
#     """
#     with open(geojson_path, 'w') as tgt:
#         subprocess.check_call(['togeojson', kml_path], stdout=tgt)

def kml2geojson(kml_path, geojson_path, json_path=None):
    run_togeojson(kml_path, geojson_path)

    # Create style file if desired
    if json_path is not None:
        with open(kml_path, 'r') as src:
            kml_str = src.read() 
        style = build_leaflet_styles(kml_str)
        with open(json_path, 'w') as tgt:
            json.dump(style, tgt)
