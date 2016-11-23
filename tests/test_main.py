import unittest
from copy import copy
import os, shutil
import xml.dom.minidom as md 
import json

from kml2geojson.main import *


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
DATA_DIR = PROJECT_ROOT/'tests'/'data'


class TestMain(unittest.TestCase):

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
        path = DATA_DIR/'google_sample.kml'
        with path.open() as src:
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
        path = DATA_DIR/'google_sample.kml'
        with path.open() as src:
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
        # Collect the test files: the KML files that GeoJSON counterparts
        root = DATA_DIR
        stems = set(p.stem for p in root.glob('*.kml')) &\
          set(p.stem for p in root.glob('*.geojson'))

        # For test file convert it into a single GeoJSON FeatureCollection
        # and compare the result to the corresponding GeoJSON file
        for s in stems:
            k_path = root/(s + '.kml')
            g_path = root/(s + '.geojson')
            with k_path.open() as src:
                kml = md.parseString(src.read())
            with g_path.open() as src:
                geojson = json.load(src)
            get = build_feature_collection(kml)
            expect = geojson 
            self.assertEqual(get, expect)

    def test_disambiguate(self):
        names = ['bingo', 'bingo1', 'bongo', 'bingo', 'bro', 'bongo']
        get = disambiguate(names)
        expect = ['bingo', 'bingo1', 'bongo', 'bingo11', 'bro', 'bongo1']
        self.assertEqual(get, expect)

    def test_to_filename(self):
        name = u"%   A d\nbla'{-+\)(ç?"
        get = to_filename(name)
        expect = "A_dbla-ç"
        self.assertEqual(get, expect)

    def test_build_layers(self):
        k_path = DATA_DIR/'two_layers'/'two_layers.kml'
        with k_path.open() as src:
            kml = md.parseString(src.read())
        expect_layers = []
        for name in ['Bingo', 'Bingo1']:
            g_path = k_path.parent/(name + '.geojson')
            with g_path.open() as src:
                geo = json.load(src) 
            expect_layers.append(geo)

        get_layers = build_layers(kml)
        for i in range(len(get_layers)):
            self.assertEqual(get_layers[i], expect_layers[i])

    def test_main(self):
        in_path = DATA_DIR/'two_layers'/'two_layers.kml'
        out_path = DATA_DIR/'tmp'
        rm_paths(out_path)

        convert(in_path, out_path, separate_folders=True, style_type='svg')
        for p in in_path.parent.iterdir():
            if p.suffix == '.kml':
                continue
            gp = out_path/p.name
            with gp.open() as src:
                get = json.load(src)
            with p.open() as src:
                expect = json.load(src)
            self.assertEqual(get, expect)

        rm_paths(out_path)


if __name__ == '__main__':
    unittest.main()
