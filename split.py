conda activate poppy-linux

import argparse
from pathlib import Path
import geopandas as gpd
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("out_dir", help="Out")
args = parser.parse_args()


from utils.shapefile import ShapefileHelper

Path(args.out_dir).mkdir(parents=True, exist_ok=True)

afg = gpd.read_file(args.shp)

# print(afg)

for i, district in afg.iterrows():
    # print(district)
    _ = []
    id_ = district['DISTID']
    name_ = district['DIST_34_NA']
    prov_ = district['PROV_34_NA']
    _.append({"id": id_, "name":name_, "province": prov_, "geometry": district['geometry']})
    gdf = gpd.GeoDataFrame(_).explode()
    gdf.dissolve(by="name")
    gdf.to_file(f"{args.out_dir}/{id_}.gpkg", driver="GPKG")
    print(gdf.geometry)
