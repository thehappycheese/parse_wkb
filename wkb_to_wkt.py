from __future__ import annotations
from struct import unpack
from typing import Any, Dict
from typing import Callable
from typing import List
# from typing import Literal
from typing import Tuple
from typing import Union

DimensionCount = int  # Literal[2, 3, 4]
DimensionNames = str  # Literal["XY", "XYZ", "XYM", "XYZM"]

ByteOrderChar = str  # Literal[">", "<"]  # 0 = big = >, 1 = little = <

Byte = int  # char
UInt32 = int  # 4 byte int
Double = float  # 8 byte float

Point = List[Double]

LinearRing = List[Point]
LineString = List[Point]
Polygon = List[LinearRing]

# TODO: python 3.8 will have TypedDict but sadly our current target is 3.7
Geometry = Dict[str, Union[str, List[Union[Point, LineString, Polygon, List[Point], List[LineString]]]]]


def multi_parse(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool, func: Callable[[bytearray, str, str, DimensionCount, bool], Tuple[Any, bytearray]], repeat_count: int) -> ((Any, ...), bytearray):
	# oh Haskell, how I miss thee, thine curried functions, thine folds. Here I wallow in constant reinvention, apart from thine warm aura of glorious composition.
	result = []
	for _ in range(repeat_count):
		item_result, wkb = func(wkb, int_parser, point_parser, dimension_count, raw)
		result.append(item_result)
	return result, wkb


def parse_Byte(wkb: bytearray) -> (Byte, bytearray):
	return wkb[0], wkb[1:]


def parse_UInt32(wkb: bytearray, int_parser) -> (UInt32, bytearray):
	return unpack(int_parser, wkb[:4])[0], wkb[4:]


# def parse_Double(wkb: bytearray, int_parser:str, point_parser:str) -> (Double, bytearray):
# 	# hopefully parses 8 byte IEEE 754 Double
# 	return unpack(byte_order[0] + " d", wkb[:8])[0], wkb[8:]


def parse_Point(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> (Point, bytearray):
	return " ".join(map(str, unpack(point_parser, wkb[:8 * dimension_count]))), wkb[8 * dimension_count:]


def parse_LinearRing(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> (LinearRing, bytearray):
	num_points, wkb = parse_UInt32(wkb, int_parser)
	return multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_Point, num_points)


def parse_LineString(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> (LineString, bytearray):
	num_points, wkb = parse_UInt32(wkb, int_parser)
	points, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_Point, num_points)
	return ", ".join(points), wkb


def parse_Polygon(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> (Polygon, bytearray):
	# TODO: The first and last point of a linear ring should be the same value. enforce?
	num_rings, wkb = parse_UInt32(wkb, int_parser)
	rings, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_LinearRing, num_rings)
	return ', '.join(f"({', '.join(item)})" for item in rings), wkb


def parse_MultiPoint(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> ([Point], bytearray):
	num_points, wkb = parse_UInt32(wkb, int_parser)
	points, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_Geometry, num_points)
	return ", ".join(points), wkb


def parse_MultiLineString(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> ([LineString], bytearray):
	num_strings, wkb = parse_UInt32(wkb, int_parser)
	linestrings, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_Geometry, num_strings)
	return ", ".join(f"({item})" for item in linestrings), wkb


def parse_MultiPolygon(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> ([Polygon], bytearray):
	num_polygons, wkb = parse_UInt32(wkb, int_parser)
	polygons, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, raw, parse_Geometry, num_polygons)
	return ", ".join(f"({item})" for item in polygons), wkb


def parse_GeometryCollection(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> ([Geometry], bytearray):
	num_geometries, wkb = parse_UInt32(wkb, int_parser)
	geoms, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, False, parse_Geometry, num_geometries)
	return ", ".join(geoms), wkb


def parse_Geometry(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, raw: bool) -> (Geometry, bytearray):
	byte_order, wkb = parse_ByteOrder(wkb)
	int_parser = byte_order + "I"
	geom_type_integer, wkb = parse_UInt32(wkb, int_parser)
	dimension_count, extra_dimension_names, point_parser = MapExtraDimensionNames.get(geom_type_integer // 1000, (None, None))
	if dimension_count is None:
		raise Exception(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer // 1000} not in WKBDimensionSets.keys()")
	point_parser = byte_order + point_parser
	type_name, parser = MapGeometryTypeNameAndParser.get(geom_type_integer % 1000, (None, None))
	if type_name is None:
		raise Exception(f"WKB geometry type number {geom_type_integer} is not valid. {geom_type_integer % 1000} not in WKBGeometryTypeInfo.keys()")
	if parser is None:
		raise Exception(f"Parser is not implemented for {type_name}")
	geom, wkb = parser(wkb, int_parser, point_parser, dimension_count, True)
	
	if raw:
		return geom, wkb
	if not extra_dimension_names == "XY":
		type_name += " " + extra_dimension_names[2:]
	
	return f"{type_name} ({geom})", wkb


def parse_ByteOrder(wkb: bytearray) -> (ByteOrderChar, bytearray):
	byte, wkb = parse_Byte(wkb)
	if byte == 0:
		return ">", wkb
	elif byte == 1:
		return "<", wkb
	raise Exception(f"Invalid byte order {byte}")


MapExtraDimensionNames: {int: (DimensionCount, DimensionNames)} = {
	0: (2, "XY", "2d"),
	1: (3, "XYZ", "3d"),
	2: (3, "XYM", "3d"),
	3: (4, "XYZM", "4d")
}

MapGeometryTypeNameAndParser = {
	1: ("POINT", parse_Point),
	2: ("LINESTRING", parse_LineString),
	3: ("POLYGON", parse_Polygon),
	4: ("MULTIPOINT", parse_MultiPoint),
	5: ("MULTILINESTRING", parse_MultiLineString),
	6: ("MULTIPOLYGON", parse_MultiPolygon),
	7: ("GEOMETRYCOLLECTION", parse_GeometryCollection),
}


def wkb_to_wkt(wkb: bytearray) -> []:
	result, wkb = parse_Geometry(wkb, None, None, None, None)
	return result, wkb
