import xml.dom.minidom as md
import json

from .context import kml2geojson, DATA_DIR
from kml2geojson import *


def test_coords1():
    v = " -112.2,36.0,2357 "
    get = coords1(v)
    expect = [-112.2, 36.0, 2357]
    assert get == expect


def test_coords():
    v = """
     -112.0,36.1,0
     -113.0,36.0,0 
     """
    get = coords(v)
    expect = [[-112.0, 36.1, 0], [-113.0, 36.0, 0]]
    assert get == expect


def test_build_rgb_and_opactity():
    get = build_rgb_and_opacity("ee001122")
    expect = ("#221100", 0.93)
    assert get == expect


def test_build_svg_style():
    path = DATA_DIR / "google_sample.kml"
    with path.open() as src:
        kml = md.parseString(src.read())
    style = build_svg_style(kml)
    get = style["#transPurpleLineGreenPoly"]
    expect = {
        "stroke": "#ff00ff",
        "stroke-opacity": 0.5,
        "stroke-width": 4.0,
        "fill": "#00ff00",
        "fill-opacity": 0.5,
    }
    assert get == expect


def test_build_leaflet_style():
    path = DATA_DIR / "google_sample.kml"
    with path.open() as src:
        kml = md.parseString(src.read())
    style = build_leaflet_style(kml)
    get = style["#transPurpleLineGreenPoly"]
    expect = {
        "color": "#ff00ff",
        "fillColor": "#00ff00",
        "fillOpacity": 0.5,
        "opacity": 0.5,
        "weight": 4.0,
    }
    assert get == expect


def test_build_feature_collection():
    # Collect the test files, i.e. the KML files and their GeoJSON counterparts
    root = DATA_DIR
    stems = set(p.stem for p in root.glob("*.kml")) & set(
        p.stem for p in root.glob("*.geojson")
    )

    # For test file convert it into a single GeoJSON FeatureCollection
    # and compare the result to the corresponding GeoJSON file
    for s in stems:
        print(s)
        k_path = root / (s + ".kml")
        g_path = root / (s + ".geojson")
        with k_path.open() as src:
            kml = md.parseString(src.read())
        with g_path.open() as src:
            geojson = json.load(src)
        get = build_feature_collection(kml)
        expect = geojson
        assert get == expect


def test_disambiguate():
    names = ["bingo", "bingo1", "bongo", "bingo", "bro", "bongo"]
    get = disambiguate(names)
    expect = ["bingo", "bingo1", "bongo", "bingo11", "bro", "bongo1"]
    assert get == expect


def test_to_filename():
    name = "%   A d\nbla'{-+)(ç?"
    get = to_filename(name)
    expect = "A_dbla-ç"
    assert get == expect


def test_build_layers():
    k_path = DATA_DIR / "two_layers" / "two_layers.kml"
    with k_path.open() as src:
        kml = md.parseString(src.read())
    expect_layers = []
    for name in ["Bingo", "Bingo1"]:
        g_path = k_path.parent / (name + ".geojson")
        with g_path.open() as src:
            geo = json.load(src)
        expect_layers.append(geo)

    get_layers = build_layers(kml)
    for i in range(len(get_layers)):
        assert get_layers[i] == expect_layers[i]


def test_convert():
    kml_path = DATA_DIR / "two_layers" / "two_layers.kml"

    get_list = convert(kml_path, style_type="svg", separate_folders=True)
    expect_list = []
    for name in ["style.json", "Bingo.geojson", "Bingo1.geojson"]:
        g_path = kml_path.parent / name
        with g_path.open() as src:
            expect_list.append(json.load(src))

    for i in range(len(get_list)):
        assert get_list[i] == expect_list[i]

    # Test without separating folders
    get_list = convert(
        kml_path,
        style_type="svg",
        separate_folders=False,
        feature_collection_name="two_layers",
    )
    expect_list = [expect_list[0]] + [
        {
            "name": "two_layers",
            "type": "FeatureCollection",
            "features": expect_list[1]["features"] + expect_list[2]["features"],
        }
    ]
    for i in range(len(get_list)):
        assert get_list[i] == expect_list[i]

    # Test without separating folders and without a style file
    get_list = convert(
        kml_path, separate_folders=False, feature_collection_name="two_layers"
    )
    for i in range(len(get_list)):
        assert get_list[i] == expect_list[i + 1]

    # Test with file object
    with kml_path.open() as kml_src:
        get_list = convert(kml_src, style_type="svg", separate_folders=True)
        expect_list = []
        for name in ["style.json", "Bingo.geojson", "Bingo1.geojson"]:
            g_path = kml_path.parent / name
            with g_path.open() as src:
                expect_list.append(json.load(src))

        for i in range(len(get_list)):
            assert get_list[i] == expect_list[i]
