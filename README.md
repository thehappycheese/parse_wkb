# Pure Python WKB Parser

Parses WKB into python tuple representation:
```python
from parse_wkb import parse_wkb

WKB = b'\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40'
PARSED = parse_wkb(WKB)
assert PARSED == [('MultiPoint ', (('Point ', (10.0, 40.0)), ('Point ', (40.0, 30.0)), ('Point ', (20.0, 20.0)), ('Point ', (30.0, 10.0))))]

# Note the equivalent WKT would be: 
WKT = 'MULTIPOINT(10 40,40 30,20 20,30 10)'
```
## Current Features
- Subset of WKB is supported:
  - Supports `Point`, `LineString`, `Polygon`, `MultiPoint`, `MultiLineString`, `MultiPolygon`, and `GeometryCollection`
  - Supports geometry with `XY`, `XYZ`, `XYM`, and `XYZM` dimensions
- `parse_wkb()` returns python tuples like this:
  - {Point}: `('Point ', (x:float, y:float))`
  - {MultiPoint}: `('MultiPoint ', ({Point}, {Point}, ...))`
  - {LineString}: `('LineString ', ({Point}, {Point}, ...))`
  - {Polygon}: `('Polygon ', (({Point}, {Point}, {Point}, ...), ({Point}, {Point}, {Point}, ...), ...))`
  - {MultiLineString}: `('MultiLineString ', ({Linestring}, {Linestring}, ...))`
  - {MultiPolygon}: `('MultiPolygon ', ({Polygon}, {Polygon}, ...))`
  - {GeometryCollection}: `('GeometryCollection ', ({Any}, {Any}, {Any}, ...))`
- Geometry with other dimensions will have it annotated per the WKT spec:
  - {PointZ}: `('Point Z', (x:float, y:float, z:float))`
  - {MultiPointZ}:  `('MultiPoint Z', (('Point Z', (x:float, y:float, z:float)), ('Point Z', (x:float, y:float, z:float)), ...))`
  - etc.

## Parse MySQL Binary Blob from Geometry Column (Internal representation)
 
MySQL provides the `ST_AsWKB()` to convert from the internal representation into standard WKB.
However the internal representation is the same as WKB **except** it has an extra 4 bytes on the front which encodes an SRID number.
The documentation makes no promises that this internal representation will stay the same or follow the OpenGIS Standard for WKB though... so beware.
Also, refer to the database documentation to find out what the SRID means; the numbering system may not be consistent with other systems. 

In any case, if for some reason you have access to the geometry column as a binary blob, but you dont have access to the `ST_AsWKB()` command, the following may be helpful:

```python
from parse_wkb import parse_MYSQL_internal, parse_wkb

MYSQL_GEOM_COLUMN = b'\x00\x00\x00\x00\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x40\x00\x00\x00\x00\x00\x00\x44\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x44\x40\x00\x00\x00\x00\x00\x00\x3e\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x34\x40\x00\x00\x00\x00\x00\x00\x34\x40\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3e\x40\x00\x00\x00\x00\x00\x00\x24\x40'
PARSED = parse_MYSQL_internal(MYSQL_GEOM_COLUMN)
assert PARSED == (('SRID=', 0), [('MultiPoint ', (('Point ', (10.0, 40.0)), ('Point ', (40.0, 30.0)), ('Point ', (20.0, 20.0)), ('Point ', (30.0, 10.0))))])

# or simply slice off 4 bytes before passing to the normal function:
PARSED = parse_wkb(MYSQL_GEOM_COLUMN[4:])
assert PARSED == [('MultiPoint ', (('Point ', (10.0, 40.0)), ('Point ', (40.0, 30.0)), ('Point ', (20.0, 20.0)), ('Point ', (30.0, 10.0))))]
```  

## Alternate Approaches

MySQL (and POSTGIS?) provide all the conversion functions you might need
  - `ST_AsGeoJSON()`
  - `ST_GeometryFromGeoJSON()`
  - `ST_AsWKT()` and
  - `ST_GeometryFromText()`

And if you are using `geopandas`+`shapely` these libraries also provide the conversion (implemented with fast C/C++ extensions)

This library may find a limited use-case when python is working on your system but you cant get the confounded binaries for `geopandas` or `shapely` to compile,
or if you don't care for the 2GB+ of numpy and everything else that comes with a few innocent `pip install` commands.


## Planned Features?
Conversions from
- WKB => Python Object => WKT
- GeoJSON => Python Object => WKB
 