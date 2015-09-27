from pykml import parser as kmlparser
import json
import argparse
import pandas as pd
from bs4 import BeautifulSoup as bs

def create_style_reference(path):
    """
    Reads the kml doc located at 'path' and creates a dictionary object
    with structure:
        dict = {
            'styleURL': {
                'icon': {
                    'href': 'BLAH',
                    'scale': float,
                },
                'linestring': {
                    'color': HEX COLOR,
                    'opacity': float
                    'width': float
                },
                'polygon': {
                    'line_color': HEX COLOR,
                    'line_width': float,
                    'color': HEX COLOR,
                    'opacity': float,
                    'outline: 0'
                }
            }
        }

    Assumes that 'Style' tag objects in the kml exist only at one level
    down from the document itself. I.e Styles cannot be inside placemark
    objects. This may or may not be the best thing to do. More testing 
    required.
    """
    styles_by_style_id = {}

    with open(path) as fio:
        doc_string = fio.read()

    root = kmlparser.fromstring(doc_string)
    document_obj = root.Document
    # For each style tag object in the document
    for style_obj in document_obj.Style:
        linestring_style_obj = None
        icon_style_obj = None
        polygon_style_obj = None

        # Find the styles id and store it
        for item in style_obj.items():
            if item[0] == 'id':
                style_id = item[1]

        # Preload the dtyle dictionary for this object
        styles_by_style_id[style_id] = {
          'icon': {'href': None, 'scale': None},
          'linestring': {'color': None, 'opacity': None, 'width': None},
          'polygon': {
            'line_color': None, 'line_width': None,
            'color': None, 'opacity': None, 'outline': None
          },
        }

        # Get icon (point) style
        try:
            icon_style_obj = style_obj.IconStyle

            styles_by_style_id[style_id]['icon']['href'] = \
              icon_style_obj.Icon.href.text

            styles_by_style_id[style_id]['icon']['scale'] = \
              icon_style_obj.scale.pyval
        except AttributeError:
            pass

        # Get linestring style
        try:
            linestring_style_obj = style_obj.LineStyle

            # Check for color of int(0). Should be Hex
            if type(linestring_style_obj.color.pyval) == int:
                styles_by_style_id[style_id]['linestring']['color'] = \
                  '000000'
                styles_by_style_id[style_id]['linestring']['opacity'] = \
                  '00'
            else:
                # 8 digit hex stored in bgr. Need rgb
                r = linestring_style_obj.color.text[-2:]
                g = linestring_style_obj.color.text[-4:-2]
                b = linestring_style_obj.color.text[-6:-4]
                styles_by_style_id[style_id]['linestring']['color'] = r+g+b

                styles_by_style_id[style_id]['linestring']['opacity'] = \
                  linestring_style_obj.color.text[0:2]

            styles_by_style_id[style_id]['linestring']['width'] = \
              linestring_style_obj.width.pyval
        except AttributeError:
            pass

        # Get polygon style
        try:
            polygon_style_obj = style_obj.PolyStyle

            # Check for color of int(0). Should be Hex
            if type(polygon_style_obj.color.pyval) == int:
                styles_by_style_id[style_id]['polygon']['color'] = \
                  '000000'
                styles_by_style_id[style_id]['polygon']['opacity'] = \
                  '00'
            else:
                # 8 digit hex stored in bgr. Need rgb
                r = polygon_style_obj.color.text[-2:]
                g = polygon_style_obj.color.text[-4:-2]
                b = polygon_style_obj.color.text[-6:-4]
                styles_by_style_id[style_id]['polygon']['color'] = r+g+b
                styles_by_style_id[style_id]['polygon']['opacity'] = \
                  polygon_style_obj.color.text[0:2]

            styles_by_style_id[style_id]['polygon']['outline'] = \
              polygon_style_obj.outline.pyval

            # if the polygon is outlined get the line style in the object and
            # apply it to the polygon
            try:
                if polygon_style_obj.outline.pyval == 1:
                    styles_by_style_id[style_id]['polygon']['line_color'] = \
                      styles_by_style_id[style_id]['linestring']['color']
                    styles_by_style_id[style_id]['polygon']['line_width'] = \
                      styles_by_style_id[style_id]['linestring']['width']
            except AttributeError:
                pass

        except AttributeError:
            pass

    return styles_by_style_id

