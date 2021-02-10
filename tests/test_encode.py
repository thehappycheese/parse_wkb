from shapely.geometry import shape, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon, LinearRing

from geojson_to_wkb import geojson_to_wkb

multigeometry_wkb = b"\x01\x07\x00\x00\x00\x02\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x40\x00\x00\x00\x00\x00\x00\x18\x40\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x40\x00\x00\x00\x00\x00\x00\x18\x40\x00\x00\x00\x00\x00\x00\x1c\x40\x00\x00\x00\x00\x00\x00\x24\x40"
multigeometry_geojson = {"type": "MultiLineString", "coordinates": [[[10, 10], [20, 20], [10, 40]], [[40, 40], [30, 30], [40, 20], [30, 10]]]}


def reference(typ, sshape):
	print("\r\n========= REFERENCE -- " + typ + "==========")
	print(sshape.__geo_interface__)


def test(typ, geojson):
	print("\r\n========= COMP " + typ + "==========")
	my_wkb = geojson_to_wkb(geojson)
	print(my_wkb)
	shapely_wkb = shape(geojson).wkb
	print(shapely_wkb)
	print(my_wkb == shapely_wkb)


reference("POINT", Point(1, 2))
reference("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]))
reference("LINESTRING", LineString([Point(1, 2), Point(1, 2)]))
reference("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]))
reference("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]))
reference("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]))

test("POINT", Point(1, 2).__geo_interface__)
test("MULTIPOINT", MultiPoint([Point(1, 2), Point(1, 2)]).__geo_interface__)
test("LINESTRING", LineString([Point(1, 2), Point(1, 2)]).__geo_interface__)
test("MULTILINESTRING", MultiLineString([LineString([Point(1, 2), Point(1, 2)]), LineString([Point(1, 2), Point(1, 2)])]).__geo_interface__)
test("POLYGON", Polygon(LinearRing([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)]), [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]).__geo_interface__)
test("MULTIPOLYGON", MultiPolygon([Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])]), Polygon([Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0), Point(0, 0)], [LinearRing([Point(0.1, 0.1), Point(0.1, 0.9), Point(0.9, 0.9), Point(0.9, 0.1), Point(0.1, 0.1)])])]).__geo_interface__)
test("MULTIGEOMETRY", multigeometry_geojson)
