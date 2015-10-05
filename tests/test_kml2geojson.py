import unittest
from copy import copy
import os, shutil
import xml.dom.minidom as md 
import json

from kml2geojson.kml2geojson import *


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

    def test_build_svg_style(self):
        with open('tests/data/google_sample.kml') as src:
            kml = md.parseString(src.read())  
        style = build_svg_style(kml)
        get = style['#transPurpleLineGreenPoly']
        expect = {
          'stroke': '#ff00ff',
          'stroke-opacity': 0.5,
          'stroke-width': 4.0,
          'fill': '#00ff00',
          'fill-opacity': 0.5,
          }
        self.assertEqual(get, expect)

    def test_build_leaflet_style(self):
        with open('tests/data/google_sample.kml') as src:
            kml = md.parseString(src.read())  
        style = build_leaflet_style(kml)
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
        # Build a list of eligible KML test files, ones that have GeoJSON
        # counterparts
        directory = 'tests/data/'
        files = os.listdir(directory)  # file names in directory
        test_files = []
        for f in files:
            if f.endswith('.kml') and\
              f.replace('.kml', '.geojson') in files:
                test_files.append(f.replace('.kml', ''))

        # For each KML test file and its GeoJSON counterpart, 
        # convert the KML into a single GeoJSON FeatureCollection
        # and compare it to the GeoJSON file
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

    def test_build_layers(self):
        directory = 'tests/data/two_layers/'
        kml_path = os.path.join(directory, 'two_layers.kml')
        with open(kml_path) as src:
            kml = md.parseString(src.read())
        expect_layers = []
        for name in ['bingo', 'bongo']:
            path = os.path.join(directory, name + '.geojson')
            with open(path) as src:
                geo = json.load(src) 
            expect_layers.append({'name': name, 'geojson': geo})

        get_layers = build_layers(kml)
        for i in range(len(get_layers)):
            self.assertEqual(get_layers[i], expect_layers[i])

        
if __name__ == '__main__':
    unittest.main()
