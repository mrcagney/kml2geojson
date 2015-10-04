import unittest
from copy import copy
import os, shutil
import xml.dom.minidom as md 

from kml2geojson import *


with open('tests/data/doc.kml') as src:
    DOC_01 = md.parseString(src.read())

class TestKml2Geojson(unittest.TestCase):

    def test_coords1(self):
        v = ' -112.2,36.0,2357 '
        get = coords1(v)
        expect = [-112.2, 36.0, 2357]
        self.assertEqual(get, expect)

    def test_coords(self):
        v = '''
         -112.0,36.1,0
         -113.0,36.0,0 
         '''
        get = coords(v)
        expect = [[-112.0, 36.1, 0], [-113.0, 36.0, 0]]
        self.assertEqual(get, expect)

    def test_build_rgb_and_opactity(self):
        get = build_rgb_and_opacity('ee001122') 
        expect = ('#221100', 0.93)
        self.assertEqual(get, expect)

    def test_build_leaflet_style(self):
        style = build_leaflet_style(DOC_01)
        get = style['#transPurpleLineGreenPoly']
        expect = {
          'color': '#ff00ff',
          'fillColor': '#00ff00',
          'fillOpacity': 0.5,
          'opacity': 0.5,
          'weight': 4.0,
          }
        self.assertEqual(get, expect)

    def test_build_feature_collection(self):
        directory = 'tests/data/'
        files = os.listdir(directory)  # file names
        test_files = [
          'style',
          'inline_style',
          'style_url',
          'literal_color',
          'cdata',
          'nogeomplacemark',  
          'noname',        
          'selfclosing',
          'point',
          'point_id',
          'linestring',
          'polygon',
          'multigeometry',
          'multigeometry_discrete',
          'simple_data',
          'extended_data',
          'multitrack',
          'non_gx_multitrack',
          'blue_hills',
          ]
        # for f in files:
        #     if f.endswith('.kml') and\
        #       f.replace('.kml', '.geojson') in fnames:
        #         test_fnames.append(f.replace('.kml', ''))
        for f in test_files:
            print(f)
            kml_path = os.path.join(directory, f + '.kml')
            geojson_path = os.path.join(directory, f + '.geojson')
            with open(kml_path) as src:
                kml = md.parseString(src.read())
            with open(geojson_path) as src:
                geojson = json.load(src)

            get = build_feature_collection(kml)
            expect = geojson 
            self.assertEqual(get, expect)

    def test_cli(self):
        pass

        
if __name__ == '__main__':
    unittest.main()
