import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tiles_dir", help="Tiles Dir")
parser.add_argument("pred_dir", help="Preds Dir")
parser.add_argument("dload_dir", help="Preds Dir")
args = parser.parse_args()


tiles = [f.split(".gpkg")[0] for f in os.listdir(args.tiles_dir)]
predictions = [f.split(".gpkg")[0] for f in os.listdir(args.pred_dir)]
dloads = [f.split(".gpkg")[0] for f in os.listdir(args.dload_dir)]

if len(tiles) != len(predictions):
    print(f"Length Mismatch: {len(tiles)} (tiles) vs {len(predictions)} (predictions)")


nocrops = []
for t in tiles:
    if t in dloads:
        if ["NOCROP" in os.listdir(args.dload_dir + f"/{t}")]:
            print(f"No crop data for: {t}")
            nocrops.append(t)
        continue
    else:
        print(f"Couldn't find downloads for {t}")



for t in tiles:
    if t in predictions:
        continue
    else:
        if t not in nocrops:
            print(f"Couldn't find predictions for {t}")