import unittest

import click.testing
from click.testing import CliRunner

from kml2geojson import *
from kml2geojson.cli import k2g


PROJECT_ROOT = Path(os.path.abspath(os.path.join(
  os.path.dirname(__file__), '../')))
DATA_DIR = PROJECT_ROOT/'tests'/'data'


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_convert(self):
        in_path = DATA_DIR/'two_layers'/'two_layers.kml'
        out_path = DATA_DIR/'tmp'
        rm_paths(out_path)

        result = self.runner.invoke(k2g, [str(in_path),
          str(out_path), '--separate-folders', '--style-type=svg', 
          '-sf=wakawakawaka.json'])
        self.assertEqual(result.exit_code, 0)

        rm_paths(out_path)
