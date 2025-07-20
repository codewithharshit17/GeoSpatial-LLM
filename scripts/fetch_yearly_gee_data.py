import ee
import geemap
import os

# Initialize Earth Engine with project
ee.Initialize(project='sixth-aloe-462909-s2')

# Define years for animation
years = list(range(2015, 2025))

# Define Mumbai boundary (adjust if needed)
mumbai = ee.Geometry.Rectangle([72.77, 18.89, 72.99, 19.30])

# Output folders
os.makedirs("data/gee", exist_ok=True)

for year in years:
    print(f"Processing year: {year}")

    # NDVI
    ndvi_collection = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterDate(f"{year}-04-01", f"{year}-06-30") \
        .filterBounds(mumbai) \
        .select("NDVI") \
        .mean().clip(mumbai)

    ndvi_out = f"data/gee/yearly_ndvi_{year}.tif"
    geemap.download_ee_image(
        image=ndvi_collection,
        filename=ndvi_out,
        region=mumbai,
        scale=250,
        crs='EPSG:4326'
    )
    print(f"✅ Saved NDVI for {year}")

    # LST
    lst_collection = ee.ImageCollection("MODIS/061/MOD11A1") \
        .filterDate(f"{year}-04-01", f"{year}-06-30") \
        .filterBounds(mumbai) \
        .select("LST_Day_1km") \
        .mean().clip(mumbai)

    lst_out = f"data/gee/yearly_lst_{year}.tif"
    geemap.download_ee_image(
        image=lst_collection,
        filename=lst_out,
        region=mumbai,
        scale=1000,
        crs='EPSG:4326'
    )
    print(f"✅ Saved LST for {year}")

print("🎉 All yearly NDVI and LST images downloaded.")