def hex_opacity_to_decimal(hex_opacity):
    """
    Takes a two digit hex opacity and converts it to a 
    decimal. e.g 4f --> 0.3098... and ff --> 1.0
    """
    if hex_opacity != None:
        return float(int(hex_opacity,16))/float(255)
    else: 
        return None

def create_kml_dict(path):
    """
    Reads the kml doc located at 'path' and creates a dictionary
    object with structure:

    dict = {
        folder_name: {
            placemark_name: {
                html: 'xxx'
                style_id: 'xxx',
                points: {
                    point_id: {coords: (x,y)}
                },
                linestrings: {
                    linestring_id: {coords: [(x1,y1),(x2,y2)...]}
                },
                polygons: {
                    polygon_id: {coords: [(x1,y1),(x2, y2)...(x1,y1)]}
                },
            }   
        }
    }   
    """

    with open(path) as fio:
        doc_string = fio.read()

    root = kmlparser.fromstring(doc_string)
    document_obj = root.Document
    # Folder objects one level deep in document
    doc_folders_objs = document_obj.Folder
    geometries_by_placemark_id_by_folder_name = {}

    # For each of the folders one level below the doc object
    count = 0
    for doc_folders_obj in doc_folders_objs:

        # Check for nested folders within this folder (note: we only 
        # check one additional level for nested folders. Could recurrsively
        # check for more at a later date)
        folder_objs = [doc_folders_obj]
        try:
            nested_folders = doc_folders_obj.Folder
            # There are nested folders...
            for nf in nested_folders:
                folder_objs.append(nf)
        except AttributeError:
            # No nested folders
            pass

        # Will mostly only evaluate once as most folders don't have nested
        # folders
        for folder_obj in folder_objs:
            f_name = str(folder_obj.name.text)
            geometries_by_placemark_id_by_folder_name[f_name] = {}
            # Check case that folder has no placemarks
            try:
                # Get the placemarks in the current folder
                placemark_objs = folder_obj.Placemark
                for placemark_obj in placemark_objs:

                    # Get the html 'description' of the placemark
                    try:
                        html = placemark_obj.description.text
                    except AttributeError:
                        html = ''
                    # Get the style ID of the placemark. 
                    style_id = placemark_obj.styleUrl.text[1::]

                    # If the placemark style points to StyleMap, then take 
                    # the first pair and the first styleURL as the style URL 
                    # (yes I know this is a dirty hack)
                    try:
                        style_maps = document_obj.StyleMap
                        for style_map in style_maps:
                            for item in style_map.items():
                                if item[0] == 'id':
                                    style_map_id = item[1]
                                    if style_id == style_map_id:
                                        style_id = style_map.Pair[0]\
                                          .styleUrl.text[1::]
                    except AttributeError:
                        pass

                    # Set default to be name, in case no id exists
                    pm_id = placemark_obj.name.text
                    for item in placemark_obj.items():
                        if item[0] == 'id':
                            pm_id = item[1]

                    geometries_by_placemark_id_by_folder_name[
                      f_name][pm_id] = {
                        'html': html,
                        'style_id': style_id,
                        'points': {},
                        'linestrings': {},
                        'polygons': {},
                    }

                    point_id = 1
                    linestring_id = 1
                    polygon_id = 1
                    # Look for MultiGeometry objects
                    try: 
                        multigeometry_objs = placemark_obj.MultiGeometry
                        # For each multiGeom object, look for linestrings, 
                        # points and polygons and add these to the placemarks 
                        # geom objects
                        for multigeometry_obj in multigeometry_objs:

                            # Look for points in the multigeom
                            try: 
                                multigeometry_points = \
                                  multigeometry_obj.Point

                                for point_obj in multigeometry_points:
                                    geometries_by_placemark_id_by_folder_name[
                                      f_name][pm_id]['points'][point_id] = {
                                      'coords': clean_point_coords(
                                      point_obj.coordinates.text)}
                                    point_id += 1
                            except AttributeError:
                                # No point objects
                                pass

                            # Look for linestrings in the multigeom
                            try: 
                                multigeometry_linestrings = \
                                  multigeometry_obj.LineString

                                for linestring_obj in multigeometry_linestrings:
                                    geometries_by_placemark_id_by_folder_name[
                                      f_name][pm_id]['linestrings'][linestring_id] =\
                                      {'coords': clean_listed_coords(
                                      linestring_obj.coordinates.text)}
                                    linestring_id += 1
                            except AttributeError:
                                # No linestring objects
                                pass

                            # Look for polygons in the multigeom
                            try: 
                                multigeometry_polygons = \
                                  multigeometry_obj.Polygon

                                for polygon_obj in multigeometry_polygons:
                                    geometries_by_placemark_id_by_folder_name[
                                      f_name][pm_id]['polygons'][polygon_id] =\
                                      {
                                      'coords': clean_listed_coords(
                                        polygon_obj.outerBoundaryIs\
                                        .LinearRing.coordinates.text,
                                        polygon=True)
                                      }
                                    polygon_id += 1
                            except AttributeError:
                                # No polygon objects
                                pass
                    except AttributeError:
                        # No multigeometry objects
                        pass

                    # LOOK FOR OBJECTS IN THE PLACEMARK ###############################
                    # Look for points in the placemark
                    try: 
                        placemark_points = placemark_obj.Point

                        for point_obj in placemark_points:
                            geometries_by_placemark_id_by_folder_name[
                              f_name][pm_id]['points'][point_id] = {
                              'coords': clean_point_coords(
                              point_obj.coordinates.text)}
                            point_id += 1
                    except AttributeError:
                        # No point objects
                        pass

                    # Look for linestrings in the placemark
                    try: 
                        placemark_linestrings = placemark_obj.LineString

                        for linestring_obj in placemark_linestrings:
                            geometries_by_placemark_id_by_folder_name[
                              f_name][pm_id]['linestrings'][linestring_id] = {
                              'coords': clean_listed_coords(
                              linestring_obj.coordinates.text)}
                            linestring_id += 1
                    except AttributeError:
                        # No linestring objects
                        pass

                    # Look for polygons in the placemark
                    try: 
                        placemark_polygons = placemark_obj.Polygon

                        for polygon_obj in placemark_polygons:
                            geometries_by_placemark_id_by_folder_name[
                              f_name][pm_id]['polygons'][polygon_id] = {
                              'coords': clean_listed_coords(polygon_obj. \
                              outerBoundaryIs.LinearRing.coordinates.text, 
                              polygon=True)}
                            polygon_id += 1
                    except AttributeError:
                        # No polygon objects
                        pass
            except AttributeError:
                pass

    return geometries_by_placemark_id_by_folder_name

