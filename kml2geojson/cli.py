import pathlib as pl
import json

import click

import kml2geojson.main as m


@click.command(short_help="Convert KML to GeoJSON")
@click.argument('kml_path', type=click.Path(exists=True))
@click.argument('output_dir')
@click.option('-st', '--style-type', type=click.Choice(m.STYLE_TYPES),  default=None)
@click.option('-sf', '--style-filename', default='style.json')
@click.option('-f', '--separate-folders', is_flag=True, default=False)
def k2g(kml_path, output_dir, style_type, style_filename, separate_folders):
    """
    Given a path to a KML file, convert it to a a GeoJSON FeatureCollection file and
    save it to the given output directory.

    If ``--separate_folders``, then create several GeoJSON files,
    one for each folder in the KML file that contains geodata or that has a descendant
    node that contains geodata.
    Warning: this can produce GeoJSON files with the same geodata in case the KML file
    has nested folders with geodata.

    If ``--style_type`` is specified, then also build a JSON style file of the given
    style type and save it to the output directory under the file name given by
    ``--style_filename`` which defaults to "style.json".
    """
    style, *layers = m.convert(kml_path, style_type, separate_folders=separate_folders)

    # Create output directory if it doesn't exist
    output_dir = pl.Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    output_dir = output_dir.resolve()

    # Write style file
    path = output_dir / style_filename
    with path.open('w') as tgt:
        json.dump(style, tgt)

    # Create filenames for layers
    stems = m.disambiguate(m.to_filename(layer['name']) for layer in layers)
    filenames = [f"{stem}.geojson" for stem in stems]

    # Write layer files
    for i in range(len(layers)):
        path = output_dir / filenames[i]
        with path.open('w') as tgt:
            json.dump(layers[i], tgt)
