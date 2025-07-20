import os
import rasterio
from rasterio.warp import transform
from shapely.geometry import box
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import geopandas as gpd
import numpy as np

# Define all recognized Mumbai sub-regions
all_regions = [
    "mumbai", "kurla", "dharavi", "chembur", "govandi", "bandra", "thane", "bhandup",
    "ghatkopar", "andheri", "malad", "borivali", "mulund", "vikhroli", "sion", "trombay",
    "jogeshwari", "kandivali", "vile parle", "chandivali", "khar", "vidyavihar", "goregaon"
]

# Folder paths
NDVI_PATH = "data/gee/yearly_ndvi_2023.tif"
LST_PATH = "data/gee/lst_series/lst_2022.tif"

# Cache geocoder
geolocator = Nominatim(user_agent="geo-llm")

def geocode_location(region):
    try:
        loc = geolocator.geocode(f"{region}, Mumbai, India", timeout=3)
        if loc:
            return loc.latitude, loc.longitude
    except:
        return None
    return None

def extract_raster_value(raster_path, lat, lon):
    try:
        with rasterio.open(raster_path) as src:
            coords = transform({'init': 'EPSG:4326'}, src.crs, [lon], [lat])
            x, y = coords[0][0], coords[1][0]
            row, col = src.index(x, y)

            value = src.read(1)[row, col]
            if value == src.nodata:
                return None
            return round(float(value), 3)
    except Exception as e:
        print(f"Error reading raster: {e}")
        return None

def get_ndvi_value(region):
    location = geocode_location(region)
    if location:
        lat, lon = location
        return extract_raster_value(NDVI_PATH, lat, lon)
    return None

def get_lst_value(region):
    location = geocode_location(region)
    if location:
        lat, lon = location
        return extract_raster_value(LST_PATH, lat, lon)
    return None

def get_max_lst_region():
    path = LST_PATH
    if not os.path.exists(path):
        return None, None
    try:
        with rasterio.open(path) as src:
            data = src.read(1)
            data[data == src.nodata] = np.nan
            max_val = np.nanmax(data)
            max_idx = np.unravel_index(np.nanargmax(data), data.shape)
            lon, lat = src.xy(*max_idx)
            return round(max_val, 2), (lat, lon)
    except Exception as e:
        print("Error reading LST:", e)
        return None, None

# ✅ NEW: Get lowest NDVI region
def get_lowest_ndvi_region():
    path = NDVI_PATH
    if not os.path.exists(path):
        return None, None
    try:
        with rasterio.open(path) as src:
            data = src.read(1)
            data[data == src.nodata] = np.nan
            min_val = np.nanmin(data)
            min_idx = np.unravel_index(np.nanargmin(data), data.shape)
            lon, lat = src.xy(*min_idx)
            return round(min_val, 3), (lat, lon)
    except Exception as e:
        print("Error reading NDVI:", e)
        return None, None

# ✅ Replaces placeholder text in LLM response
def patch_placeholders(final_response):
    patched = final_response
    val1, coords1 = get_max_lst_region()
    val2, coords2 = get_lowest_ndvi_region()

    if "[area with the maximum LST value]" in patched and val1 and coords1:
        patched = patched.replace(
            "[area with the maximum LST value]",
            f"{coords1} with LST of {val1}°C"
        )

    if "[specific geographical coordinates or names of the areas with the lowest vegetation]" in patched and val2 and coords2:
        patched = patched.replace(
            "[specific geographical coordinates or names of the areas with the lowest vegetation]",
            f"{coords2} with NDVI of {val2}"
        )

    return patched, coords1 or coords2
