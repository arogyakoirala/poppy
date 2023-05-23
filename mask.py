
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

def clip(raster, shp, output):
    Vector=gpd.read_file(shp)


    with rasterio.open(raster) as src:
        print(src.crs)
        Vector=Vector.to_crs("epsg:4326")
        # print(Vector.crs)
        out_image, out_transform=mask(src,Vector.geometry,crop=True, nodata=np.nan)
        out_meta=src.meta.copy() # copy the metadata of the source DEM
        
    out_meta.update({
        "driver":"Gtiff",
        "height":out_image.shape[1], # height starts with shape[1]
        "width":out_image.shape[2], # width starts with shape[2]
        "transform":out_transform
    })
                
    with rasterio.open(output,'w',**out_meta) as dst:
        dst.write(out_image)

clip("server/2019-30day/predictions/r1/predictions.tif", "server/inputs/processed/afgmask85.gpkg", "output.tif")



# inshp = '/home/ec2-user/data/hybas_sa_lev01-12_v1c/hybas_sa_lev06_v1c.shp'
# inRas = '/home/ec2-user/data/SmallDEM_Testing.tif'
# outRas = '/home/ec2-user/data/ClippedSmallRaster.tif'





# import rasterio
# from rasterio.features import shapes
# mask = None
# with rasterio.Env():
#     with rasterio.open('a_raster') as src:
#         image = src.read(1) # first band
#         results = (
#         {'properties': {'raster_val': v}, 'geometry': s}
#         for i, (s, v) in enumerate(shapes(image, mask=mask, transform=src.transform)))




# import xarray as xr
# import numpy as np
# import rasterio as rio
# from shapely.geometry import box
# import geopandas as gpd
# from rasterio.mask import mask




# def getFeatures(gdf):
#     """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
#     import json
#     return [json.loads(gdf.to_json())['features'][0]['geometry']]


# def clip(preds, mask_):
#     mask_ = rio.open(mask_)
#     ra = rio.open(preds)
#     bounds  = ra.bounds
#     geom = box(*bounds)
#     df = gpd.GeoDataFrame({"id":1,"geometry":[geom]})
#     # df = df.to_crs(crs=ra.crs.data)
#     coords = getFeatures(df)
#     out_img, out_transform = mask(dataset=mask_, shapes=coords, crop=True) 

#     return out_img


# def masker(preds, mask, crop_proba):   
#     preds = xr.open_rasterio(preds)
#     mask = xr.open_rasterio(mask)

#     print(preds.shape)
#     print(mask.shape)
#     # preds = preds.where(mask >= crop_proba, other=np.nan)
#     # return preds




# a = clip("server/2019-30day/predictions/r2/predictions.tif", "inputs/mask.tif")
# print(a.shape)

# print(xr.open_rasterio("server/2019-30day/predictions/r2/predictions.tif").shape)