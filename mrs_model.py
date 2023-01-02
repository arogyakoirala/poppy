import zarr
import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from pathlib import Path
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("zarr", help="Data zarr location")
parser.add_argument("--data_dir", help="Data Dir")
parser.add_argument("--n", help="N")
parser.add_argument("--run_id", help="Run ID or label")
args = parser.parse_args()

DATA_DIR = "../data"
N = 3
RUN_ID = f"kmeans_{N}"



if args.data_dir:
    DATA_DIR=args.data_dir

if args.n:
    N = int(args.n)

if args.run_id:
    RUN_ID = args.run_id

print(f"""
   N = {N},
   DATA_DIR = {DATA_DIR},
   RUN_ID = {RUN_ID} 
""")

data = zarr.open(args.zarr)

data = data[:]
data = pd.DataFrame(data)
data['ndvi'] = (data[7]-data[3])/(data[7]+data[3])
for col in range(0,12):    
    data[col] = data[col+12] - data[col]

data = data[[*range(0,12), 26,'ndvi']]
data = data[-data['ndvi'].isna()]
# data.isna()
data = data[data['ndvi'] > 0.0]
data.columns = data.columns.astype(str)

print(f"""
   Training using {len(data)} pixels
""")

scaler = StandardScaler()
scaler.fit(data)
normalised_data = scaler.transform(data)

model = KMeans(n_clusters=N, init="k-means++", n_init=3)
model.fit(normalised_data)

MODEL_DIR = f'{DATA_DIR}/outputs/models/{RUN_ID}'
Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

with open(f'{MODEL_DIR}/model.pickle', 'wb') as f:
    pickle.dump(model, f)
        
with open(f'{MODEL_DIR}/scaler.pickle', 'wb') as f:
    pickle.dump(scaler, f)


