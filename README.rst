kml2geojson
************
.. image:: https://travis-ci.org/araichev/kml2geojson.svg?branch=master
    :target: https://travis-ci.org/araichev/kml2geojson
    
kml2geojson is a Python 3.4+ package to convert KML files to GeoJSON files.
Most of its code is a translation into Python of the Node.js package `togeojson <https://github.com/mapbox/togeojson>`_, but kml2geojson also adds the following features.

- Preserve KML object styling, such as color and opacity
- Optionally write one JSON file cataloging all the KML styles used
- Optionally create several GeoJSON files of FeatureCollections, one for each KML folder 


Installation
=============
``pip install kml2geojson``


Usage
======
At the command line type ``k2g --help`` for instructions.
You can also use kml2geojson as a library.


Documentation
==============
In ``docs`` and on RawGit `here <https://rawgit.com/araichev/kml2geojson/master/docs/_build/singlehtml/index.html>`_.


Notes
========
- Development status: Alpha
- This project uses semantic versioning (major.minor.micro), where each breaking feature or API change is considered a major change


Authors
========
- Alex Raichev (2015-10-03)


Contributing
===================
If you want to help develop this project, here is some background reading.

- The `KML reference <https://developers.google.com/kml/documentation/kmlreference?hl=en>`_ 
- Python's `Minimal DOM implementation <https://docs.python.org/3.4/library/xml.dom.minidom.html>`_, which this project uses to parse KML files


History
========

4.0.2, 2017-04-26
-------------------
- Fixed the bug where ``setup.py`` could not find the license file.


4.0.1, 2017-04-22
-------------------
- Stopped making FeatureCollections with top-level 'properties' attributes, because `RFC 7946 says that's not allowed <https://tools.ietf.org/html/rfc7946#section-7>`_. Moved FeatureCollection names into a top-level 'name' attribute.
- Stripped leading and trailing whitespace from text content to avoid cluttered or blank name and description attribute values
- Switched to pytest for testing


4.0.0, 2016-11-24
-------------------
- Moved command line functionality to separate module
- Renamed some functions


3.0.4, 2015-10-15
-------------------
Disambiguated filenames in ``main()``.


3.0.3, 2015-10-13
-------------------
Improved ``to_filename()`` again.


3.0.2, 2015-10-12
-------------------
Improved ``to_filename()`` and removed the lowercasing.


3.0.1, 2015-10-12
-------------------
Tweaked ``to_filename()`` to lowercase and underscore results. 
Forgot to do that last time.


3.0.0, 2015-10-12
---------------
Changed the output of ``build_layers()`` and moved layer names into the GeoJSON FeatureCollections


2.0.2, 2015-10-12
-------------------
- Replaced underscores with dashes in command line options


2.0.1, 2015-10-12
-------------------
- Set default border style for colored polygons
 

2.0.0, 2015-10-08
------------------
- Added documentation
- Tweaked the command line tool options 


1.0.0, 2015-10-05
------------------
- Changed some names 
- Added lots of tests


0.1.1, 2015-10-03
-------------------
Fixed packaging to find ``README.rst``


0.1.0, 2015-10-03
-----------------
First


