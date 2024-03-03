import math

class WGS84Coordinates:
    def __init__(self, longitude, latitude, elevation):
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation

    def to_ecef(self):
        ellipsoid_params = EllipsoidParameters()
        ee = (ellipsoid_params.a ** 2 - ellipsoid_params.b ** 2) / ellipsoid_params.a ** 2
        N = ellipsoid_params.a / math.sqrt(1 - ee * (math.sin(math.radians(self.latitude)) ** 2))
        h = self.elevation

        X = (N + h) * math.cos(math.radians(self.latitude)) * math.cos(math.radians(self.longitude))
        Y = (N + h) * math.cos(math.radians(self.latitude)) * math.sin(math.radians(self.longitude))
        Z = ((1 - ee) * N + h)

        return ECEFPoint(X, Y, Z)
    
    def to_json(self):
        return {"latitude": self.latitude, "longitude": self.longitude, "altitude": self.elevation}

class ECEFPoint:
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z
        
# GRS-80 Ellipsoid parameters

class EllipsoidParameters:
    def __init__(self):
        self.a = 6378137
        self.b = 6356752.314140347
        self.f = 1 / 298.257223563
