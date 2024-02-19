from __future__ import annotations
from struct import unpack
from typing import Any, Dict
from typing import Callable
from typing import List
# from typing import Literal
from typing import Tuple
from typing import Union
import warnings

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


def multi_parse(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount, func: Callable[[bytearray, str, str, DimensionCount], Tuple[Any, bytearray]], repeat_count: int) -> Tuple[Tuple[Any, ...], bytearray]:
	# oh Haskell, how I miss thee, thine curried functions, thine folds. Here I wallow in constant reinvention, apart from thine warm aura of glorious composition.
	result = []
	for _ in range(repeat_count):
		item_result, wkb = func(wkb, int_parser, point_parser, dimension_count)
		result.append(item_result)
	return tuple(result), wkb


def parse_Byte(wkb: bytearray) -> Tuple[Byte, bytearray]:
	return wkb[0], wkb[1:]


def parse_UInt32(wkb: bytearray, int_parser) -> Tuple[UInt32, bytearray]:
	return unpack(int_parser, wkb[:4])[0], wkb[4:]


# def parse_Double(wkb: bytearray, int_parser:str, point_parser:str) -> (Double, bytearray):
# 	# hopefully parses 8 byte IEEE 754 Double
# 	return unpack(byte_order[0] + " d", wkb[:8])[0], wkb[8:]


def parse_Point(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[Point, bytearray]:
	return tuple(unpack(point_parser, wkb[:8 * dimension_count])), wkb[8 * dimension_count:]


def parse_LinearRing(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[LinearRing, bytearray]:
	num_points, wkb = parse_UInt32(wkb, int_parser)
	points, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Point, num_points)
	return (num_points, *points), wkb


def parse_LineString(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[LineString, bytearray]:
	num_points, wkb = parse_UInt32(wkb, int_parser)
	points, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Point, num_points)
	return (num_points, *points), wkb


def parse_Polygon(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[Polygon, bytearray]:
	# TODO: The first and last point of a linear ring should be the same value. enforce?
	num_rings, wkb = parse_UInt32(wkb, int_parser)
	polygon, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_LinearRing, num_rings)
	return (num_rings, *polygon), wkb


def parse_MultiPoint(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[list[Point], bytearray]:
	num_points, wkb = parse_UInt32(wkb, int_parser)
	points, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Geometry, num_points)
	return (num_points, *points), wkb


def parse_MultiLineString(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[list[LineString], bytearray]:
	num_strings, wkb = parse_UInt32(wkb, int_parser)
	linestrings, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Geometry, num_strings)
	return (num_strings, *linestrings), wkb


def parse_MultiPolygon(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[list[Polygon], bytearray]:
	num_polygons, wkb = parse_UInt32(wkb, int_parser)
	polygons, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Geometry, num_polygons)
	return (num_polygons, *polygons), wkb


def parse_GeometryCollection(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[list[Geometry], bytearray]:
	num_geometries, wkb = parse_UInt32(wkb, int_parser)
	geoms, wkb = multi_parse(wkb, int_parser, point_parser, dimension_count, parse_Geometry, num_geometries)
	return (num_geometries, *geoms), wkb


def parse_Geometry(wkb: bytearray, int_parser: str, point_parser: str, dimension_count: DimensionCount) -> Tuple[Geometry, bytearray]:
	byte_order, byte_order_name, wkb = parse_ByteOrder(wkb)
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
	geom, wkb = parser(wkb, int_parser, point_parser, dimension_count)
	return (byte_order_name, (type_name, extra_dimension_names), *geom), wkb


def parse_ByteOrder(wkb: bytearray) -> Tuple[ByteOrderChar, bytearray]:
	byte, wkb = parse_Byte(wkb)
	if byte == 0:
		return ">", "BEnd", wkb
	elif byte == 1:
		return "<", "LEnd", wkb
	raise Exception(f"Invalid byte order {byte}")


MapExtraDimensionNames: dict[int: Tuple[DimensionCount, DimensionNames]] = {
	0: (2, "XY", "2d"),
	1: (3, "XYZ", "3d"),
	2: (3, "XYM", "3d"),
	3: (4, "XYZM", "4d")
}

MapGeometryTypeNameAndParser = {
	1: ("Point", parse_Point),
	2: ("LineString", parse_LineString),
	3: ("Polygon", parse_Polygon),
	4: ("MultiPoint", parse_MultiPoint),
	5: ("MultiLineString", parse_MultiLineString),
	6: ("MultiPolygon", parse_MultiPolygon),
	7: ("Geometrycollection", parse_GeometryCollection),
}


def wkb_to_abstract(wkb: bytearray) -> list[Geometry]:
	result, wkb = parse_Geometry(wkb, None, None, None)
	if len(wkb) > 0:
		warnings.warn(f"WKB data not fully parsed. {len(wkb)} bytes remaining")
	return result
