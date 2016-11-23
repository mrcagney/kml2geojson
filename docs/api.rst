API
===

The kml2geojson package contains two independent modules, ``main`` and ``cli``, the latter of which is a command line interface for the package.


kml2geojson.main module
-------------------------------
.. automodule:: kml2geojson.main
    :members:
    :undoc-members:
    :show-inheritance:


kml2geojson.cli module
-------------------------------
Sphinx auto-documentation does not work on this module, because all the functions inside are decorated by Click decorators, which don't play nicely with Sphinx. So use the command line to access the documentation for k2g, the command line interface for kml2geojson::

    ~> k2g --help
    Usage: k2g [OPTIONS] KML_PATH OUTPUT_DIR

    Given a path to a KML file, convert it to a a GeoJSON FeatureCollection
    file and save it to the given output directory.

    If ``--separate_folders``, then create several GeoJSON files, one for each
    folder in the KML file that contains geodata or that has a descendant node
    that contains geodata. Warning: this can produce GeoJSON files with the
    same geodata in case the KML file has nested folders with geodata.

    If ``--style_type`` is specified, then also build a JSON style file of the
    given style type and save it to the output directory under the file name
    given by ``--style_filename``.

    Options:
      -f, --separate-folders
      -st, --style-type [svg|leaflet]
      -sf, --style-filename TEXT
      --help                          Show this message and exit.
