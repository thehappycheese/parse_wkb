# Pure Python WKB Parser

Parses WKB geometry from bytes into an arbitrary (WKT-ish) python tuple representation:

```python
from wkb_to_abstract import parse_wkb

WKB = b'\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40'
PARSED, any_remaining_bytes = parse_wkb(WKB)
assert len(any_remaining_bytes) == 0
assert PARSED == ('MULTIPOINT', 'XY', (('POINT', 'XY', (10.0, 40.0)), ('POINT', 'XY', (40.0, 30.0)), ('POINT', 'XY', (20.0, 20.0)), ('POINT', 'XY', (30.0, 10.0))))

# Note the equivalent WKT would be: 
WKT = 'MULTIPOINT(10 40,40 30,20 20,30 10)'
```


## Current Features
- A subset of WKB is supported:
  - Supports `POINT`, `LINESTRING`, `POLYGON`, `MULTIPOINT`, `MULTILINESTRING`, `MULTIPOLYGON`, and `GEOMETRYCOLLECTION`
  - Supports geometry with `XY`, `XYZ`, `XYM`, and `XYZM` dimensions
- `parse_wkb()` returns python tuples like this:
  - {Point}: `('POINT', 'XY', (x:float, y:float))`
  - {MultiPoint}: `('MULTIPOINT', 'XY', ({Point}, {Point}, ...))`
  - {LineString}: `('LINESTRING', 'XY', ({Point}, {Point}, ...))`
  - {Polygon}: `('POLYGON', 'XY', (({Point}, {Point}, {Point}, ...), ({Point}, {Point}, {Point}, ...), ...))`
  - {MultiLineString}: `('MULTILINESTRING', 'XY', ({LineString}, {LineString}, ...))`
  - {MultiPolygon}: `('MULTIPOLYGON', 'XY', ({Polygon}, {Polygon}, ...))`
  - {GeometryCollection}: `('GEOMETRYCOLLECTION', 'XY', ({Any}, {Any}, {Any}, ...))`
- Geometry with extra dimensions will be specified in the second element of the tuple as follows:
  - {PointZ}: `('Point', 'XYZ', (x:float, y:float, z:float))`
  - {PointM}: `('Point', 'XYM', (x:float, y:float, m:float))`
  - {PointZM}: `('Point', 'XYZM', (x:float, y:float, z:float, m:float))`
  - {MultiPointZ}:  `('MultiPoint', 'XYZ', ( ('Point', 'XYZ', (x:float, y:float, z:float)), ('Point', 'XYZ', (x:float, y:float, z:float)), ...) )`
  - etc.

## Specification
This module is based on v1.2.1 of the **OpenGIS Implementation Standard for Geographic information - Simple feature access - Part 1: Common architecture**
(which can be found here https://www.ogc.org/standards/sfa).

###MySQL
The goal was to support the same subset of the spec that is currently supported by MySQL (v8.0.23 of the `mysql` docker image tested in Feb 2021).
The function `parse_MYSQL_internal()` will parse the variant of WBK used by MySQL.

MYSQL doesn't say it supports Z and M parts, but this module supports them anyway.

The functions worked with the latest version .

The internal storage format of MySQL is very similar to standard WKB with the exception that the first 4 bytes of the BLOB encode an SRID.

###PostGIS
I don't think this library will help with PostGIS.
POSTGIS has an extension called EWKB which is currently a superset of WKB, but their website warns that they don't care much about retaining this compatibility.

###SQLite / SpatiaLite
SQLite with the SpatiaLite extension also uses a variation of WKB but it is incompatible with this script as it departs substantially from standard WKB.


## Parse MySQL Binary Blob from Geometry Column (Internal representation)
 
MySQL provides the `ST_AsWKB()` to convert from the internal representation into standard WKB.
However the internal representation is the same as WKB **except** it has an extra 4 bytes on the front which encodes an SRID number.
The documentation makes no promises that this internal representation will stay the same or follow the OpenGIS Standard for WKB though... so beware.
Also, refer to the database documentation to find out what the SRID means; the numbering system may not be consistent with other systems. 

In any case, if for some reason you have access to the geometry column as a binary blob, but you don't have access to the `ST_AsWKB()` command, the following may be helpful:

```python
from wkb_to_abstract import parse_MYSQL_internal, parse_wkb

MYSQL_GEOM_COLUMN = b'\x00\x00\x00\x00\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40'

parsed, any_remaining_bytes = parse_MYSQL_internal(MYSQL_GEOM_COLUMN)
assert len(any_remaining_bytes) == 0
assert parsed == (('SRID=', 0), ('MULTIPOINT', 'XY', (('POINT', 'XY', (10.0, 40.0)), ('POINT', 'XY', (40.0, 30.0)), ('POINT', 'XY', (20.0, 20.0)), ('POINT', 'XY', (30.0, 10.0)))))

# or simply slice off 4 bytes before passing to the normal function:
parsed, any_remaining_bytes = parse_wkb(MYSQL_GEOM_COLUMN[4:])
assert len(any_remaining_bytes) == 0
assert parsed == ('MULTIPOINT', 'XY', (('POINT', 'XY', (10.0, 40.0)), ('POINT', 'XY', (40.0, 30.0)), ('POINT', 'XY', (20.0, 20.0)), ('POINT', 'XY', (30.0, 10.0))))
```  

Note that according to the documentation, MySQL stores geometry always in little endian order. Therefore I have assumed that the SRID is always stored this way also. I have not tested it since I discarded the SRID part.


## Alternate Approaches

MySQL (and POSTGIS?) provide all the conversion functions you might need
  - `ST_AsGeoJSON()`
  - `ST_GeometryFromGeoJSON()`
  - `ST_AsWKT()` and
  - `ST_GeometryFromText()`

And if you are using `geopandas`+`shapely` these libraries also provide the conversion (implemented with fast C/C++ extensions)

This library may find a limited use-case when python is working on your system but you cant get the confounded binaries for `geopandas` or `shapely` to compile,
or if you don't care for the 2GB+ of numpy and everything else that comes with a few innocent `pip install` commands.

From making this script I learned that WKB is actually not a great spec...
 - it stores a lot of redundant information by repeating the byte order and geometry type for every point.
 - Only 8 byte double precision floats are permitted... seems overkill for some applications. Would be better it we could specify precision, or even use integer types. 


## Planned Features?
Conversions from
- WKB => Python Object => WKT
- GeoJSON => Python Object => WKB
 