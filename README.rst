kml2geojson
************
.. image:: https://github.com/mrcagney/kml2geojson/actions/workflows/run_tests.yml/badge.svg
    :target: https://github.com/mrcagney/kml2geojson
    
kml2geojson is a Python 3.8+ package to convert KML files to GeoJSON files.
Most of its code is a translation into Python of the Node.js package `togeojson <https://github.com/mapbox/togeojson>`_, but kml2geojson also adds the following features.

- Preserve KML object styling, such as color and opacity
- Optionally create a style dictionary cataloging all the KML styles used
- Optionally create several GeoJSON FeatureCollections, one for each KML folder present


Installation
=============
Create a Python 3.8+ virtual environment and run ``poetry add kml2geojson``.


Usage
======
Use as a library or from the command line.
For instructions on the latter, type ``k2g --help``.


Documentation
==============
In the ``docs`` directory and published at `mrcagney.github.io/kml2geojson_docs <https://mrcagney.github.io/kml2geojson_docs/>`_.


Notes
========
- Development status is Alpha.
- This project uses semantic versioning.
- Thanks to `MRCagney <https://mrcagney.com>`_ for funding this project.


Authors
========
- Alex Raichev (2015-10-03), maintainer


Contributing
===================
If you want to help develop this project, here is some background reading.

- The `KML reference <https://developers.google.com/kml/documentation/kmlreference?hl=en>`_ 
- Python's `Minimal DOM implementation <https://docs.python.org/3.4/library/xml.dom.minidom.html>`_, which this project uses to parse KML files


Changes
========

5.1.0, 2022-04-29
-----------------
- Extended ``convert()`` to accept a KML file object.
- Added type hints.
- Updated dependencies and removed version caps.
- Dropped support for Python versions less than 3.8.
- Switched from Travis CI to Github Actions.


5.0.1, 2021-10-11
-----------------
- Re-included the MIT License file and added more metadata to the file ``pyproject.toml`` for a more informative listing on PyPi.


5.0.0, 2021-10-07
-----------------
- Upgraded to Python 3.9 and dropped support for Python versions < 3.6.
- Switched to Poetry.
- Breaking change: refactored the ``convert`` function to return dictionaries instead of files.
- Moved docs from Rawgit to Github Pages.


4.0.2, 2017-04-26
-------------------
- Fixed the bug where ``setup.py`` could not find the license file.


4.0.1, 2017-04-22
-------------------
- Moved the name of a FeatureCollection into a 'name' attribute, because `RFC 7946 says that a GeoJSON FetaureCollection must not have a 'properties' attribute <https://tools.ietf.org/html/rfc7946#section-7>`_
- Stripped leanding and trailing whitespace from text content to avoid cluttered or blank name and description attribute values
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
------------------
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


