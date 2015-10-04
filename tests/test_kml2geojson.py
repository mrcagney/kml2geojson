import unittest
from copy import copy
import os, shutil
import xml.dom.minidom as md 

from kml2geojson import *


with open('tests/data/example_01/doc.kml') as src:
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

    def test_cli(self):
        pass

        
if __name__ == '__main__':
    unittest.main()
