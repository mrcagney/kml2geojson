Introduction
************

kml2geojson is a Python 3.4+ program to convert KML files to GeoJSON files.

Much of the code is a translation into Python of the Node.js package `togeojson <https://github.com/mapbox/togeojson>`_.
But kml2geojson also adds the following features.

- Preserves KML object styling, such as color and opacity
- Optionally writes one JSON file cataloging all the KML styles used
- Optionally creates several GeoJSON files of FeatureCollections, one for each KML folder 


Installation
=============
``pip install kml2geojson``


Usage
======
At the command line type ``k2g --help`` for instructions.
You can also use kml2geojson as a library.


Notes
========
- Development status: Alpha
- This project uses semantic versioning (major.minor.micro), where each breaking feature or API change is considered a major change


Authors
========
- Alex Raichev (2015-10-03)