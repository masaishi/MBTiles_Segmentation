from typing import Union, List, Tuple

def point_to_wkt(point: Tuple[float, float]) -> str:
    return f"POINT ({point[0]} {point[1]})"

def _linestring_exterior(linestring: List[Tuple[float, float]]) -> str:
    return ", ".join([f"{x} {y}" for (x, y) in linestring])

def linestring_to_wkt(linestring: List[Tuple[float, float]]) -> str:
    return "LINESTRING (" + _linestring_exterior(linestring) + ")"

def _polygon_exterior(polygon: List[Tuple[float, float]]) -> str:
    return ", ".join([f"{x} {y}" for (x, y) in polygon[0]])

def polygon_to_wkt(polygon: List[List[Tuple[float, float]]]) -> str:
    return f"POLYGON (({_polygon_exterior(polygon)}))"

def multipoint_to_wkt(multipoint: List[Tuple[float, float]]) -> str:
    points = ", ".join([f"({x} {y})" for x, y in multipoint])
    return f"MULTIPOINT ({points})"

def multilinestring_to_wkt(multilinestring: List[List[Tuple[float, float]]]) -> str:
    lines = ", ".join(["(" + _linestring_exterior(line) + ")" for line in multilinestring])
    return f"MULTILINESTRING ({lines})"

def multipolygon_to_wkt(multipolygons: List[List[List[Tuple[float, float]]]]) -> str:
    polygons = ", ".join(["((" + _polygon_exterior(poly) + "))" for poly in multipolygons])
    return f"MULTIPOLYGON ({polygons})"

def geometrycollection_to_wkt(geometries: List[Union[str, List]]) -> str:
    geometries_wkt = ", ".join([geometry_to_wkt(geometry) for geometry in geometries])
    return f"GEOMETRYCOLLECTION ({geometries_wkt})"

def geometry_to_wkt(type: str, coords: Union[Tuple[float, float], List[Tuple[float, float]]]) -> str:
    r"""
    Converts a GeoJSON geometry to a WKT string.
    """
    if type == 'Point':
        return point_to_wkt(coords)
    elif type == 'LineString':
        return linestring_to_wkt(coords)
    elif type == 'Polygon':
        return polygon_to_wkt(coords)
    elif type == 'MultiPoint':
        return multipoint_to_wkt(coords)
    elif type == 'MultiLineString':
        return multilinestring_to_wkt(coords)
    elif type == 'MultiPolygon':
        return multipolygon_to_wkt(coords)
    # Add more geometry types if necessary
    else:
        raise ValueError(f"Unknown geometry type: {type}")
