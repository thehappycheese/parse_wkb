from typing import Tuple

# TODO: only XY points are exported. The GeoJSON spec optionally accepts a Z coordinate.

def to_geojson_feature(parsed_geometry:Tuple, properties:{str:str}):

def to_geojson_Geometry(parsed_geometry:Tuple):
	return

def coordinate_from_parsed_point(point):
	point[2][:2]

def to_geojson_Point(parsed_geometry:Tuple):
	return {"type":"Point", "coordinates":[*parsed_geometry[2][:2]]}


def to_geojson_LineString(parsed_geometry:Tuple):
	return {"type": "LineString", "coordinates": [[*item[:2]] for item in parsed_geometry[2]]}

def to_geojson_Polygon(parsed_geometry:Tuple):
	return {"type": "Polygon", "coordinates": [*parsed_geometry[2]]}

MapGeometryNameToParser = {
	"POINT":to_geojson_Point,
	"LINESTRING":to_geojson_LineString,
	"POLYGON":to_geojson_Polygon,
	"MULTIPOINT":to_geojson_MultiPoint),
	"MULTILINESTRING":to_geojson_MultiLineString),
	"MULTIPOLYGON":to_geojson_MultiPolygon),
	"GEOMETRYCOLLECTION":to_geojson_GeometryCollection),
}