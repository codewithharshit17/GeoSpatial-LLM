from geopy.geocoders import Nominatim
from shapely.geometry import box
import geopandas as gpd

def mark_llm_places(llm_response, map_obj=None):
    geolocator = Nominatim(user_agent="geo-llm", timeout=5)
    locations = []

    keywords = ["mumbai", "kurla", "dharavi", "chembur", "govandi", "bandra", "thane"]
    for region in keywords:
        if region in llm_response.lower():
            try:
                location = geolocator.geocode(f"{region}, Mumbai, India")
            except:
                location = None

            if location:
                # Create a bounding box around the location
                buffer = 0.01  # degrees (~1 km area)
                polygon = box(location.longitude - buffer, location.latitude - buffer,
                              location.longitude + buffer, location.latitude + buffer)
                locations.append((region.title(), polygon))

                if map_obj:
                    gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon])
                    map_obj.add_gdf(gdf, layer_name=region.title(),
                                    style={"fillColor": "orange", "color": "black", "weight": 2})

    # Return first location center for zooming
    if locations:
        name, poly = locations[0]
        centroid = poly.centroid
        return [centroid.y, centroid.x]  # lat, lon
    return None
