kml2geojson
============
This is a Python 3.4 command-line program to convert KML files to GeoJSON.
Much of the code is a translation into Python of the KML converter in the 
Node.js package `togeojson <https://github.com/mapbox/togeojson>`_.

The added features of ``kml2geojson``, are

- the ability to create several GeoJSON files of FeatureCollections, one for each KML folder 
- one JSON file containing all the KML styles


Installation
-------------
``pip install kml2geojson``


Usage
------
At the command line type ``kml2geojson --help`` for instructions.


Documentation
--------------
In ``docs`` and on RawGit `here <https://rawgit.com/araichev/kml2geojson/master/docs/_build/singlehtml/index.html>`_.


Notes
-------
- Development status: Alpha
- This project uses semantic versioning (major.minor.micro), where each breaking feature or API change is considered a major release.
  So the version code reflects the project's change history, rather than its development status.
  In particular, a high major version number, does not imply a mature development status. 


Background Reading
------------------
If you want to help develop this project, here is some background reading.

- The `KML reference <https://developers.google.com/kml/documentation/kmlreference?hl=en>`_ 
- Python's `Minimal DOM implementation <https://docs.python.org/3.4/library/xml.dom.minidom.html>`_, which this project uses to parse KML files


Authors
---------
- Alex Raichev (2015-10-03)


