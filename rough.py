import rasterio

from rasterio.mask import mask
import geopandas as gpd
import shutil
import numpy as np

def clip(raster, shp, output):
    Vector=gpd.read_file(shp)


    with rasterio.open(raster) as src:
        Vector=Vector.to_crs("epsg:4326")
        # print(Vector.crs)
        out_image, out_transform=mask(src,Vector.geometry,crop=True, nodata=np.nan, indexes=[1,2,3])
        out_meta=src.meta.copy() # copy the metadata of the source DEM
        
    out_meta.update({
        "driver":"Gtiff",
        "height":out_image.shape[1], # height starts with shape[1]
        "width":out_image.shape[2], # width starts with shape[2]
        "transform":out_transform
    })
                
    with rasterio.open(output,'w',**out_meta) as dst:
        dst.write(out_image)



in_file = "server/debug/2308_3/scores.tif"
shp = "server/inputs/processed/afgmask60.gpkg"
out = "masked.tif"

clip(in_file, shp, out)