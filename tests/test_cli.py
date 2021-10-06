import shutil

from click.testing import CliRunner

from .context import DATA_DIR
from kml2geojson.cli import *


runner = CliRunner()

def rm_paths(*paths):
    """
    Delete the given file paths/directory paths, if they exists.
    """
    for p in paths:
        p = pl.Path(p)
        if p.exists():
            if p.is_file():
                p.unlink()
            else:
                shutil.rmtree(str(p))

def test_k2g():
    kml_path = DATA_DIR / "two_layers" / "two_layers.kml"
    out_dir = DATA_DIR / "tmp"
    rm_paths(out_dir)

    result = runner.invoke(
        k2g,
        [
            str(kml_path),
            str(out_dir),
            "--style-type=svg",
            "-sf=wakawakawaka.json",
            "--separate-folders",
        ]
    )
    assert result.exit_code == 0

    rm_paths(out_dir)