def clean_point_coords(coords_string):
    """
    Takes a string of coords, e.g ' 174.7673352033589,-36.84672220664692,0'
    and converts to a list of floats, stripping off the z coord 
    e.g [174.7673352033589,-36.84672220664692]
    """
    coord_list = []
    for coord in coords_string.split(',')[0:2]:
        try:
            coord_list.append(float(coord))
        except ValueError:
            coord_list.append(0.0)
    return coord_list

def clean_listed_coords(coords_string, polygon=False):
    """
    Takes a string of coords, e.g 
    ' 174.7673352033589,-36.84672220664692,0 
      178.25673432033589,-33.45672220664692,0'
    and converts to a list of lists containing floats, 
    stripping off the z coord in the process
    e.g [ [174.7673352033589,-36.84672220664692],
          [178.25673432033589,-33.45672220664692] ]

    if polygon == True, return a list around the list of lists
    """
    list_of_strings = [s for s in coords_string.split()]
    list_of_lists = []
    for s in list_of_strings:
        coord_list = []
        for coord in s.split(',')[0:2]:
            try:
                coord_list.append(float(coord))
            except ValueError:
                coord_list.append(0.0)
        list_of_lists.append(coord_list)

    if polygon:
        return [list_of_lists]
    else:
        return list_of_lists

