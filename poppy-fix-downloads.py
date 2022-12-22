import argparse

parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="What dir should I ue for generating data")
parser.add_argument("--n_cores", type=int, help="Number of cores to use")
args = parser.parse_args()
DATA_DIR = args.data_dir
N_CORES = 1
if args.n_cores:
    N_CORES = args.n_cores


# DATA_DIR = "../../data"
# N_CORES = 10

import geopandas as gpd
import numpy as np
import os
import pandas as pd
from utils.rasters import RasterGenerationHelper
from utils.shapefile import ShapefileHelper
import time
from pathlib import Path
import shutil

TILE_DIR = f'{DATA_DIR}/interim/tiles'
PARENT_GDF = f'{DATA_DIR}/interim/parent.gpkg'
REDO_GDF = f'{DATA_DIR}/interim/redo.gpkg'

def get_missing():
    parent = gpd.read_file(PARENT_GDF)
    _all_ids = set(parent['pgrid_id'])
    _downloaded_ids = set([int(file.split(".tif")[0]) for file in os.listdir(TILE_DIR)])
    missing = _all_ids - _downloaded_ids
    missing_gdf = parent[parent['pgrid_id'].isin(list(missing))]
    if len(missing_gdf) > 0:
        missing_gdf.to_file(f"{DATA_DIR}/interim/redo.gpkg", driver="GPKG")
    return missing

complete = False
tries = 0
while not complete:
    missing = get_missing()
    if len(missing) > 0 and tries < 5:
        print(f"#### Missing {len(missing)} tiles, redownloading..")
    
        _TILE_OUTPUT_DIR = f'{DATA_DIR}/interim/tiles'
        _PATH_TO_PARENT_GRID = f"{DATA_DIR}/interim/redo.gpkg"
        _PATH_TO_CHILD_GRID = f"{DATA_DIR}/interim/child.gpkg"
        _N_CORES = N_CORES

        if os.path.exists(_TILE_OUTPUT_DIR):
            shutil.rmtree(_TILE_OUTPUT_DIR)

#         shutil.rmtree(_TILE_OUTPUT_DIR)
        Path(_TILE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        rgh = RasterGenerationHelper(_PATH_TO_PARENT_GRID, _PATH_TO_CHILD_GRID, _TILE_OUTPUT_DIR, _N_CORES, clean = True, post_period_days = [30,45])
        rgh.get_rasters()
        tries += 1
    else:
        if len(missing) == 0:
            print(f"#### Missing {len(missing)} tiles, DOWNLOAD COMPLETE..")
        else:
            print(f"#### Missing {len(missing)} tiles, but moving on..")

        complete = True


    