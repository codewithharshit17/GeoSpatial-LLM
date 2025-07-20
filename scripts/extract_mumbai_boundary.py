import osmnx as ox
import geopandas as gpd
import os

# Mumbai boundary extraction
place = "Mumbai, India"
gdf = ox.geocode_to_gdf(place)

# Save to correct path
output_path = "data/osm/mumbai_boundary.geojson"
os.makedirs("data/osm", exist_ok=True)
gdf.to_file(output_path, driver="GeoJSON")

print(f"✅ Boundary saved to: {output_path}")
