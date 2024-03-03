import dash
import dash_leaflet as dl
import dash_html_components as html
from dash.dependencies import Input, Output
from GpxReader import gpxReader
from time import sleep
from CoordinateConversion import WGS84Coordinates
from FindShortestPath import FindShortestPath
import dash_core_components as dcc

# Read the GPX file
gpx_path = "route.gpx"
gpx_points = gpxReader.read_gpx(gpx_path)

# Create the Dash application
app = dash.Dash(__name__)

# Function to calculate the route from GPX points
def calculate_route(progress):
    route = []
    for i in range(progress+1):
        route.append((float(gpx_points[i]["Latitude"]), float(gpx_points[i]["Longitude"])))
    return route

# Create the map container
map_container = dl.Map(
    [
        dl.TileLayer(),
        dl.LayerGroup(id="markers"),
        dl.LayerGroup([
            dl.Polyline(
                positions=calculate_route(0),
                color="blue",
                weight=5,
                opacity=1.0,
                id="route"
            ),
            dl.Marker(
                position=calculate_route(0)[0],
                children=dl.Tooltip("Start Point"),
                id="start-point"
            ),
            dl.Marker(
                position=calculate_route(0)[-1],
                children=dl.Tooltip("End Point"),
                id="end-point"
            )
        ])
    ],
    center=calculate_route(0)[0],
    zoom=12,
    style={'width': '100%', 'height': '100vh'}
)

# Application layout
app.layout = html.Div([
    html.H1("GNSS-Data Visualization on Map"),
    html.Div([
        html.Button("Route", id="play-button", n_clicks=0),
        html.Button("Pause", id="pause-button", n_clicks=0),
        html.Button("Show Middle-Points", id="show-points-button", n_clicks=0),
    ]),
    html.Div([
        html.Button("Access Coordinate Information", id="access-info-button", style={"display": "none"}),  # Initially hidden
        html.Div(id="length-dropdown-container", style={"display": "none"}, children=[
            html.Div("Total Length:", style={'float': 'left', 'margin-right': '10px', 'margin-top': '7px'}),
            dcc.Dropdown(
                id='length-dropdown',
                options=[
                    {'label': 'Geodesic Line', 'value': 'geodesic'},
                    {'label': 'Loksodrom Curve', 'value': 'loksodrom'},
                ],
                value='geodesic',
                placeholder="Select Length Type",
                style={'width': '200px', 'float': 'left'}
            ),
        ]),
    ], style={'margin-top': '10px'}),  # Spacing for the buttons
    html.Div(id="length-output"),  # New output area for length information
    html.Div(id="point-info"),  # New output area for point information
    map_container
])

# Variable to toggle coordinate info display
show_coordinate_info = False
show_length_info = False

# Callback to toggle display of coordinate information
@app.callback(
    Output("point-info", "children"),
    Output("access-info-button", "children"),
    Input("access-info-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_coordinate_info(access_info_clicks):
    global show_coordinate_info
    if show_coordinate_info:
        show_coordinate_info = False
        return "", "Access Coordinate Information"
    else:
        show_coordinate_info = True
        gnss_coordinate_info = []
        for i, point in enumerate(gpx_points, start=1):
            wgs84_point = WGS84Coordinates(point["Longitude"], point["Latitude"], point["Elevation"])
            ecef_point = wgs84_point.to_ecef()
            x_str = "{:.4f}".format(ecef_point.X)
            y_str = "{:.4f}".format(ecef_point.Y)
            z_str = "{:.4f}".format(ecef_point.Z)
            if len(x_str) > 5:
                x_str = "{:.3f}".format(ecef_point.X)
            if len(y_str) > 5:
                y_str = "{:.3f}".format(ecef_point.Y)
            if len(z_str) > 5:
                z_str = "{:.3f}".format(ecef_point.Z)
            gnss_coordinate_info.append(html.P(f"Point {i}: X = {x_str}, Y = {y_str}, Z = {z_str}, Time = {point['Time']}"))
        point_info_text = html.Div([
            html.H3("GNSS-Coordinate Information (meter)"),
            *gnss_coordinate_info
        ])
        return point_info_text, "Hide Coordinate Information"

# Callback to update length information
@app.callback(
    Output("length-output", "children"),  # Total distance output
    Input("length-dropdown", "value"),  # New button trigger
    prevent_initial_call=True
)
def update_length_info(selected_value):
    total_distance_geodesic = FindShortestPath.calculate_total_geodesic_distance_from_gpx(
        [WGS84Coordinates(point["Longitude"], point["Latitude"], point["Elevation"]) for point in gpx_points]
    )  # Calculate total distance as geodesic line

    total_distance_loxsodrom = FindShortestPath.calculate_total_loksodrom_curve_from_gpx(
        [WGS84Coordinates(point["Longitude"], point["Latitude"], point["Elevation"]) for point in gpx_points]
    )  # Calculate total distance as loksodromic curve

    if selected_value == 'geodesic':
        return f"Total Length as Geodesic Line: {total_distance_geodesic:.2f} km"
    elif selected_value == 'loksodrom':
        return f"Total Length as Loksodrom Curve: {total_distance_loxsodrom:.2f} km"

# Callback function to update GNSS route
@app.callback(
    Output("route", "positions"),
    Output("end-point", "position"),
    Output("markers", "children"),  # Marker output
    Output("access-info-button", "style"),  # Coordinate info button visibility
    Output("length-dropdown-container", "style"),  # Length dropdown visibility
    Input("play-button", "n_clicks"),
    Input("show-points-button", "n_clicks"),
    prevent_initial_call=True
)
def update_map(play_clicks, show_points_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [], [], [], {"display": "none"}

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    progress = 0

    if button_id == "play-button" or button_id == "show-points-button":
        route_positions = []
        end_point_position = None
        markers = []
        if button_id == "show-points-button":
            for i, point in enumerate(gpx_points, start=1):
                wgs84_point = WGS84Coordinates(point["Longitude"], point["Latitude"], point["Elevation"])
                ecef_point = wgs84_point.to_ecef()
                x_str = "{:.4f}".format(ecef_point.X)
                y_str = "{:.4f}".format(ecef_point.Y)
                z_str = "{:.4f}".format(ecef_point.Z)
                if len(x_str) > 5:
                    x_str = "{:.3f}".format(ecef_point.X)
                if len(y_str) > 5:
                    y_str = "{:.3f}".format(ecef_point.Y)
                if len(z_str) > 5:
                    z_str = "{:.3f}".format(ecef_point.Z)
                marker_tooltip = html.Div([
                    html.P(f"Point {i}:"),
                    html.P(f"X = {x_str}"),
                    html.P(f"Y = {y_str}"),
                    html.P(f"Z = {z_str}"),
                    html.P(f"Time = {point['Time']}")
                ])
                markers.append(
                    dl.Marker(
                        position=(point["Latitude"], point["Longitude"]),
                        children=[dl.Tooltip(marker_tooltip)],
                        id={"type": "point-marker", "index": i}
                    )
                )
        while progress < len(gpx_points):
            sleep(0.01)  # Wait time to slow down the animation
            route_positions = calculate_route(progress)
            end_point_position = route_positions[-1]
            progress += 1

        return route_positions, end_point_position, markers, {"display": "inline"}, {"display": "block"}

# Run the application
if __name__ == '__main__':
    app.run_server(port=8050)
