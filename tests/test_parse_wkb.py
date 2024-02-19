import pytest
import json
from parse_wkb import (
    wkb_to_abstract,
    wkb_to_geojson,
    wkb_to_wkt,
    geojson_to_wkb,
)
import shapely
from shapely.geometry import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    LinearRing,
    GeometryCollection
)

# Define test data for geometries
test_data = [
    ("POINT", Point(1, 2)),
    ("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)])),
    ("LINESTRING", LineString([Point(1, 2), Point(1, 2)])),
    ("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])])),
    ("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])),
    ("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])])),
    ("GEOMETRYCOLLECTION", GeometryCollection([Point(4.0, 6.0),LineString([[4.0, 6.0], [7.0, 10.0]])]))
]

@pytest.mark.parametrize("typ, shape", test_data)
def test_wkb_to_abstract(typ, shape):
    wkb = shape.wkb
    parsed = wkb_to_abstract(wkb)
    assert parsed[0] == "LEnd"  
    assert parsed[1][0].upper() == typ.upper()

@pytest.mark.parametrize("typ, shape", test_data)
def test_wkb_to_geojson(typ, shape):
    wkb = shape.wkb
    geojson = wkb_to_geojson(wkb)
    assert geojson['type'].upper() == typ.upper()
    assert shape == shapely.from_geojson(json.dumps(geojson))
    

@pytest.mark.parametrize("typ, shape", test_data)
def test_wkb_to_wkt(typ, shape):
    wkb = shape.wkb
    wkt = wkb_to_wkt(wkb)
    assert wkt.startswith(typ)
    assert shape == shapely.from_wkt(wkt)

@pytest.mark.parametrize("typ, shape", test_data)
def test_geojson_to_wkb(typ, shape):
    # Convert Shapely geometry to GeoJSON
    geojson_dict = shapely.geometry.mapping(shape)
    # Use the function to convert GeoJSON back to WKB
    wkb_from_geojson = geojson_to_wkb(geojson_dict)
    # Convert WKB back to a Shapely object for comparison
    shape_from_wkb = shapely.from_wkb(wkb_from_geojson)
    # Assert that the original shape and the one derived from WKB are equal
    assert shape == shape_from_wkb, f"Mismatch in geometry for type {typ}"