def create_geoJSON(geoms_dict, style_ref, required_rows_by_kml_rows):
    """
    Takes a deconstructed kml file and turns it into a geoJSON object.
    Folders become feature collections.
    """
    geoJSON_feature_collections = []
    num_feature_collections = 0
    for folder in geoms_dict:
        # Add new feature collection
        geoJSON_feature_collections.append({
          "name": folder,
          "type": "FeatureCollection",
          "features": []
        })

        for pm in geoms_dict[folder]:
            style_id = geoms_dict[folder][pm]['style_id']
            html = get_required_html(
              html=geoms_dict[folder][pm]['html'], 
              required_rows_by_kml_rows=required_rows_by_kml_rows)
            
            # Account for the possibility that a style was not caught by the style reference function. Possibly because it was in a folder not the document
            try:
                href = style_ref[style_id]['icon']['href']
                scale = style_ref[style_id]['icon']['scale']
            except KeyError:
                continue

            linestring_col = style_ref[style_id]['linestring']['color']
            linestring_op = hex_opacity_to_decimal(
              style_ref[style_id]['linestring']['opacity'])
            linestring_width = style_ref[style_id]['linestring']['width']

            polygon_col = style_ref[style_id]['polygon']['color']
            polygon_line_col = style_ref[style_id]['polygon']['line_color']
            polygon_line_width = style_ref[style_id]['polygon']['line_width']
            polygon_op = hex_opacity_to_decimal(
              style_ref[style_id]['polygon']['opacity'])
            polygon_outline = style_ref[style_id]['polygon']['outline']

            # Parse the point objects
            for point_id in geoms_dict[folder][pm]['points']:

                coords = geoms_dict[folder][pm]['points'][point_id]['coords']

                geoJSON_feature_collections[
                  num_feature_collections]['features'].append({
                  "type": "Feature",
                  "geometry": {"type": "Point", "coordinates": coords},
                  "properties": {"href": href, "scale": scale, "html": html}
                })

            # Parse the linestring objects
            for linestring_id in geoms_dict[folder][pm]['linestrings']:

                coords = geoms_dict[
                  folder][pm]['linestrings'][linestring_id]['coords']

                geoJSON_feature_collections[
                  num_feature_collections]['features'].append({
                  "type": "Feature",
                  "geometry": {"type": "LineString", "coordinates": coords},
                  "properties": {"color": linestring_col, "html": html,
                    "opacity": linestring_op, "width": linestring_width}
                })

            # Parse the polygon objects
            for polygon_id in geoms_dict[folder][pm]['polygons']:

                coords = geoms_dict[
                  folder][pm]['polygons'][polygon_id]['coords']

                geoJSON_feature_collections[
                  num_feature_collections]['features'].append({
                  "type": "Feature",
                  "geometry": {"type": "Polygon", "coordinates": coords},
                  "properties": {"color": polygon_col, "opacity": polygon_op, 
                    "outline": polygon_outline, "line_color": polygon_line_col,
                    "line_width": polygon_line_width, "html": html}
                })

        num_feature_collections += 1

    return geoJSON_feature_collections

def get_required_html(html, required_rows_by_kml_rows):
    """
    Given a dict of required row names, keyed by the row names as they are
    found in the KML, eg. {'num_cats': '#Cats', 'num_dogs': '#Dogs'}, 
    with html in the KML such as: 

    <td>num_cats</td>
    <td>5</td>
    <td>num_dogs</td>
    <td>2</td>
    <td>num_badgers</td>
    <td>11</td>

    Return the snippet of html that corresponds to to the required rows. 
    i.e return 
    <td>#Cats</td>
    <td>5</td>
    <td>#Dogs</td>
    <td>2</td>

    if required_rows_by_kml_rows is empty, return None
    """
    required_html = ''
    if required_rows_by_kml_rows:
        html_soup = bs(html)
        tds = html_soup.find_all('td')
        rows_found = 0
        required_html += '<table>'
        for i in range(len(tds)):
            if tds[i].text in required_rows_by_kml_rows:
                rows_found += 1
                required_html += \
                  '<tr><td><b>' \
                  + required_rows_by_kml_rows[tds[i].text] \
                  +'</b></td><td>' \
                  + tds[i+1].text + \
                  '</td></tr>'
        required_html += '</table>'

        if rows_found == 0:
            return '<div> No popup content </div>'
        else:
            return required_html
    else:
        return None

