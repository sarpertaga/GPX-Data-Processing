from xml.dom import minidom
from datetime import datetime, timedelta

class gpxReader:
    @staticmethod
    def read_gpx(file_path):
        points = []

        try:
            with open(file_path, 'r') as file:
                xml_data = minidom.parse(file)
                track_points = xml_data.getElementsByTagName('trkpt')

                initial_time = datetime.combine(datetime.now().date(), datetime.min.time())  # Today date and time
                time_increment = timedelta(minutes=5, seconds=30)  # Time increase limit

                for index, node in enumerate(track_points):
                    point_time = node.getElementsByTagName('time')[0].firstChild.data if node.getElementsByTagName('time') else None
                    if point_time:
                        point_time = datetime.fromisoformat(point_time)
                    else:
                        point_time = initial_time + index * time_increment  # Adjust time
                    point = {
                        'Latitude': float(node.getAttribute('lat')),
                        'Longitude': float(node.getAttribute('lon')),
                        'Elevation': float(node.getElementsByTagName('ele')[0].firstChild.data) if node.getElementsByTagName('ele') else 100,
                        'Time': point_time
                    }
                    points.append(point)
        except Exception as ex:
            print(f"An error occurred while reading the GPX file: {ex}")

        return points
