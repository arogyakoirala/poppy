import argparse

parser = argparse.ArgumentParser()
parser.add_argument("shps_dir", help="Directory that contains shapefiles for which to generate data")
parser.add_argument("--out_dir", help="Where to store the predictions? By default will be stored in ../data/outputs")
args = parser.parse_args()
SHPS_DIR = args.shps_dir
OUT_DIR = "../data/outputs"

print(SHPS_DIR)

if args.out_dir:
    OUT_DIR = args.out_dir

from pathlib import Path
import os

Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

shps = [f for f in os.listdir(SHPS_DIR) if ".gpkg" in f]
for shp in shps:
    DATA_DIR = f"{OUT_DIR}/{shp.split('.gpkg')[0]}"
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    





