import os
import rasterio
from rasterio.enums import Resampling
import numpy as np

# --- Normalization Function ---
def normalize(array):
    return (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))

# --- Save Raster Function ---
def save_raster(output_path, data, transform, crs):
    # Auto-create folder if missing
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(data, 1)

# --- File Paths ---
ndvi_path = "data/gee/mumbai_ndvi.tif"
lst_path = "data/gee/mumbai_lst.tif"
output_path = "processed/risk_layer.tif"

# --- Load NDVI as reference ---
with rasterio.open(ndvi_path) as ndvi_src:
    ndvi = ndvi_src.read(1)
    transform = ndvi_src.transform
    crs = ndvi_src.crs
    shape = ndvi.shape

# --- Load and resample LST ---
with rasterio.open(lst_path) as lst_src:
    lst = lst_src.read(1, out_shape=shape, resampling=Resampling.bilinear)

# --- Normalize & Combine ---
ndvi_norm = normalize(ndvi)
lst_norm = normalize(lst)
ndvi_inverted = 1 - ndvi_norm

risk = (ndvi_inverted * 0.6) + (lst_norm * 0.4)
save_raster(output_path, risk.astype(np.float32), transform, crs)

print(f"✅ Risk layer saved at {output_path}")
