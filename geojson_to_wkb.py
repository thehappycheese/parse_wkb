from typing import Dict
from struct import pack
from itertools import flat

# Always use little endian form, since apparently this is what shapely uses
ByteOrderChar = str  # Literal[">", "<"]  # 0 = big = >, 1 = little = <
byte_order_char: ByteOrderChar = "<"
byte_order_byte = 1

MapExtraDimensionNames = {
	2: (0, "XY", "2d"),
	3: (1, "XYZ", "3d"),
}


def flatten(items):
	for item in items:
		for sub_item in item:
			yield sub_item


def encode_Point(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"])
	int_geom_type, dimension_names, point_encoder = MapExtraDimensionNames[number_of_dimensions]
	geom_type = 1000 * int_geom_type + MapGeometryTypeNameAndParser["Point"][0]
	return pack(byte_order_char + "bI" + point_encoder, byte_order_byte, geom_type, *geojson["coordinates"])


def encode_LineString(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0])
	number_of_points = len(geojson["coordinates"])
	int_geom_type, dimension_names, point_encoder = MapExtraDimensionNames[number_of_dimensions]
	geom_type = 1000 * int_geom_type + MapGeometryTypeNameAndParser["Point"][0]
	return pack(byte_order_char + "bII" + point_encoder * number_of_points, byte_order_byte, geom_type, *flatten(geojson["coordinates"]))

def encode_Ring(geojson:Dict)

def encode_Polygon(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0][0])
	number_of_rings = len(geojson["coordinates"])
	int_geom_type, dimension_names, point_encoder = MapExtraDimensionNames[number_of_dimensions]
	geom_type = 1000 * int_geom_type + MapGeometryTypeNameAndParser["Point"][0]
	return pack(byte_order_char + "bII" + point_encoder * number_of_points, byte_order_byte, geom_type, *flatten(geojson["coordinates"]))

MapGeometryTypeNameAndParser = {
	"Point":              (1, "coordinates", encode_Point),
	"LineString":         (2, "coordinates", encode_LineString),
	"Polygon":            (3, "coordinates", encode_Polygon),
	"MultiPoint":         (4, "coordinates", encode_MultiPoint),
	"MultiLineString":    (5, "coordinates", encode_MultiLineString),
	"MultiPolygon":       (6, "coordinates", encode_MultiPolygon),
	"Geometrycollection": (7, "geometries", encode_GeometryCollection),
}
