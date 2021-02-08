from __future__ import annotations
import struct
from typing import Any
from typing import Callable
from typing import List
# from typing import Literal
from typing import NewType
from typing import Tuple
from typing import Union

DimensionCount = int  # Literal[2, 3, 4]
DimensionNames = str  # Literal["XY", "XYZ", "XYM", "XYZM"]

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
	# TODO: The first and last point of a linear ring should be the same value. enforce?
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
	(type_name, dimension_count, extra_dimension_names, parser), wkb = parse_GeometryType(wkb, byte_order)
	geom, wkb = parser(wkb, byte_order, dimension_count)
	return (type_name, extra_dimension_names, geom), wkb


def parse_GeometryCollection(wkb: bytearray, byte_order: ByteOrderChar, dimension_count: DimensionCount) -> ([Geometry], bytearray):
	num_geometries, wkb = parse_UInt32(wkb, byte_order)
	return multi_parse(wkb, byte_order, dimension_count, parse_Geometry, num_geometries)


def parse_ByteOrder(wkb: bytearray) -> (ByteOrderChar, bytearray):
	byte, wkb = parse_Byte(wkb)
	if byte == 0:
		return ">", wkb
	elif byte == 1:
		return "<", wkb
	raise WKBParseException(f"Invalid byte order {byte}")


MapExtraDimensionNames: {int: (DimensionCount, DimensionNames)} = {
	0: (2, "XY"),
	1: (3, "XYZ"),
	2: (3, "XYM"),
	3: (4, "XYZM")
}

MapGeometryTypeNameAndParser = {
	1:  ("POINT", parse_Point),
	2:  ("LINESTRING", parse_LineString),
	3:  ("POLYGON", parse_Polygon),
	4:  ("MULTIPOINT", parse_MultiPoint),
	5:  ("MULTILINESTRING", parse_MultiLineString),
	6:  ("MULTIPOLYGON", parse_MultiPolygon),
	7:  ("GEOMETRYCOLLECTION", parse_GeometryCollection),
	15: ("POLYHEDRALSURFACE", None),
	16: ("TIN", None),
	17: ("TRIANGLE", None),
}


def parse_GeometryType(wkb: bytearray, byte_order: ByteOrderChar) -> ((str, DimensionCount, DimensionNames, Callable), bytearray):
	geom_type_integer, wkb = parse_UInt32(wkb, byte_order)
	type_name, parser = MapGeometryTypeNameAndParser.get(geom_type_integer % 1000, (None, None))
	if type_name is None:
		raise WKBParseException(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer % 1000} not in WKBGeometryTypeInfo.keys()")
	
	if parser is None:
		raise WKBParseException(f"Parser is not implemented for {type_name}")
	
	dimension_count, extra_dimension_names = MapExtraDimensionNames.get(geom_type_integer // 1000, (None, None))
	if dimension_count is None:
		raise WKBParseException(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer // 1000} not in WKBDimensionSets.keys()")
	
	return (type_name, dimension_count, extra_dimension_names, parser), wkb


def parse_wkb(wkb: bytearray) -> []:
	result, wkb = parse_Geometry(wkb, None, None)
	return result, wkb


def parse_MYSQL_internal_SRID(wkb: bytearray, byte_order: ByteOrderChar = "<") -> (UInt32, bytearray):
	# TODO: according to the documentation, MySQL stores geometry always in little endian order. Therefore I assume that this is how they store the SRID. Test this is the case?
	# reads in little endian "<" by default
	return struct.unpack(byte_order[0] + " I", wkb[:4])[0], wkb[4:]


def parse_MYSQL_internal(wkb: bytearray):
	SRID, wkb = parse_MYSQL_internal_SRID(wkb)
	result, wkb = parse_wkb(wkb)
	return (("SRID=", SRID), result), wkb


class WKBParseException(Exception):
	def __init__(self, msg):
		super().__init__(msg)
