import rasterio
import matplotlib.pyplot as plt
import os

def plot_raster(file_path, title):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with rasterio.open(file_path) as src:
        data = src.read(1)
        plt.figure(figsize=(8, 6))
        plt.title(title)
        plt.imshow(data, cmap='viridis')
        plt.colorbar(label='Value')
        plt.axis('off')
        plt.show()

# Paths to NDVI and LST
ndvi_path = "data/gee/mumbai_ndvi.tif"
lst_path = "data/gee/mumbai_lst.tif"

# Visualize NDVI
plot_raster(ndvi_path, "🌿 Mumbai NDVI (Vegetation Index)")

# Visualize LST
plot_raster(lst_path, "🌡️ Mumbai LST (Land Surface Temp.)")
