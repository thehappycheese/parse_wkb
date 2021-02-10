from typing import Dict, Sequence
from struct import pack

# Always use little endian form, since apparently this is what shapely uses
ByteOrderChar = str  # Literal[">", "<"]  # 0 = big = >, 1 = little = <
byte_order_char: ByteOrderChar = "<"
byte_order_byte = 1

UNINT32 = byte_order_char + "I"
BYTE_UNINT32 = byte_order_char + "bI"
BYTE_UNINT32_UNINT32 = byte_order_char + "bII"

map_geom_type_thousands_and_point_encoder = {
	2: (0, byte_order_char + "2d"),
	3: (1, byte_order_char + "3d"),
}


# def flatten(items):
# 	for item in items:
# 		for sub_item in item:
# 			yield sub_item

def get_geom_type_and_point_encoder(type_name, number_of_dimensions):
	geom_type_thousands, point_encoder = map_geom_type_thousands_and_point_encoder[number_of_dimensions]
	geom_type_units = map_type_number_depth_and_encoder[type_name][0]
	geom_type = 1000 * geom_type_thousands + geom_type_units
	return geom_type, point_encoder


def len_at_depth(a_list: Sequence, depth):
	while depth > 0:
		a_list = a_list[0]
		depth = depth - 1
	return len(a_list)


def get_number_of_dimensions(geojson):
	while geojson["type"] == "GeometryCollection":
		if len(geojson["geometries"]) > 0:
			geojson = geojson["geometries"][0]
			continue
		return 2
	return len_at_depth(geojson["coordinates"], map_type_number_depth_and_encoder[geojson["type"]][1])


def encode_Point(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"])
	geom_type, point_encoder = get_geom_type_and_point_encoder("Point", number_of_dimensions)
	result = pack(BYTE_UNINT32, byte_order_byte, geom_type)
	return result + pack(point_encoder, *geojson["coordinates"])


def encode_Ring(coordinates: list, point_encoder: str):
	number_of_points = len(coordinates)
	result = pack(UNINT32, number_of_points)
	for item in coordinates:
		result += pack(point_encoder, *item)
	return result


def encode_LineString(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0])
	geom_type, point_encoder = get_geom_type_and_point_encoder("LineString", number_of_dimensions)
	result = pack(BYTE_UNINT32, byte_order_byte, geom_type)
	result += encode_Ring(geojson["coordinates"], point_encoder)
	return result


def encode_Polygon(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0][0])
	geom_type, point_encoder = get_geom_type_and_point_encoder("Polygon", number_of_dimensions)
	
	number_of_rings = len(geojson["coordinates"])
	result = pack(BYTE_UNINT32_UNINT32, byte_order_byte, geom_type, number_of_rings)
	for ring in geojson["coordinates"]:
		result += encode_Ring(ring, point_encoder)
	return result


def encode_MultiPoint(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0])
	number_of_points = len(geojson["coordinates"])
	geom_type, point_encoder = get_geom_type_and_point_encoder("MultiPoint", number_of_dimensions)
	result = pack(BYTE_UNINT32_UNINT32, byte_order_byte, geom_type, number_of_points)
	point_geom_type, point_point_encoder = get_geom_type_and_point_encoder("Point", number_of_dimensions)
	for item in geojson["coordinates"]:
		if number_of_dimensions != len(item):
			raise Exception("MultiPoint shall not contain mixed number of dimensions")
		result += pack(BYTE_UNINT32, byte_order_byte, point_geom_type)
		result += pack(point_encoder, *item)
	return result


def encode_MultiLineString(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0][0])
	number_of_linestrings = len(geojson["coordinates"])
	geom_type, point_encoder = get_geom_type_and_point_encoder("MultiLineString", number_of_dimensions)
	result = pack(BYTE_UNINT32_UNINT32, byte_order_byte, geom_type, number_of_linestrings)
	linestring_geom_type, point_encoder = get_geom_type_and_point_encoder("LineString", number_of_dimensions)
	for linestring in geojson["coordinates"]:
		if not len(linestring[0]) == number_of_dimensions:
			raise Exception("MultiLineString shall not contain mixed number of dimensions")
		result += pack(BYTE_UNINT32, byte_order_byte, linestring_geom_type)
		result += encode_Ring(linestring, point_encoder)
	return result


def encode_MultiPolygon(geojson: Dict):
	number_of_dimensions = len(geojson["coordinates"][0][0][0])
	number_of_polygons = len(geojson["coordinates"])
	geom_type, point_encoder = get_geom_type_and_point_encoder("MultiPolygon", number_of_dimensions)
	result = pack(BYTE_UNINT32_UNINT32, byte_order_byte, geom_type, number_of_polygons)
	polygon_geom_type, point_encoder = get_geom_type_and_point_encoder("Polygon", number_of_dimensions)
	for polygon in geojson["coordinates"]:
		number_of_rings = len(geojson["coordinates"])
		result += pack(BYTE_UNINT32_UNINT32, byte_order_byte, polygon_geom_type, number_of_rings)
		if not len(polygon[0][0]) == number_of_dimensions:
			raise Exception("MultiPolygon shall not contain mixed number of dimensions")
		geom_type, point_encoder = get_geom_type_and_point_encoder("Point", number_of_dimensions)
		for ring in polygon:
			result += encode_Ring(ring, point_encoder)
	return result


def encode_GeometryCollection(geojson: Dict):
	number_of_dimensions = get_number_of_dimensions(geojson)
	number_of_geometries = len(geojson["geometries"])
	geom_type, point_encoder = get_geom_type_and_point_encoder("GeometryCollection", number_of_dimensions)
	result = pack(BYTE_UNINT32_UNINT32, byte_order_byte, geom_type, number_of_geometries)
	for geometry in geojson["geometries"]:
		result += geojson_to_wkb(geometry)
	return result


map_type_number_depth_and_encoder = {
	"Point":              (1, 0, encode_Point),
	"LineString":         (2, 1, encode_LineString),
	"Polygon":            (3, 2, encode_Polygon),
	"MultiPoint":         (4, 1, encode_MultiPoint),
	"MultiLineString":    (5, 2, encode_MultiLineString),
	"MultiPolygon":       (6, 3, encode_MultiPolygon),
	"GeometryCollection": (7, None, encode_GeometryCollection),
}


def geojson_to_wkb(geojson):
	encoder = map_type_number_depth_and_encoder[geojson["type"]][2]
	return encoder(geojson)
