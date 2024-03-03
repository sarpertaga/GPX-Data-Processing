import math
import json
from shapely.geometry import LineString, Point
from CoordinateConversion import WGS84Coordinates, EllipsoidParameters

class FindShortestPath:
    
    @staticmethod
    def calculate_shortest_path(start_latitude, start_longitude, end_latitude, end_longitude):
        earth_radius = 6371

        start_lat_rad = math.radians(start_latitude)
        start_lon_rad = math.radians(start_longitude)
        end_lat_rad = math.radians(end_latitude)
        end_lon_rad = math.radians(end_longitude)

        delta_lon = end_lon_rad - start_lon_rad
        y = math.sqrt((math.cos(end_lat_rad) * math.sin(delta_lon)) ** 2 +
                      (math.cos(start_lat_rad) * math.sin(end_lat_rad) -
                       math.sin(start_lat_rad) * math.cos(end_lat_rad) * math.cos(delta_lon)) ** 2)
        x = math.sin(start_lat_rad) * math.sin(end_lat_rad) + math.cos(start_lat_rad) * math.cos(end_lat_rad) * math.cos(delta_lon)
        c = math.atan2(y, x)
        distance = earth_radius * c

        return distance
    
    @staticmethod
    def find_loksordom_curve_from_gpx(start_point, end_point):
        shortest_path = FindShortestPath.calculate_shortest_path(start_point.latitude, start_point.longitude, end_point.latitude, end_point.longitude)
        return shortest_path

    @staticmethod
    def calculate_geodesic_distance(start_point, end_point):
        ellipsoid = EllipsoidParameters()

        start_latitude = start_point.latitude
        start_longitude = start_point.longitude
        end_latitude = end_point.latitude
        end_longitude = end_point.longitude

        L = math.radians(end_longitude - start_longitude)
        U1 = math.atan((1 - ellipsoid.f) * math.tan(math.radians(start_latitude)))
        U2 = math.atan((1 - ellipsoid.f) * math.tan(math.radians(end_latitude)))
        sinU1 = math.sin(U1)
        cosU1 = math.cos(U1)
        sinU2 = math.sin(U2)
        cosU2 = math.cos(U2)
        lambda_val = L
        lambda_p = 0
        sin_sigma = 0
        cos_sigma = 0
        sigma = 0
        sin_alpha = 0
        cos_sq_alpha = 0
        cos_2sigma_m = 0
        C = 0

        while True:
            sin_lambda = math.sin(lambda_val)
            cos_lambda = math.cos(lambda_val)
            sin_sigma = math.sqrt((cosU2 * sin_lambda) ** 2 +
                                  (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda) *
                                  (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda))
            if sin_sigma == 0:
                return 0
            cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
            cos_sq_alpha = 1 - sin_alpha ** 2
            cos_2sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos_sq_alpha
            C = ellipsoid.f / 16 * cos_sq_alpha * (4 + ellipsoid.f * (4 - 3 * cos_sq_alpha))
            lambda_p = lambda_val
            lambda_val = L + (1 - C) * ellipsoid.f * sin_alpha * (
                        sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))

            if abs(lambda_val - lambda_p) <= 1e-12:
                break

        u_sq = cos_sq_alpha * (ellipsoid.a ** 2 - ellipsoid.b ** 2) / (ellipsoid.b ** 2)
        A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
        B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
        delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
                                    B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)))
        s = (ellipsoid.b * A * (sigma - delta_sigma)) / 1000

        return s
    
    @staticmethod
    def find_geodesic_distance_from_gpx(start_point, end_point):
        geodesic_distance = FindShortestPath.calculate_geodesic_distance(start_point, end_point)
        return geodesic_distance
    
    @staticmethod
    def calculate_total_geodesic_distance_from_gpx(points):
        total_distance = 0
        for i in range(len(points) - 1):
            total_distance += FindShortestPath.calculate_geodesic_distance(points[i], points[i + 1])
        return total_distance
    
    @staticmethod
    def calculate_total_loksodrom_curve_from_gpx(points):
        total_distance = 0
        for i in range(len(points) - 1):
            total_distance += FindShortestPath.find_loksordom_curve_from_gpx(points[i], points[i + 1])
        return total_distance
    
    def find_shortest_path_from_geojson(start_point, end_point, geojson_path):
        with open(geojson_path, 'r') as f:
            data = json.load(f)

        start_ecef = start_point.to_ecef()
        end_ecef = end_point.to_ecef()
        
        shortest_path = None
        shortest_distance = float('inf')

        for feature in data['features']:
            if feature['geometry']['type'] == 'MultiLineString':
                for line_string in feature['geometry']['coordinates']:
                    total_distance = 0
                    for i in range(len(line_string) - 1):
                        point1 = WGS84Coordinates(line_string[i][0], line_string[i][1], 0)
                        point2 = WGS84Coordinates(line_string[i+1][0], line_string[i+1][1], 0)
                        point1_ecef = point1.to_ecef()
                        point2_ecef = point2.to_ecef()
                        distance = math.sqrt((point2_ecef.X - point1_ecef.X)**2 + 
                                            (point2_ecef.Y - point1_ecef.Y)**2 + 
                                            (point2_ecef.Z - point1_ecef.Z)**2)
                        total_distance += distance
                    
                    if total_distance < shortest_distance:
                        shortest_distance = total_distance
                        shortest_path = line_string

        return shortest_path, shortest_distance

