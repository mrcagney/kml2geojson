Introduction
************
kml2geojson is a Python 3.6+ package to convert KML files to GeoJSON files.
Most of its code is a translation into Python of the Node.js package `togeojson <https://github.com/mapbox/togeojson>`_, but kml2geojson also adds the following features.

- Preserve KML object styling, such as color and opacity
- Optionally create a style dictionary cataloging all the KML styles used
- Optionally create several GeoJSON FeatureCollections, one for each KML folder present


Installation
=============
Create a Python 3.6+ virtual environment and run ``poetry add kml2geojson``.


Usage
======
At the command line type ``k2g --help`` for instructions.
You can also use kml2geojson as a library.


Documentation
==============
In the ``docs`` directory and published at `mrcagney.github.io/kml2geojson_docs <https://mrcagney.github.io/kml2geojson_docs/>`_.


Notes
========
- Development status is Alpha.
- This project uses semantic versioning.


Authors
========
- Alex Raichev (2015-10-03), maintainer

