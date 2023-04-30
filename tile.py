import argparse
from pathlib import Path
import geopandas as gpd
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("out_dir", help="Out")
parser.add_argument("--resolution", help="Resolution")
parser.add_argument("--subset", help="Subset District IDs")
args = parser.parse_args()

RESOLUTION = 50000
SUBSET = None


subset_dict = {
    "hfp_2019": [2308, 2302, 2306, 2304, 2303, 2407, 2307, 2311, 1906, 1905, 2601, 2312, 2605, 2105, 1608, 1606, 2416, 2313, 1115, 2604, 2301, 2205, 2305, 3106, 2106, 2111, 2415, 1607, 1116, 2706, 809, 2406, 2408, 2603],
    "hfp_2020": [2308, 2302, 2306, 2304, 1906, 2303, 2407, 1905, 2311, 2307, 1903, 2601, 2105, 2312, 2313, 1904, 1115, 2416, 2605, 2205, 2604, 2106, 1608, 2305, 2415, 1606, 3106, 2111, 1803, 2705, 2301, 1607, 805, 1116, 2603],
    "nadali_qandahar": [2308, 2416]
    "all": [2304, 2305, 2306, 2307, 2308, 2309, 2311, 2312, 2313, 1803, 2705, 2706, 2205, 3106, 804, 805, 2601, 809, 2603, 2604, 2605, 1711, 2103, 2105, 2106, 2111, 1606, 1607, 1608, 2506, 1115, 1116, 2403, 2405, 2406, 2407, 2408, 2415, 2416, 1905, 1906, 1903, 1904, 2301, 2302, 2303]
}

# prefix = os.path.split(args.shp)[-1].split(".gpkg")[0]


if args.resolution:
    RESOLUTION=int(args.resolution)

if args.subset:
    SUBSET = [f"{str(f)}.gpkg" for f in subset_dict[args.subset]]

print("Generating tiles for:", SUBSET)


from utils.shapefile import ShapefileHelper

Path(args.out_dir).mkdir(parents=True, exist_ok=False)

shps = [f for f in os.listdir(args.shp) if f != '.DS_Store']

if SUBSET is not None:
    shps = SUBSET

for shp in shps:
    prefix=shp.split(".gpkg")[0]
    sh = ShapefileHelper(f"{args.shp}/{shp}", args.out_dir)
    sh.make_grid(RESOLUTION, "grid");

    GRID_PATH = f"{args.out_dir}/grid.gpkg"
    grid = gpd.read_file(GRID_PATH)

    # Create tiles at specific resolution for all shapefiles in a given directory
    for i, tile in grid.iterrows():
        temp = gpd.GeoDataFrame(grid.iloc[i]).transpose()
        temp = temp[['grid_id', 'geometry']]
        temp['grid_id'] = temp['grid_id'].astype('int')
        temp.columns = ['GID', 'geometry']
        temp = temp.set_crs("epsg:4326")
        temp.to_file(f'{args.out_dir}/{prefix}_{temp.iloc[0][0]}.gpkg')
    os.remove(f"{args.out_dir}/grid.gpkg")