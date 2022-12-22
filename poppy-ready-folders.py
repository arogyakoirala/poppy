#%%
import time
from utils.shapefile import ShapefileHelper
import os
from pathlib import Path


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="Path to directory")
parser.add_argument("shp_dir", help="A folder containing all shapefiles for which to predict")
args = parser.parse_args()

SHP_DIR = args.shp_dir
DATA_DIR = args.data_dir

aois = os.listdir(SHP_DIR)

for aoi in aois:
    dist_id = aoi.split('.gpkg')[0]
    _VECTOR_OUTPUT_DIR = f"{DATA_DIR}/dnq"
    Path(_VECTOR_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


    aoi = f"{SHP_DIR}/{aoi}"
    sh = ShapefileHelper(aoi, _VECTOR_OUTPUT_DIR)
    sh.make_grid(resolution=25000, name="o", separate=True, prefix=dist_id, data_dir=DATA_DIR)





