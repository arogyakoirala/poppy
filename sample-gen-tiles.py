import time
import geopandas as gpd
import argparse
from utils.shapefile import ShapefileHelper
from pathlib import Path
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("shp_path", help="Use a custom shapefile instead of aoi.gpkg")
parser.add_argument("--res", help="Resolution in meters")
parser.add_argument("--n", help="Number of samples")
args = parser.parse_args()
SHP_PATH = args.shp_path
RES = 5000
N = 200


if args.res:
    RES=int(args.res)


if args.n:
    N=int(args.n)

sh = ShapefileHelper(SHP_PATH, "./outputs")
sh.make_grid(resolution=RES, name="output")


grid = gpd.read_file("./outputs/output.gpkg")
all_dists = gpd.read_file("../poppydata/inputs/district398.gpkg")
ids = ["1103", "1115", "1607", "1608", "1711", "1905", "1906", "2105", "2106", "2111", "2205", "2301", "2302", "2303", "2304", "2305", "2306", "2307", "2308", "2309", "2311", "2313", "2406", "2407", "2408", "2415", "2416", "2601", "2603", "2604", "2605", "2705", "2706", "3106", "804", "809"]
ids = ["2308", "2302", "1809", "1906", "2304", "1905", "2309", "3103", "2306", "1904", "2303", "1702", "3101", "2601", "1608", "1701", "2407"]
all_dists = all_dists[all_dists['DISTID'].astype(str).isin(ids)]

## gdal_calc.py -A ../poppydata/inputs/2019_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif --outfile=result.tif --calc="A>=50" --NoDataValue=0

sample = gpd.sjoin(grid, all_dists)
vectorized_crop_mask =  gpd.read_file("../poppydata/inputs/vectorized_crop_mask.gpkg")
print(sample.columns)
print(vectorized_crop_mask.columns)
sample = gpd.sjoin(sample.drop('index_right', axis=1), vectorized_crop_mask, how='left')

print(len(sample))
sample = sample.sample(N)

if os.path.exists('./outputs/sample_tiles'):
    shutil.rmtree('./outputs/sample_tiles')
Path('./outputs/sample_tiles').mkdir(parents=True, exist_ok=True)

for i, tile in sample.iterrows():
    temp = gpd.GeoDataFrame(grid.iloc[i]).transpose()
    temp = temp[['grid_id', 'geometry']]
    temp['gid'] = temp['grid_id'].astype('int')
    temp = temp.drop('grid_id', axis=1)
    temp.to_file(f'./outputs/sample_tiles/{i}.gpkg')
    

sample.to_file("./outputs/sample.gpkg", driver="GPKG")
print(sample.head())


