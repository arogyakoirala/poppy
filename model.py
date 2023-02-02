import argparse
import zarr
import numpy as np
import pickle
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture

parser = argparse.ArgumentParser()

parser.add_argument("data", help="Data file path (ZARR format needed)")
parser.add_argument("model", help="Type of model")
parser.add_argument("n", help="N")
parser.add_argument("--out_dir", help="Out Dir")
parser.add_argument("--cutoff", help="N")

args = parser.parse_args()

DATA = args.data
MODEL = args.model
N = int(args.n)
OUT_DIR = "out"

if args.cutoff:
    CUTOFF = args.cutoff

if args.out_dir:
    OUT_DIR = args.out_dir

DATA = zarr.open(DATA)[:]
DATA = DATA[:, :-1]
DATA = DATA[:, 2:]
print(DATA.shape)

scaler = StandardScaler()
scaler.fit(DATA)
norm = scaler.transform(DATA)

_MODEL_PATH = f"{OUT_DIR}/model-{MODEL}-{N}"
Path(_MODEL_PATH).mkdir(parents=True, exist_ok=True)

with open(f'{_MODEL_PATH}/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)


print(np.any(np.isnan(norm)))

if MODEL=='kmeans':
    model = KMeans(n_clusters=N)
    model.fit(norm)

if MODEL=='gmm':
    model = GaussianMixture(N, covariance_type='full', random_state=0)
    model.fit(norm)

with open(f'{_MODEL_PATH}/model.pkl', 'wb') as f:
    pickle.dump(model, f)

metadata = open(f'{_MODEL_PATH}/run_metadata.txt', "w")
metadata.write(f"{MODEL}-{N}")
metadata.close()