from wkb_to_abstract import wkb_to_abstract
from wkb_to_geojson import wkb_to_geojson
from wkb_to_wkt import wkb_to_wkt
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon, LinearRing

# shapely does not support multigeometries so we have to supply some test data we found online.
multigeometry = b"\x01\x07\x00\x00\x00\x02\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x40\x00\x00\x00\x00\x00\x00\x18\x40\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x40\x00\x00\x00\x00\x00\x00\x18\x40\x00\x00\x00\x00\x00\x00\x1c\x40\x00\x00\x00\x00\x00\x00\x24\x40"


def reference(typ, item):
	print("\r\n========= REFERENCE -- " + typ + "==========")
	print(item.wkt)
	print(item.__geo_interface__)


def test(typ, item):
	print("\r\n========= ABSTRACT " + typ + "==========")
	parsed = wkb_to_abstract(item)[0]
	print(parsed)


def test2(typ, item):
	print("\r\n========= WKB TO GEOJSON -- " + typ + "==========")
	parsed = wkb_to_geojson(item)[0]
	print(parsed)


def test3(typ, item):
	print("\r\n========= WKB TO WKT -- " + typ + "==========")
	parsed = wkb_to_wkt(item)[0]
	print(parsed)


# test("POINT", b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")
# test("MULTIPOINT", b"\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")
# test("MULTILINESTRING", b"\x01\x05\x00\x00\x00\x02\x00\x00\x00\x01\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40")

# tests using shapely Geometry.wkb

reference("POINT", Point(1, 2))
reference("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]))
reference("LINESTRING", LineString([Point(1, 2), Point(1, 2)]))
reference("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]))
reference("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]))
reference("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]))

test("POINT", Point(1, 2).wkb)
test("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).wkb)
test("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).wkb)
test("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).wkb)
test("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).wkb)
test("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).wkb)
test("MULTIGEOMETRY", multigeometry)

test2("POINT", Point(1, 2).wkb)
test2("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).wkb)
test2("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).wkb)
test2("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).wkb)
test2("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).wkb)
test2("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).wkb)
test2("MULTIGEOMETRY", multigeometry)

test3("POINT", Point(1, 2).wkb)
test3("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).wkb)
test3("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).wkb)
test3("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).wkb)
test3("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).wkb)
test3("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).wkb)
test3("MULTIGEOMETRY", multigeometry)
