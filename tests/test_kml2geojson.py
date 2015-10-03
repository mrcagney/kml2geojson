import unittest
from copy import copy
import os, shutil

from kml2geojson import *


class TestKml2Geojson(unittest.TestCase):
    def test_coord1(self):
        v = ' -112.2,36.0,2357 '
        get = coord1(v)
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

    def test_cli(self):
        pass

        
if __name__ == '__main__':
    unittest.main()
