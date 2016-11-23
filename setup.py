from distutils.core import setup

setup(
    name='kml2geojson',
    version='4.0.0',
    author='Alexander Raichev',
    packages=['kml2geojson', 'tests'],
    url='https://github.com/araichev/kml2geojson',
    license='LICENSE',
    description='A Python 3.4 tool kit for converting KML files to GeoJSON files',
    long_description=open('README.rst').read(),
    install_requires=[
        'click>=6.6',
    ],
    entry_points = {
      'console_scripts': ['k2g=kml2geojson.cli:k2g'],
      },
    )

