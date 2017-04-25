import click.testing
from click.testing import CliRunner

from .context import kml2geojson, DATA_DIR
from kml2geojson import *
from kml2geojson.cli import *


runner = CliRunner()

def test_convert():
    in_path = DATA_DIR/'two_layers'/'two_layers.kml'
    out_path = DATA_DIR/'tmp'
    rm_paths(out_path)

    result = runner.invoke(k2g, [str(in_path),
      str(out_path), '--separate-folders', '--style-type=svg', 
      '-sf=wakawakawaka.json'])
    assert result.exit_code == 0

    rm_paths(out_path)
