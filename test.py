from parse_wkb import parse_wkb
from wkb_to_geojson import wkb_to_GeoJSON
from to_geojson import to_geojson_Geometry
from shapely.geometry import Point, MultiPoint, LineString,MultiLineString, Polygon, MultiPolygon, LinearRing


def test(typ, item):
	print("\r\n========= " + typ + "==========")
	parsed = parse_wkb(item)[0]
	print(parsed)
	geojson = to_geojson_Geometry(parsed)
	print(geojson)


def test2(typ, item):
	print("\r\n========= TEST 2 -- " + typ + "==========")
	parsed = wkb_to_GeoJSON(item)[0]
	print(parsed)

# test("POINT", b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")
# test("MULTIPOINT", b"\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")
# test("MULTILINESTRING", b"\x01\x05\x00\x00\x00\x02\x00\x00\x00\x01\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")

# tests using shapely Geometry.wkb

test("POINT", Point(1, 2).wkb)
test("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).wkb)

test("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).wkb)
test("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).wkb)

test("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).wkb)
test("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]),Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).wkb)

test2("POINT", Point(1, 2).wkb)
test2("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).wkb)
test2("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).wkb)
test2("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).wkb)
test2("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).wkb)
test2("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]),Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).wkb)