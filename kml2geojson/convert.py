import json

import xmltodict


def get_rgb_and_opacity(color):
    if isinstance(color, str):
        r = color[-2:]
        g = color[-4:-2]
        b = color[-6:-4]
        rgb = r + g + b
        opacity = color[0:2]        
    else:
        rgb = '000000'
        opacity = 'ff'
        
    # Convert opacity to int
    opacity = round(int(opacity, 16)/256, 2)
    
    return rgb, opacity

def build_leaflet_style(kml_str):
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
                rgb, opacity = get_rgb_and_opacity(x['color'])
                props['color'] = rgb
                props['opacity'] = opacity
            if 'width' in x:
                props['weight'] = x['width']
        if 'PolyStyle' in item:
            x = item['LineStyle']
            if 'color' in x:
                rgb, opacity = get_rgb_and_opacity(x['color'])
                props['fillColor'] = rgb
                props['fillOpacity'] = opacity
        if 'IconStyle' in item:
            # Clear other style properties
            props = {}
            x = item['IconStyle']
            props['iconUrl'] = x['Icon']['href']
            
        d[style_id] = props
        
    return d