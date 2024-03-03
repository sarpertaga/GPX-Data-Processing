from GeoJSONParser import GeoJSONParser
from GpxReader import gpxReader
from FindShortestPath import FindShortestPath
from CoordinateConversion import WGS84Coordinates

def main():
    start_end_points = "YOUR_GPX_FILE"
    route_gpx = "YOUR_GPX_FILE"
    geojson = "YOUR_GEOJSON_FILE"

    geometries = GeoJSONParser.parse_geo_json(geojson)

    gpx_points = gpxReader.read_gpx(start_end_points)

    wgs84_coordinates_list = [{
        "Latitude": point["Latitude"],
        "Longitude": point["Longitude"],
        "Elevation": point["Elevation"]
    } for point in gpx_points]

    wgs84_coordinates_list = [WGS84Coordinates(longitude=point["Longitude"],
                                                latitude=point["Latitude"],
                                                elevation=point["Elevation"]) for point in gpx_points]

    first_point = wgs84_coordinates_list[0]
    last_point = wgs84_coordinates_list[-1]

    loksodrom_distance = FindShortestPath.find_loksordom_curve_from_gpx(first_point, last_point)
    geodesic_line = FindShortestPath.find_geodesic_distance_from_gpx(first_point, last_point)
    geodesic_line_with_route = FindShortestPath.calculate_total_geodesic_distance_from_gpx(wgs84_coordinates_list)
    high_way_line = FindShortestPath.find_shortest_path_from_geojson(first_point, last_point, geojson)
    print(loksodrom_distance, geodesic_line, geodesic_line_with_route, high_way_line)
    
    
if __name__ == "__main__":
    main()
