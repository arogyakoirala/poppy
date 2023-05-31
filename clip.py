import argparse
import os
from pathlib import Path
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import shutil
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("pred_dir", help="Preds Dir")
parser.add_argument("out_dir", help="Out Dir")
parser.add_argument("mask_shp", help="Mask SHP")

args = parser.parse_args()

def clip(raster, shp, output, indices):
    vector=gpd.read_file(shp)


    with rasterio.open(raster) as src:
        vector=vector.to_crs("epsg:4326")
        # print(vector.crs)
        out_image, out_transform=mask(src,vector.geometry,crop=True, nodata=np.nan, indexes=indices)
        out_meta=src.meta.copy() # copy the metadata of the source DEM
        
    out_meta.update({
        "driver":"Gtiff",
        "height":out_image.shape[1], # height starts with shape[1]
        "width":out_image.shape[2], # width starts with shape[2]
        "transform":out_transform
    })
                
    with rasterio.open(output,'w',**out_meta) as dst:
        dst.write(out_image)


folders = [f for f in os.listdir(args.pred_dir)]
folders = filter(lambda f: f !='.DS_Store', folders)

for f in folders:
    Path(f'{args.out_dir}/{f}').mkdir(exist_ok=True, parents=True)
    if os.path.exists(f'{args.pred_dir}/{f}/predictions.tif'):
        print(f"Clipping {f}: Predictions")
        clip(f'{args.pred_dir}/{f}/predictions.tif', args.mask_shp,f'{args.out_dir}/{f}/predictions.tif', [1])
    else:
        print(f"No exist preds {f}")
    
    if os.path.exists(f'{args.pred_dir}/{f}/scores.tif'):
        print(f"Clipping {f}: Scores")
        clip(f'{args.pred_dir}/{f}/scores.tif', args.mask_shp,f'{args.out_dir}/{f}/scores.tif', [1,2,3])
    else:
        print(f"No exist scores {f}")

    if os.path.exists(f'{args.pred_dir}/{f}/distances.tif'):
        print(f"Clipping {f}: Distances")
        clip(f'{args.pred_dir}/{f}/distances.tif', args.mask_shp,f'{args.out_dir}/{f}/distances.tif', [1,2,3])
    else:
        print(f"No exist dists {f}")
