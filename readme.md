# Pure Python WKB (Well Known Binary) Converter

[![Test and Publish PyPi](https://github.com/thehappycheese/parse_wkb/actions/workflows/publish_to_pypi.yml/badge.svg)](https://github.com/thehappycheese/parse_wkb/actions/workflows/publish_to_pypi.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/parse-wkb.svg)](https://pypi.org/project/parse-wkb)

- `wkb_to_geojson()` converts WKB geometry into GeoJSON
- `wkb_to_wkt()` converts WKB geometry into WKT
- `geojson_to_wkb()` converts GeoJSON into WKB
- `wkb_to_abstract()` converts WKB into an abstract representation which closely resembles the binary format (for debugging purposes)

```python
from parse_wkb import (
    wkb_to_abstract,
    wkb_to_geojson,
    wkb_to_wkt,
    geojson_to_wkb
)

import json

WKB = b"\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x00D@\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00D@\x00\x00\x00\x00\x00\x00>@\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x004@\x00\x00\x00\x00\x00\x004@\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00>@\x00\x00\x00\x00\x00\x00$@"

parsed_to_geojson = wkb_to_geojson(WKB)
assert json.dumps(parsed_to_geojson) == '{"type": "MultiPoint", "coordinates": [[10.0, 40.0], [40.0, 30.0], [20.0, 20.0], [30.0, 10.0]]}'

parsed_to_wkt = wkb_to_wkt(WKB)
assert parsed_to_wkt == 'MULTIPOINT (10.0 40.0, 40.0 30.0, 20.0 20.0, 30.0 10.0)'

parsed_to_abstract = wkb_to_abstract(WKB)
assert parsed_to_abstract == (
	'LEnd',
	('MultiPoint', 'XY'),
	4,
	('LEnd', ('Point', 'XY'), 10.0, 40.0),
	('LEnd', ('Point', 'XY'), 40.0, 30.0),
	('LEnd', ('Point', 'XY'), 20.0, 20.0),
	('LEnd', ('Point', 'XY'), 30.0, 10.0)
)

# the reverse operation is only implemented from GeoJSON at the moment:
encoded_to_wkb_from_geojson = geojson_to_wkb(parsed_to_geojson)
assert encoded_to_wkb_from_geojson == WKB
```

## Supported Geometry Types

Supports `POINT`, `LINESTRING`, `POLYGON`, `MULTIPOINT`, `MULTILINESTRING`, `MULTIPOLYGON`, and `GEOMETRYCOLLECTION`

Supports geometry with `XY`, `XYZ`, `XYM`, and `XYZM` dimensions

## Specification

This module is based on v1.2.1 of the **OpenGIS Implementation Standard for Geographic information - Simple feature access - Part 1: Common architecture**
(which can be found here https://www.ogc.org/standards/sfa).

## Alternate Approaches

This library is somewhat redundant because:

- MySQL, POSTGIS and SQLite (SpatiaLite extension) provide the following conversion functions:
    - `ST_AsGeoJSON()`
    - `ST_GeometryFromGeoJSON()`
    - `ST_AsWKT()`
    - `ST_GeometryFromText()`

- if you are using `geopandas`+`shapely` these libraries provide conversion to and from WKB (implemented with fast C/C++ libraries)

However this library has a limited use-case; when python is working on your system, but you can't get the confounded binaries for `geopandas` or `shapely` to compile, or if you don't care for the size of numpy and everything else that comes with a few innocent `pip/conda install` commands.

From making this script I learned that WKB is actually not a great spec...

- WKB stores a lot of redundant information by repeating the byte order and geometry type for every point.
- Only 8 byte double precision floats are permitted... seems overkill for some applications. Would be better it we could specify precision, or even use integer types.

## Planned Features?

- WKT => WKB
 