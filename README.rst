kml2geojson
============
A Python 3.4 command-line program to convert KML files to GeoJSON.
Much of the code is a translation into Python of the KML converter in the Node.js package
`togeojson <https://github.com/mapbox/togeojson>`_.
The added features of ``kml2geojson``, are

- the ability to create several GeoJSON files of FeatureCollections, one for each KML folder 
- one JSON file containing the KML styles


Installation
-------------
``pip install kml2geojson``


Usage
------
At the command line type ``kml2geojson --help`` for instructions.


Notes
-------
- Development status: Alpha
- This project uses semantic versioning (major.minor.patch), 
where each breaking feature or API change is considered a major release.
So the version code reflects the project's change history, rather than its development status.
In particular, a high major version number, does not imply a mature development status. 


Authors
---------
- Alex Raichev (2015-10-03)


