import argparse
from pathlib import Path
import geopandas as gpd
import os

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("out", help="Out")
args = parser.parse_args()


from utils.shapefile import ShapefileHelper


Path(args.out).mkdir(parents=True, exist_ok=True)

sh = ShapefileHelper(args.shp, args.out)
sh.make_grid(10000, "grid");


GRID_PATH = f"{args.out}/grid.gpkg"
grid = gpd.read_file(GRID_PATH)

for i, tile in grid.iterrows():
    temp = gpd.GeoDataFrame(grid.iloc[i]).transpose()
    temp = temp[['grid_id', 'geometry']]
    temp['grid_id'] = temp['grid_id'].astype('int')
    temp.columns = ['GID', 'geometry']
    temp = temp.set_crs("epsg:4326")
    temp.to_file(f'{args.out}/{temp.iloc[0][0]}.gpkg')

os.remove(f"{args.out}/grid.gpkg")