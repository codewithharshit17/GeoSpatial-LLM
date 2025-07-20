import ee
import geemap

ee.Initialize(project='sixth-aloe-462909-s2')  # Replace with your GEE project ID

# Define region of interest: Mumbai
roi = ee.Geometry.Rectangle([72.77, 18.89, 72.98, 19.30])  # Adjust to exact Mumbai bbox

# NDVI
ndvi = ee.ImageCollection("MODIS/061/MOD13Q1") \
         .filterDate('2024-01-01', '2024-12-31') \
         .select('NDVI') \
         .mean() \
         .clip(roi)

# LST
lst = ee.ImageCollection("MODIS/061/MOD11A1") \
        .filterDate('2024-01-01', '2024-12-31') \
        .select('LST_Day_1km') \
        .mean() \
        .clip(roi)

# Export
geemap.ee_export_image(
    ndvi,
    filename='data/gee/mumbai_ndvi.tif',
    scale=250,  # try 250, or even 100 if MODIS allows
    region=roi,
)

geemap.ee_export_image(
    lst,
    filename='data/gee/mumbai_lst.tif',
    scale=1000,
    region=roi,
)
