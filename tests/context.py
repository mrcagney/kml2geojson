import os
import sys
from pathlib import Path 

sys.path.insert(0, os.path.abspath('..'))

import kml2geojson


DATA_DIR = Path('tests/data')