import geopandas as gpd

class GeoJSONParser:
    @staticmethod
    def parse_geo_json(file_path):
        try:
            gdf = gpd.read_file(file_path)
            return gdf
        except Exception as ex:
            print(f"An error occurred while parsing the GeoJSON file: {ex}")
            return None