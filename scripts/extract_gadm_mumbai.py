import geopandas as gpd
import os

# Load GADM Level 2 shapefile
gdf = gpd.read_file("path/to/gadm41_IND.shp")

# Filter for Mumbai districts
mumbai = gdf[gdf["NAME_2"].str.contains("Mumbai", case=False)]

# Save as GeoJSON
os.makedirs("data/osm", exist_ok=True)
mumbai.to_file("data/osm/mumbai_boundary.geojson", driver="GeoJSON")

print("✅ Clean Mumbai boundary saved to data/osm/mumbai_boundary.geojson")
