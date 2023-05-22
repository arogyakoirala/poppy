import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("tiles_dir", help="Tiles Dir")
parser.add_argument("pred_dir", help="Preds Dir")
args = parser.parse_args()


tiles = [f.split(".gpkg")[0] for f in os.listdir(args.tiles_dir)]
predictions = [f.split(".gpkg")[0] for f in os.listdir(args.pred_dir)]

if len(tiles) != len(predictions):
    print(f"Length Mismatch: {len(tiles)} (tiles) vs {len(predictions)} (predictions)")

for t in tiles:
    if t in predictions:
        continue
    else:
        print(f"Couldn't find predictions for {t} in {args.pred_dir}")