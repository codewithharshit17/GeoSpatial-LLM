import osmnx as ox
import os
os.makedirs("data/osm", exist_ok=True)

place = "Mumbai, India"

# Buildings
buildings = ox.features_from_place(place, tags={"building": True})
buildings.to_file("data/osm/mumbai_buildings.gpkg", driver="GPKG")

# Parks
parks = ox.features_from_place(place, tags={"leisure": "park"})
parks.to_file("data/osm/mumbai_parks.gpkg", driver="GPKG")

# Hospitals
hospitals = ox.features_from_place(place, tags={"amenity": "hospital"})
hospitals.to_file("data/osm/mumbai_hospitals.gpkg", driver="GPKG")

# Road Network
graph = ox.graph_from_place(place, network_type="drive")
ox.save_graph_geopackage(graph, filepath="data/osm/mumbai_roads.gpkg")

print("✅ OSM data downloaded and saved.")
