import argparse

parser = argparse.ArgumentParser()

parser.add_argument("data_dir", help="What dir should I use for generating data")
parser.add_argument("shp", help="Shapefile")

args = parser.parse_args()

DATA_DIR = args.data_dir
SHP_FILE = args.shp


from utils.shapefile import ShapefileHelper
import geopandas as gpd
from pathlib import Path
import os
import shutil

INTERIM_DIR = f'{DATA_DIR}/interim'
Path(INTERIM_DIR).mkdir(parents=True, exist_ok=True)
sh = ShapefileHelper(SHP_FILE, INTERIM_DIR)
sh.make_grid(25000, "grid");

GRID_PATH = f"{INTERIM_DIR}/grid.gpkg"
grid = gpd.read_file(GRID_PATH)

for i, tile in grid.iterrows():
    temp = gpd.GeoDataFrame(grid.iloc[i]).transpose()
    temp = temp[['grid_id', 'geometry']]
    temp['grid_id'] = temp['grid_id'].astype('int')
    temp.columns = ['GID', 'geometry']
    temp = temp.set_crs("epsg:4326")
    temp.to_file(f'{INTERIM_DIR}/{temp.iloc[0][0]}.gpkg')
    
grids = [tile for tile in os.listdir(INTERIM_DIR) if tile != "grid.gpkg" and  tile != ".ipynb_checkpoints"]

DNQ_DIR = f"{INTERIM_DIR}/dnq"
if os.path.exists(DNQ_DIR):
    shutil.rmtree(DNQ_DIR)
for grid in grids:
    temp = grid.split(".gpkg")[0]
    Path(f"{DNQ_DIR}/{temp}/inputs").mkdir(parents=True, exist_ok=True)
#     shutil.copy2(f"{DATA_DIR}/inputs/2019_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif",f"{DNQ_DIR}/{temp}/inputs")