With this project, it is aimed to visualize the points with .gpx extension, which are considered to be GNSS data, on the map.

The points here were taken with Google Earth, and the 3rd dimension coordinate, Elevation data, was obtained using SRTM data.

At the same time, a route was created using the coordinates specified by an aerial tribute object, and the shortest distance of this route on the ellipsoid was determined as the geodesic line. However, considering that the route taken by this aircraft is on the sphere, the shortest distance it traveled on the loxodrome curve was also found.

Raw data were taken as latitude, longitude and altitude, and considering that these were GNSS coordinates, they were converted into ECEF (The Earth-centered, Earth-fixed coordinate system) coordinates. For this purpose, coordinate transformation is provided.

It should be noted that this operation can be done on any .geojson extension file, so the GeoJSON parser code has also been added.

This project is currently reading coordinate data with .gpx extension. In the progress phase, the aim is to analyze GNSS data with RiNEX extension using Python.

Stay tuned!

![](https://github.com/sarpertaga/GPX-Data-Processing/blob/main/gif/gif.gif)