def write_out_geojson(list_of_feature_classes, path, file_name_prefix='fc_'):
    """
    'list_of_feature_classes' is a list of dictionary objects

    For each feature class dictionary, in 'list_of_feature_classes'
    write the feature class to it's own geojson file
    """
    i = 1
    for feature_class in list_of_feature_classes:
        json.dump(
          feature_class, 
          open(path + file_name_prefix + str(i) + '.geojson', 'w'))
        i += 1

def convert_kml_to_geojson(input_file_path, output_folder_path, 
  file_name_prefix='fc_', required_rows_by_kml_rows={}):
    """
    Execute the process to convert a kml doc to a set of geojson files. One 
    geojson file corresponds to one feature class which corresponds to one 
    'folder' in the KML.
    """
    style_ref_from_kml = create_style_reference(path=input_file_path)
    geoms_dict_from_kml = create_kml_dict(path=input_file_path)
    geoJson_feature_classes = create_geoJSON(
      geoms_dict=geoms_dict_from_kml, 
      style_ref = style_ref_from_kml,
      required_rows_by_kml_rows=required_rows_by_kml_rows)
    write_out_geojson(
      list_of_feature_classes=geoJson_feature_classes,
      path=output_folder_path, 
      file_name_prefix=file_name_prefix)

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
      description='Required files for Kml to GeoJSON conversion')
    parser.add_argument("--inputfile", type=str, required=True, help="The full path to the input KML file")
    parser.add_argument("--outputfolder", type=str, required=True, help="The full path to the output folder, including the trailing '/'")
    parser.add_argument("--datafile", type=str, help="OPTIONAL: The full path to a csv file containing columns 'raw' and 'popup'. The 'raw' column contains the data column names as they appear in the KML and the 'popup' column contains the corresponding column name to display in the popup")
    
    # Vars stored in args.inputfile, args.outputfolder and args.datafile
    args = parser.parse_args()
    
    required_data_row_names_by_kml_names = {}
    # Read datafile csv and populate dict if it was given
    if args.datafile is not None:
        data_df = pd.read_csv(args.datafile, dtype=str)
        for i, row in data_df.iterrows():
            required_data_row_names_by_kml_names[row['raw']] = row['popup']

    print("\n")
    print("======================= Converting =========================")
    print("------------------------------------------------------------")
    print("Creating Style Reference...")
    style_ref_from_kml = create_style_reference(path=args.inputfile)
    print("Done!")
    print("------------------------------------------------------------")
    print("Creating Geometry Reference from KML Objects...")
    geoms_dict_from_kml = create_kml_dict(path=args.inputfile)
    print("Done!")
    print("------------------------------------------------------------")
    print("Creating GeoJSON...")
    geoJson_feature_classes = create_geoJSON(
      geoms_dict=geoms_dict_from_kml, 
      style_ref = style_ref_from_kml,
      required_rows_by_kml_rows=required_data_row_names_by_kml_names)
    print("Done!")
    print("------------------------------------------------------------")
    print "Writing GeoJSON to: ", args.outputfolder
    write_out_geojson(
      list_of_feature_classes=geoJson_feature_classes,
      path=args.outputfolder, 
      file_name_prefix="fc_")
    print("Done!")
    print("------------------------------------------------------------")
    print("Creating config.json...")
    config_file = json.dumps({
        'title': 'Enter the map title here...',
        'description': 'Enter the map description here',
        'use_canvas': 'Enter 1 or 0 between the quotes here. Enter 1 for big maps',
        'layer_order': ["Enter the layers in the order you want them to display. Enter the layer you want on the top last. Leave the array blank if the layer order doesn't matter.."]
    }, indent=4, sort_keys=True)
    with open(args.outputfolder + 'config.json', 'w') as config_f:
        config_f.write(config_file)
    print("========================= Finished =========================")
    print("\n")