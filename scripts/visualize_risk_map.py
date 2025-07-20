import folium
import os
import geopandas as gpd
import rasterio
from rasterio.plot import reshape_as_image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from branca.colormap import linear

# Step 1: Path
raster_path = "processed/risk_layer.tif"

# Step 2: Read raster
with rasterio.open(raster_path) as src:
    data = src.read(1)
    bounds = src.bounds

# Step 3: Normalize values (0 to 1)
data = np.where(np.isnan(data), 0, data)
norm = (data - np.min(data)) / (np.max(data) - np.min(data))

# Step 4: Generate colormap (red=high risk, green=low)
cmap = cm.get_cmap('RdYlGn_r')
rgba_img = cmap(norm)
rgb_img = (rgba_img[:, :, :3] * 255).astype(np.uint8)

# Step 5: Save temporary PNG image
temp_image = "processed/risk_map_overlay.png"
plt.imsave(temp_image, rgb_img)

# Step 6: Define bounds
image_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

# Step 7: Create map
m = folium.Map(location=[(bounds.top + bounds.bottom)/2, (bounds.left + bounds.right)/2],
               zoom_start=11)

# Step 8: Add overlay
folium.raster_layers.ImageOverlay(
    name="Risk Layer",
    image=temp_image,
    bounds=image_bounds,
    opacity=0.6,
).add_to(m)

# Step 9: Add colormap legend
colormap = linear.RdYlGn_11.scale(0, 1).to_step(10)
colormap.caption = 'Risk Level (Red = High Risk)'
colormap.add_to(m)

# Step 10: Save map
map_path = "processed/risk_map.html"
m.save(map_path)
print(f"✅ Risk map saved at {map_path}")
