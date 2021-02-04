import struct
from typing import Any
from typing import Callable
from typing import List
# from typing import Literal
from typing import NewType
from typing import Tuple
from typing import Union

# This module was built using the "OpenGIS® Implementation Standard for Geographic information - Simple feature access - Part 1: Common architecture"
# From 06-103r4_Implementation_Specification_for_Geographic_Information_-_Simple_feature_access_-_Part_1_Common_Architecture_v1.2.1.pdf
# However it only supports the feature types that MYSQL supports (Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, and GeometryCollection)
# MYSQL doesnt even say it supports Z and M parts, but we support them here anyway.
# POSTGIS has an extension called EWKB which is currently a superset of WKB, but their website warns that they don't care much about retaining this compatibility.
# internally MYSQL prepends 4 bytes to the beginning of each fragment of WKB (each feature??) which represents the SRID. POSTGIS does something similar

DimensionCount = int  # Literal[2, 3, 4]
DimensionNames = str  # Literal["", "Z", "M", "ZM"]
WKBDimensionSets: {int: (DimensionCount, DimensionNames)} = {
	0: (2, ""),
	1: (3, "Z"),
	2: (3, "M"),
	3: (4, "ZM")
}

ByteOrderChar = str  # Literal[">", "<"]  # 0 = big = >, 1 = little = <

Byte = int  # char
UInt32 = int  # 4 byte int
Double = float  # 8 byte float

PointXY = Tuple[Double, Double]
PointXYZ = Tuple[Double, Double, Double]
PointXYM = Tuple[Double, Double, Double]
PointXYZM = Tuple[Double, Double, Double, Double]
Point = Union[PointXY, PointXYZ, PointXYM, PointXYZM]

LinearRing = List[Point]
LineString = List[Point]
Polygon = List[LinearRing]

Geometry = (str, Union[Point, LineString, Polygon, List[Point], List[LineString]])

T = NewType("T", Any)


def multi_parse(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount, func: Callable[[bytearray, ByteOrderChar, DimensionCount], Tuple[T, bytearray]], repeat_count: int) -> ((T, ...), bytearray):
	# oh Haskell, how I miss thee, thine curried functions, thine folds. Here I wallow in constant reinvention, apart from thine warm aura of glorious composition.
	result = []
	for _ in range(repeat_count):
		item_result, wkb = func(wkb, byte_order, dimension_count)
		result.append(item_result)
	return tuple(result), wkb


def parse_Byte(wkb: bytearray) -> (Byte, bytearray):
	return wkb[0], wkb[1:]


def parse_UInt32(wkb: bytearray, byte_order: ByteOrderChar) -> (UInt32, bytearray):
	return struct.unpack(byte_order[0] + " I", wkb[:4])[0], wkb[4:]


def parse_Double(wkb: bytearray, byte_order: ByteOrderChar) -> (Double, bytearray):
	# hopefully parses 8 byte IEEE 754 Double
	return struct.unpack(byte_order[0] + " d", wkb[:8])[0], wkb[8:]


def parse_Point(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> (Point, bytearray):
	return tuple(item[0] for item in struct.iter_unpack(byte_order[0] + " d", wkb[:8 * dimension_count])), wkb[8 * dimension_count:]


def parse_LinearRing(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> (LinearRing, bytearray):
	num_points, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Point, num_points)


def parse_LineString(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> (LineString, bytearray):
	num_points, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Point, num_points)


def parse_Polygon(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> (Polygon, bytearray):
	num_rings, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_LinearRing, num_rings)


def parse_MultiPoint(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> ([Point], bytearray):
	num_points, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Geometry, num_points)


def parse_MultiLineString(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> ([LineString], bytearray):
	num_strings, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Geometry, num_strings)


def parse_MultiPolygon(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> ([Polygon], bytearray):
	num_polygons, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Geometry, num_polygons)


def parse_Geometry(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> (Geometry, bytearray):
	# Apparently all features in a GeometryCollection can have their own byte-order and dimension set
	byte_order, wkb = parse_ByteOrder(wkb)
	(type_name, dimension_count, dimension_names, parser), wkb = parse_GeometryType(wkb, byte_order)
	geom, wkb = parser(wkb, byte_order, dimension_count)
	return (' '.join((type_name, dimension_names)), geom), wkb


def parse_GeometryCollection(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> ([LineString], bytearray):
	num_geometries, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Geometry, num_geometries)


def parse_ByteOrder(wkb: bytearray) -> (ByteOrderChar, bytearray):
	byte, wkb = parse_Byte(wkb)
	if byte == 0:
		return ">", wkb
	elif byte == 1:
		return "<", wkb
	raise WKBParseException(f"Invalid byte order {byte}")


def parse_GeometryType(wkb: bytearray, byte_order: ByteOrderChar) -> ((str, DimensionCount, DimensionNames, Callable), bytearray):
	"""
	returns type number (tens and units)
	dimention set (divide by 1000)
	"""
	geom_type_integer, wkb = parse_UInt32(wkb, byte_order)
	try:
		type_name, parser = WKBGeometryTypeInfo[geom_type_integer % 1000]
	except:
		raise WKBParseException(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer % 1000} not in WKBGeometryTypeInfo.keys()")
	
	if parser is None:
		raise WKBParseException(f"Parser is not implemented for {type_name}")
	
	try:
		dimension_count, dimension_names = WKBDimensionSets[geom_type_integer // 1000]
	except:
		raise WKBParseException(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer // 1000} not in WKBDimensionSets.keys()")
	
	return (type_name, dimension_count, dimension_names, parser), wkb


WKBGeometryTypeInfo = {
	1: ("Point", parse_Point),
	2: ("LineString", parse_LineString),
	3: ("Polygon", parse_Polygon),
	4: ("MultiPoint", parse_MultiPoint),
	5: ("MultiLineString", parse_MultiLineString),
	6: ("MultiPolygon", parse_MultiPolygon),
	7: ("GeometryCollection", parse_GeometryCollection),
	15: ("PolyhedralSurface", None),
	16: ("TIN", None),
	17: ("Triangle", None),
}


def parse_wkb(wkb: bytearray) -> []:
	result = []
	while wkb:
		byte_order, wkb = parse_ByteOrder(wkb)
		(type_name, dimension_count, dimension_names, parser), wkb = parse_GeometryType(wkb, byte_order)
		geom, wkb = parser(wkb, byte_order, dimension_count)
		result.append((' '.join((type_name, dimension_names)), geom))
	return result


def parse_MYSQL_internal_SRID(wkb: bytearray, byte_order: ByteOrderChar = "<") -> (UInt32, bytearray):
	# reads in little endian "<" by default
	return struct.unpack(byte_order[0] + " I", wkb[:4])[0], wkb[4:]


def parse_MYSQL_internal(wkb: bytearray):
	# TODO: according to the documentation, MySQL stores geometry always in little endian order. Therefore I assume that this is how they store the SRID
	SRID, wkb = parse_MYSQL_internal_SRID(wkb)
	return (("SRID=", SRID), parse_wkb(wkb))


class WKBParseException(Exception):
	def __init__(self, msg):
		super().__init__(msg)
