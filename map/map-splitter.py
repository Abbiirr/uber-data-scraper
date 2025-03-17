import geopandas as gpd
import matplotlib.pyplot as plt
import json
import pandas as pd
from shapely.geometry import shape, box, Point
from shapely.ops import unary_union

# ------------------------------
# Load the Dhaka boundaries from the provided GeoJSON file
# ------------------------------
geojson_file_path = "categorizer/dhaka_bounding_box.geojson"
with open(geojson_file_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract all features assuming they represent Dhaka boundaries
geometries = []
properties = []
for feature in geojson_data["features"]:
    geom = shape(feature["geometry"])
    properties.append(feature["properties"])
    geometries.append(geom)

# Create a GeoDataFrame with CRS set to WGS84
dhaka_boundary_gdf = gpd.GeoDataFrame(properties, geometry=geometries, crs="EPSG:4326")

# Dissolve multiple features into a single unified boundary
dhaka_boundary_gdf = dhaka_boundary_gdf.dissolve()

# ------------------------------
# Create a point from the updated Dhaka center coordinates
# ------------------------------
# Updated coordinates:
#   Latitude:  23° 48' 39.8016'' N ≈ 23.811056° N
#   Longitude: 90° 24' 27.3888'' E ≈ 90.407608° E
lat_decimal = 23.811056
lon_decimal = 90.407608
dhaka_center = Point(lon_decimal, lat_decimal)
print("Dhaka center point (decimal degrees):", dhaka_center)

# ------------------------------
# Convert the Dhaka boundary to UTM (EPSG:32646) for grid creation
# ------------------------------
dhaka_boundary_utm = dhaka_boundary_gdf.to_crs("EPSG:32646")

# ------------------------------
# Generate Grid Cells (500m x 500m) over the bounding box of Dhaka in UTM coordinates
# ------------------------------
min_x, min_y, max_x, max_y = dhaka_boundary_utm.total_bounds
grid_size = 1000  # Set grid size to 500 meters

grid_polygons = []
grid_labels = []
x = min_x
while x < max_x:
    y = min_y
    while y < max_y:
        # Create a square cell
        cell = box(x, y, x + grid_size, y + grid_size)
        grid_polygons.append(cell)
        col = int((x - min_x) // grid_size)
        row = int((y - min_y) // grid_size)
        grid_labels.append(f"R{row}C{col}")
        y += grid_size
    x += grid_size

grid_gdf = gpd.GeoDataFrame({'label': grid_labels, 'geometry': grid_polygons}, crs="EPSG:32646")

# ------------------------------
# Clip grid cells to only those within the Dhaka boundary
# ------------------------------
clipped_grid = gpd.overlay(grid_gdf, dhaka_boundary_utm, how="intersection")

# ------------------------------
# Export Grid Boundaries to CSV (after reprojecting back to WGS84)
# ------------------------------
clipped_grid = clipped_grid.to_crs("EPSG:4326")
grid_boundaries = []
for idx, row in clipped_grid.iterrows():
    minx, miny, maxx, maxy = row.geometry.bounds
    grid_boundaries.append({
        "label": row["label"],
        "min_x": minx,
        "min_y": miny,
        "max_x": maxx,
        "max_y": maxy
    })

grid_boundaries_df = pd.DataFrame(grid_boundaries)
csv_path = "categorizer/grid_boundaries.csv"
grid_boundaries_df.to_csv(csv_path, index=False)
print("Grid boundaries exported to 'grid_boundaries.csv'")

# ------------------------------
# Plot the boundaries and grid cells for visualization
# ------------------------------
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the unified Dhaka boundary with no fill and a clear black edge
dhaka_boundary_gdf.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=2, label="Dhaka Boundary")

# Plot the grid cells (clipped to Dhaka)
clipped_grid.boundary.plot(ax=ax, edgecolor="blue", linewidth=0.5, alpha=0.7, label="1000m Grids")

# Plot the center point
ax.scatter([lon_decimal], [lat_decimal], color="red", marker="x", s=100, label="Dhaka Center")

ax.set_title("Dhaka City Divided into 500m Grids within Official Boundaries")
ax.set_axis_off()
plt.legend()
plt.show()
