from distutils.core import setup

dependencies = ['click']
setup(
    name='kml2geojson',
    version='0.1',
    author='Alexander Raichev',
    author_email='alex@raichev.net',
    packages=['kml2geojson', 'tests'],
    url='https://github.com/araichev/kml2geojson',
    license='LICENSE',
    description='A Python 3.4 tool kit for converting KML files to GeoJSON files',
    long_description=open('README.rst').read(),
    install_requires=dependencies,
    entry_points = {
      'console_scripts': ['kml2geojson=kml2geojson.cli:main'],
      },
    )

