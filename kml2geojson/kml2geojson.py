import json
import subprocess
import tempfile
from copy import deepcopy
import pathlib

import xmltodict
import click

def build_rgb_and_opacity(kml_color_str):
    """
    Given a KML color string, return an equivalent
    RGB hex color string and an opacity float 
    (rounded to 2 decimal places).
    
    For example::

        >>> build_rgb_and_opacity('ee001122')
        ('#221100', 0.93)

    """
    s = kml_color_str
    if isinstance(s, str):
        b = s[2:4]
        g = s[4:6]
        r = s[6:8]
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

    The Leaflet style options (the keys in the Leaflet style dictionaries) 
    are

    - ``iconUrl``: URL of icon
    - ``weight``:  stroke width in pixels
    - ``color``: stroke color; RGB hex string
    - ``opacity``: stroke opacity
    - ``fillColor``: fill color; RGB hex string
    - ``fillOpacity``: fill opacity
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
    To do so, use the Node.js package ``togeojson``.
    Assume the Node package is installed.
    Throw a ``subprocess.CalledProcessError`` if the Node call fails.
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
          'name': folder name,
          'geojson': (decoded) GeoJSON FeatureCollection 
        }

    The GeoJSON part is created using :func:`build_geojson`.
    """
    x = xmltodict.parse(kml_str)
    y = deepcopy(x)

    layers = []
    style = x['kml']['Document']['Style']
    for i, folder in enumerate(x['kml']['Document']['Folder']):
        # Need to included style with folder to avoid errors in build_geojson
        y['kml']['Document']['Folder'] = [style, folder]
        kml_str = xmltodict.unparse(y)
        try:
            g = build_geojson(kml_str)
        except subprocess.CalledProcessError:
            continue

        if 'name' in folder:
            name = folder['name']
        else:
            name = 'layer_{:03d}'.format(i)
        d = {
          'name': folder['name'],
          'geojson': g,
          }            
        layers.append(d)

    return layers

@click.command()
@click.argument('kml_path', type=str)
@click.argument('output_dir', type=str)
@click.option('--export_style', type=bool)
def convert(kml_path, output_dir='.', export_style=True):
    """
    Given a path to a KML file, convert the file to GeoJSON FeatureCollections,
    one for each KML folder, and write the resulting files to the given
    output directory (the default is the current directory).
    If ``export_style == True`` (the default), 
    then also build and write a Leaflet-based JSON style file to the 
    output directory.
    """
    # Create absolute paths
    kml_path = pathlib.Path(kml_path).resolve()
    output_dir
    output_dir = pathlib.Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    output_dir = output_dir.resolve()

    # Read KML
    with kml_path.open('r') as src:
        kml_str = src.read()
    
    # Build and export GeoJSON layers
    layers = build_geojson_layers(kml_str)
    for layer in layers:
        file_name = layer['name'].lower().replace(' ', '_') + '.geojson'
        path = pathlib.Path(output_dir, file_name)
        with path.open('w') as tgt:
            json.dump(layer['geojson'], tgt)

    # Build and export style file if desired
    if export_style:
        style = build_leaflet_styles(kml_str)
        path = pathlib.Path(output_dir, 'style.json')
        with path.open('w') as tgt:
            json.dump(style, tgt)


if __name__ == '__main__':
    convert()