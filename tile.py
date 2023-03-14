import argparse
from pathlib import Path
import geopandas as gpd
import os

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("out_dir", help="Out")
parser.add_argument("--resolution", help="Resolution")
args = parser.parse_args()

RESOLUTION = 50000

if args.resolution:
    RESOLUTION=int(args.resolution)

from utils.shapefile import ShapefileHelper

Path(args.out_dir).mkdir(parents=True, exist_ok=True)

sh = ShapefileHelper(args.shp, args.out_dir)
sh.make_grid(RESOLUTION, "grid");

GRID_PATH = f"{args.out_dir}/grid.gpkg"
grid = gpd.read_file(GRID_PATH)

for i, tile in grid.iterrows():
    temp = gpd.GeoDataFrame(grid.iloc[i]).transpose()
    temp = temp[['grid_id', 'geometry']]
    temp['grid_id'] = temp['grid_id'].astype('int')
    temp.columns = ['GID', 'geometry']
    temp = temp.set_crs("epsg:4326")
    temp.to_file(f'{args.out_dir}/{temp.iloc[0][0]}.gpkg')

os.remove(f"{args.out_dir}/grid.gpkg")