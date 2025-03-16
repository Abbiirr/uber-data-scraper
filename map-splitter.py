import geopandas as gpd
import matplotlib.pyplot as plt
import json
from shapely.geometry import shape, MultiPolygon, Polygon, box

# Load the raw JSON data from the provided GeoJSON file
with open("bangladesh.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract features related to Dhaka
dhaka_features = [f for f in geojson_data["features"] if "Dhaka" in f["properties"].get("NAME_1", "")]

# Convert extracted features into geometries and properties
processed_geometries = []
processed_properties = []

for f in dhaka_features:
    geom = shape(f["geometry"])  # Convert GeoJSON to Shapely geometry
    props = f["properties"]

    # If it's a MultiPolygon, extract individual Polygons
    if isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            processed_geometries.append(Polygon(poly.exterior))  # Keep only outer boundary
            processed_properties.append(props)
    elif isinstance(geom, Polygon):
        processed_geometries.append(Polygon(geom.exterior))  # Keep only outer boundary
        processed_properties.append(props)

# Create a GeoDataFrame for Dhaka boundary
dhaka_boundary_gdf = gpd.GeoDataFrame(processed_properties, geometry=processed_geometries, crs="EPSG:4326")

# Convert to UTM (metric projection) for accurate grid creation
dhaka_boundary_utm = dhaka_boundary_gdf.to_crs("EPSG:32646")

# Get bounding box for Dhaka City
min_x, min_y, max_x, max_y = dhaka_boundary_utm.total_bounds

# Define grid size (5km x 5km)
grid_size = 5000  # in meters

# Create grid cells (polygons)
polygons = []
grid_labels = []
x = min_x
while x < max_x:
    y = min_y
    while y < max_y:
        # Create a square cell polygon
        cell = box(x, y, x + grid_size, y + grid_size)
        polygons.append(cell)
        # Assign labels
        col = int((x - min_x) // grid_size)
        row = int((y - min_y) // grid_size)
        grid_labels.append(f"R{row}C{col}")
        y += grid_size
    x += grid_size

# Create GeoDataFrame for the grid
grid_gdf = gpd.GeoDataFrame({'label': grid_labels, 'geometry': polygons}, crs="EPSG:32646")

# Clip grid to fit inside Dhaka City boundary
clipped_grid = gpd.overlay(grid_gdf, dhaka_boundary_utm, how="intersection")

# Convert back to WGS84 for plotting
clipped_grid = clipped_grid.to_crs("EPSG:4326")
dhaka_boundary_gdf = dhaka_boundary_gdf.to_crs("EPSG:4326")

# Plot the final result
fig, ax = plt.subplots(figsize=(10, 10))

# Plot Dhaka boundary
dhaka_boundary_gdf.boundary.plot(ax=ax, edgecolor="black", linewidth=2, label="Dhaka Boundary")

# Plot clipped grid
clipped_grid.boundary.plot(ax=ax, edgecolor="blue", linewidth=1, alpha=0.7, label="Grid Cells")

ax.set_title("Dhaka City Divided into Grids within Official Boundaries")
ax.set_axis_off()
plt.legend()
plt.show()
