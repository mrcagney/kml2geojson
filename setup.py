from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='kml2geojson',
    version='4.0.1',
    author='Alexander Raichev',
    url='https://github.com/araichev/kml2geojson',
    license=license,
    description='A Python 3.4 package to convert KML files to GeoJSON files',
    long_description=readme,
    install_requires=[
        'click>=6.6',
    ],
    entry_points = {
        'console_scripts': ['k2g=kml2geojson.cli:k2g'],
    },
    packages=find_packages(exclude=('tests', 'docs')),   
)

