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

INTERIM_DIR ="interim"
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


# idir_split = args.out_dir.rsplit("/", 1)
# INTERIM_DIR = f"{idir_split[0].join("/")}/{idir_split[1]}_interim"

# if os.path.exists(INTERIM_DIR):
#     shutil.rmtree(INTERIM_DIR)
# Path(INTERIM_DIR).mkdir(exist_ok=False, parents=True)    

# if os.path.exists(INTERIM_DIR):
#     shutil.rmtree(INTERIM_DIR)
# Path(INTERIM_DIR).mkdir(exist_ok=False, parents=True)

# if os.path.exists(OUT_DIR):
#     shutil.rmtree(OUT_DIR)
# Path(OUT_DIR).mkdir(exist_ok=False, parents=True)
        
# if os.path.exists(OUT_DIR):
#     shutil.rmtree(OUT_DIR)
# Path(OUT_DIR).mkdir(exist_ok=True, parents=True)

print(f"""

    Starting prediction step...
    
    Run parameters:

        SHP = {SHP}
        MODEL = {MODEL}
        INTERIM_DIR = {INTERIM_DIR}
        OUT_DIR = {OUT_DIR}
        YEAR = {YEAR}
        MASK = {MASK} 

""")


# if MASK is not None:
#     os.system(f"python -u download.py --shp {SHP} --out_dir {OUT_DIR} --interim_dir {INTERIM_DIR} --n_cores 1 --year {YEAR}")
# else:
os.system(f"python -u download.py --shp {SHP} --out_dir {OUT_DIR} --interim_dir {INTERIM_DIR} --n_cores 1 --year {YEAR} --mask {MASK}")


def compute_euclidean(x, y):
    return np.sqrt(np.sum((x-y)**2))

with open(f'{MODEL}/run_metadata.txt') as f:
    lines = f.readlines()

TYPE = lines[0].split("-")[0]
N = int(lines[0].split("-")[1])

print(lines[0])

with open(f"{MODEL}/scaler.pkl", 'rb') as f:
    scaler = pickle.load(f)

with open(f"{MODEL}/model.pkl", 'rb') as f:
    model = pickle.load(f)

DATA = f"{OUT_DIR}/sample.zarr"
DATA = zarr.open(DATA)[:]
DATA = DATA[:, :-1]
DATA = DATA[~np.isnan(DATA).any(axis=1)]

X = DATA[:, 2:]

NORM = scaler.transform(X)

np.random.seed(42)

def getDistances(a, b):
    aSumSquare = np.sum(np.square(a),axis=1)
    bSumSquare = np.sum(np.square(b),axis=1)
    mul = np.dot(a,b.T)
    dists = np.sqrt(aSumSquare[:,np.newaxis]+bSumSquare-2*mul)
    return dists

if TYPE == 'kmeans':
    CENTROIDS =  model.cluster_centers_
    DISTANCES = getDistances(NORM, CENTROIDS)
    # print("^^^^^DISTANCES", DISTANCES)
    # print("^^^^^DISTANCES-SHAPE", DISTANCES.shape)

    _n = NORM.shape[1]
    _1_by_d = (1/DISTANCES)**(_n-1)
    _sigma_term = np.sum(_1_by_d, axis=1)
    _sigma_term = _sigma_term.reshape(_sigma_term.shape[0], 1)
    # print(_sigma_term)
    SCORES = np.divide(_1_by_d,_sigma_term)
    # print("^^^^^SCORES-SHAPE", SCORES)

    PREDS = model.predict(NORM) + 1
    PREDS = np.array(PREDS)
    PREDS = PREDS.reshape(PREDS.shape[0], 1)

    RES = DATA[:, [0,1,14]]
    RES = np.hstack((RES, PREDS, DISTANCES, SCORES))
    RES = pd.DataFrame(RES, columns = ['y','x','ndvi','cluster', "dist_centroid_0", "dist_centroid_1", "dist_centroid_2", "score_centroid_0",  "score_centroid_1",  "score_centroid_2"])

    INPUT_RASTER = SHP.split("/")[-1].split(".gpkg")[0]

    with rasterio.open(f"{INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
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

    with rasterio.open(f"{INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
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
RES.dist_centroid_0.rio.to_raster(f"{OUT_DIR}/dist_0.tif")
RES.dist_centroid_1.rio.to_raster(f"{OUT_DIR}/dist_1.tif")
RES.dist_centroid_2.rio.to_raster(f"{OUT_DIR}/dist_2.tif")
RES.score_centroid_0.rio.to_raster(f"{OUT_DIR}/score_0.tif")
RES.score_centroid_1.rio.to_raster(f"{OUT_DIR}/score_1.tif")
RES.score_centroid_2.rio.to_raster(f"{OUT_DIR}/score_2.tif")


s = rasterio.open(f"{INTERIM_DIR}/{INPUT_RASTER}.tif")
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
    with rasterio.open(f"{INTERIM_DIR}/{INPUT_RASTER}.tif") as src:
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


RESULTS = pd.DataFrame(RES_.groupby('cluster').count()['ndvi']/100).rename(columns={'ndvi': 'clustering_ha'})
RESULTS.to_csv(f'{OUT_DIR}/cluster_dist_{TYPE}_{N}.csv')
# shutil.rmtree(OUT_DIR)
# shutil.rmtree(INTERIM_DIR)


for i in range(N):
    for j in np.linspace(0,1,6):
        RESULTS = pd.DataFrame(RES_)
        RESULTS = RESULTS[RESULTS[f"score_centroid_{i}"]>=j]
        RESULTS = pd.DataFrame(RESULTS.groupby('cluster').count()['ndvi']/100).rename(columns={'ndvi': 'clustering_ha'})
        RESULTS.to_csv(f'{OUT_DIR}/{TYPE}_{N}_K_{i}_dist_score_gte_{int(np.round(j*100))}.csv')


print(f"QC: Completed prediction process for: {SHP}")


    