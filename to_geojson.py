from typing import Tuple


# TODO: only XY points are exported even though The GeoJSON spec optionally accepts a Z coordinate.

def coordinate_from_parsed_point(point):
	if len(point[1]) > 2 and point[1][2] == "Z":
		return [*point[2][:3]]
	return [*point[2][:2]]


def to_geojson_Point(parsed_geometry: Tuple):
	return {"type": "Point", "coordinates": coordinate_from_parsed_point(parsed_geometry)}


def to_geojson_LineString(parsed_geometry: Tuple):
	return {"type": "LineString", "coordinates": [*map(list, parsed_geometry[2])]}


def to_geojson_Polygon(parsed_geometry: Tuple):
	return {"type": "Polygon", "coordinates": [[*map(list, item)] for item in parsed_geometry[2]]}


def to_geojson_MultiPoint(parsed_geometry: Tuple):
	return {"type": "MultiPoint", "coordinates": [*map(coordinate_from_parsed_point, parsed_geometry[2])]}


def to_geojson_MultiLineString(parsed_geometry: Tuple):
	return {"type": "MultiLineString", "coordinates": [[*map(list, item[2])] for item in parsed_geometry[2]]}


def to_geojson_MultiPolygon(parsed_geometry: Tuple):
	return {"type": "MultiPolygon", "coordinates": [[[*map(list, item)] for item in polygon[2]] for polygon in parsed_geometry[2]]}


def to_geojson_GeometryCollection(parsed_geometry: Tuple):
	return {"type": "GeometryCollection", "geometries": [*map(to_geojson_Geometry, parsed_geometry[2])]}


def to_geojson_Geometry(parsed_geometry: Tuple):
	return MapGeometryNameToParser[parsed_geometry[0]](parsed_geometry)


MapGeometryNameToParser = {
	"POINT":              to_geojson_Point,
	"LINESTRING":         to_geojson_LineString,
	"POLYGON":            to_geojson_Polygon,
	"MULTIPOINT":         to_geojson_MultiPoint,
	"MULTILINESTRING":    to_geojson_MultiLineString,
	"MULTIPOLYGON":       to_geojson_MultiPolygon,
	"GEOMETRYCOLLECTION": to_geojson_GeometryCollection,
}
