import geopandas as gpd
import folium
import json
from shapely.geometry import shape, Point

# ------------------------------
# Load the Dhaka boundary from the provided GeoJSON file
# ------------------------------
geojson_file_path = "categorizer/Dhaka_Gruebner_2014.geojson"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract all geometries from the file
geometries = []
properties = []
for feature in geojson_data["features"]:
    geom = shape(feature["geometry"])
    properties.append(feature["properties"])
    geometries.append(geom)

# Create a GeoDataFrame with CRS set to WGS84
dhaka_boundary_gdf = gpd.GeoDataFrame(properties, geometry=geometries, crs="EPSG:4326")

# If multiple features exist, dissolve them into one unified boundary
dhaka_boundary_gdf = dhaka_boundary_gdf.dissolve()

# ------------------------------
# Define the Dhaka center based on updated coordinates
# ------------------------------
# Updated center coordinates:
#   Latitude:  23° 48' 39.8016'' N ≈ 23.811056° N
#   Longitude: 90° 24' 27.3888'' E ≈ 90.407608° E
lat_decimal = 23.811056
lon_decimal = 90.407608
dhaka_center = Point(lon_decimal, lat_decimal)
print("Dhaka center point (decimal degrees):", dhaka_center)

# ------------------------------
# Visualize using Folium
# ------------------------------
# Create a folium map centered on Dhaka
m = folium.Map(location=[lat_decimal, lon_decimal], zoom_start=12)

# Add the boundary polygon to the map with a clear black outline and no fill color
folium.GeoJson(
    dhaka_boundary_gdf.__geo_interface__,
    name="Dhaka Boundary",
    style_function=lambda feature: {
        'fillColor': 'none',
        'color': 'black',
        'weight': 3
    }
).add_to(m)

# Add a marker at the center point
folium.Marker(
    location=[lat_decimal, lon_decimal],
    popup="Dhaka Center",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# Add layer control and display the map
folium.LayerControl().add_to(m)

# Save map to HTML (or display in a Jupyter Notebook)
m.save("dhaka_boundary_map.html")
m
