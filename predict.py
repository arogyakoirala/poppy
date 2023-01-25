import argparse
import os
import shutil
from pathlib import Path
import pickle
import zarr
import numpy as np
import pandas as pd
import rioxarray as rxr
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from rasterio.windows import Window
from shapely.geometry import box
import shutil
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans
# from sklearn.mixture import GaussianMixture

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="Path to Shapefile")
parser.add_argument("model", help="Path to model")
parser.add_argument("--mask", help="Path to mask if available")
parser.add_argument("--year", help="Year")
parser.add_argument("--interim_dir", help="Interim")
parser.add_argument("--out_dir", help="Out Dir")
args = parser.parse_args()

SHP = args.shp
MODEL = args.model

INTERIM_DIR = "prediction_interim"
OUT_INTERIM_DIR = "out_interim"
OUT_DIR = "out"
YEAR = "2019"
MASK = None

if args.out_dir:
    OUT_DIR=args.out_dir

if args.interim_dir:
    INTERIM_DIR=args.interim_dir

if args.mask:
    MASK=args.mask

if args.year:
    YEAR=args.year


if os.path.exists(INTERIM_DIR):
    shutil.rmtree(INTERIM_DIR)
Path(INTERIM_DIR).mkdir(exist_ok=False, parents=True)

if os.path.exists(OUT_INTERIM_DIR):
    shutil.rmtree(OUT_INTERIM_DIR)
Path(OUT_INTERIM_DIR).mkdir(exist_ok=False, parents=True)
        
if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR)
Path(OUT_DIR).mkdir(exist_ok=True, parents=True)

if MASK is not None:
    os.system(f"python -u download.py --shp {SHP} --out_dir {OUT_INTERIM_DIR} --interim_dir {INTERIM_DIR} --n_cores 1 --year {YEAR}")
else:
    os.system(f"python -u download.py --shp {SHP} --out_dir {OUT_INTERIM_DIR} --interim_dir {INTERIM_DIR} --n_cores 1 --year {YEAR} --mask {MASK}")


with open(f'{MODEL}/run_metadata.txt') as f:
    lines = f.readlines()

TYPE = lines[0].split("-")[0]
N = int(lines[0].split("-")[1])

print(lines[0])

with open(f"{MODEL}/scaler.pkl", 'rb') as f:
    scaler = pickle.load(f)

with open(f"{MODEL}/model.pkl", 'rb') as f:
    model = pickle.load(f)

DATA = f"{OUT_INTERIM_DIR}/sample.zarr"
DATA = zarr.open(DATA)[:]
DATA = DATA[:, :-1]
X = DATA[:, 2:]

NORM = scaler.transform(X)

if TYPE == 'kmeans':
    PREDS = model.predict(NORM)
    PREDS = np.array(PREDS)
    PREDS = PREDS.reshape(PREDS.shape[0], 1)

    RES = DATA[:, [0,1,14]]
    RES = np.hstack((RES, PREDS))
    RES = pd.DataFrame(RES, columns = ['y','x','ndvi','cluster'])

    INPUT_RASTER = SHP.split("/")[-1].split(".gpkg")[0]

    with rasterio.open(f"{OUT_INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
        profile = src.profile
    crs = profile['crs']
    transform = profile['transform']
            
    RES = RES.drop_duplicates(subset=['y', 'x'])
    RES = RES.sort_values(['y', 'x'], ascending=False)
    # RES = RES.set_coords(['x', 'y'])

if TYPE == "gmm":
    PREDS = model.predict_proba(NORM)
    
    
    MAX_VAL = np.amax(PREDS, 1)
    MAX_VAL = np.array(MAX_VAL)
    MAX_VAL = MAX_VAL.reshape(MAX_VAL.shape[0], 1)
    
    MAX_I = np.argmax(PREDS, 1)
    MAX_I = np.array(MAX_I)
    MAX_I = MAX_I.reshape(MAX_I.shape[0], 1)

    RES = DATA[:, [0,1,14]]
    RES = np.hstack((RES, MAX_VAL))
    RES = np.hstack((RES, MAX_I))

    RES = pd.DataFrame(RES, columns = ['y','x','ndvi','cluster_prob', 'cluster'])

    INPUT_RASTER = SHP.split("/")[-1].split(".gpkg")[0]

    with rasterio.open(f"{OUT_INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
        profile = src.profile
    crs = profile['crs']
    transform = profile['transform']

    RES = RES.drop_duplicates(subset=['y', 'x'])
    print(RES.shape)

    RES = RES[RES['cluster_prob']>0.9]
    RES = RES.sort_values(['y', 'x'], ascending=False)

RES_ = RES
RES = RES.set_index(['y', 'x']).to_xarray()
RES.cluster.rio.to_raster(f"{OUT_DIR}/predictions.tif")

s = rasterio.open(f"{OUT_INTERIM_DIR}/{INPUT_RASTER}.tif")
x_lb = (s.width//2) - (s.width//4)
x_ub = (s.width//2) + (s.width//4)
y_lb = (s.height//2) - (s.height//4)
y_ub = (s.height//2) + (s.height//4)

n_images = 8
fig, ax = plt.subplots(3,n_images,figsize=(8*n_images,3*n_images), dpi=50)
ax=ax.flatten()

for i in range(n_images):
    x = np.random.randint(x_lb, x_ub)
    y = np.random.randint(y_lb, y_ub)
    with rasterio.open(f"{OUT_INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
        window = Window(x, y, 100, 100)
        pre = src.read((4,3,2), window=window)
        post = src.read((16,15,14), window=window)
        show(pre, ax=ax[i], adjust=True)
        show(post, ax=ax[n_images+i],  adjust=True)
    bounds = rasterio.windows.bounds(window, src.transform)
    bbox = box(minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3])
    pred_ = rxr.open_rasterio(f"{OUT_DIR}/predictions.tif")
    pred_ = pred_.rio.write_crs("epsg:4326", inplace=True)
    pred_clip = pred_.rio.clip_box(minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3])
    pred_clip.plot(ax=ax[n_images+n_images+i], add_colorbar=False)
    ax[n_images+n_images+i].set_xticks([])
    ax[n_images+n_images+i].set_yticks([])
    ax[n_images+n_images+i].set(xlabel=None, ylabel=None)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/plot_predictions_{TYPE}_{N}.png')


fig, ax = plt.subplots(N, 1, dpi=70, figsize=(9,9))
ax=ax.flatten()
    
for i in range(0,N):
    data = RES_[RES_['cluster']==i]['ndvi']
    ax[i].hist(data, bins=100)
    ax[i].set_title(f"k={N}; cluster={i}")
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/plot_ndvi_dist_{TYPE}_{N}.png')


pd.DataFrame(RES_.groupby('cluster').count()['ndvi']/100).rename(columns={'ndvi': 'clustering_ha'}).to_csv(f'{OUT_DIR}/cluster_dist_{TYPE}_{N}.csv')

shutil.rmtree(OUT_INTERIM_DIR)
shutil.rmtree(PREDICT_INTERIM_DIR)






    