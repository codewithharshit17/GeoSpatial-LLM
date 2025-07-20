import ee
import geemap
import os

ee.Initialize(project='sixth-aloe-462909-s2')

# Mumbai bounding box (approx)
region = ee.Geometry.Rectangle([72.775, 18.875, 72.985, 19.305])

years = list(range(2010, 2024))
ndvi_dir = "data/gee/ndvi_series"
lst_dir = "data/gee/lst_series"
os.makedirs(ndvi_dir, exist_ok=True)
os.makedirs(lst_dir, exist_ok=True)

for year in years:
    print(f"Processing year: {year}")

    # NDVI
    ndvi = (
        ee.ImageCollection("MODIS/006/MOD13Q1")
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .select("NDVI")
        .mean()
        .clip(region)
        .multiply(0.0001)  # scale NDVI
    )

    ndvi_path = os.path.join(ndvi_dir, f"ndvi_{year}.tif")
    geemap.ee_export_image(ndvi, filename=ndvi_path, scale=250, region=region)
    print(f"✅ Saved NDVI for {year}")

    # LST
    lst = (
        ee.ImageCollection("MODIS/006/MOD11A1")
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .select("LST_Day_1km")
        .mean()
        .clip(region)
        .multiply(0.02)
        .subtract(273.15)  # Kelvin to Celsius
    )

    lst_path = os.path.join(lst_dir, f"lst_{year}.tif")
    geemap.ee_export_image(lst, filename=lst_path, scale=1000, region=region)
    print(f"✅ Saved LST for {year}")
