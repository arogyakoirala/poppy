from osgeo import gdal
import os

# files = [f'test/{f}' for f in os.listdir("test")]
# shp = "inputs/districts_tiled_15k/2416_3.gpkg"

# g = gdal.Warp("test/clipped.tif", files, format="GTiff",
#              cutlineDSName=shp,
#              cropToCutline=True)
# g = None


import argparse
from pathlib import Path
import geopandas as gpd
import os
import shutil
import rioxarray as rxr
from shapely.geometry import mapping
from rioxarray.merge import merge_arrays
import pandas as pd
import numpy as np
import zarr
import time
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle
import xarray as xr
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from rasterio.windows import Window
from shapely.geometry import box
import fiona

# Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("model_dir", help="Model Dir")
parser.add_argument("rasters_dir", help="Rasters Dir")
parser.add_argument("out_dir", help="Out")
args = parser.parse_args()


# Specify parameters
TRANSFORM = 'diff_bands'
NDVI_CUTOFF = 0.4
N = 3

# Folders
MDIR = args.model_dir 
ODIR = args.out_dir
Path(ODIR).mkdir(parents=True, exist_ok=False)
RDIR = args.rasters_dir

IMGDIR = f"{ODIR}/images"
Path(IMGDIR).mkdir(parents=True, exist_ok=True)

TDIR = f'{ODIR}/tables'
Path(TDIR).mkdir(parents=True, exist_ok=True)

# Load Model
def load_model(d):
    _ = open(f"{d}/model.pkl",'rb')
    model = pickle.load(_)
    _ = open(f"{d}/scaler.pkl",'rb')
    scaler = pickle.load(_)
    return model, scaler
model, scaler = load_model(MDIR)

# Adds NDVI Values to data
def add_ndvi(df, b8, b4, label):
    df[label] = (df[b8] - df[b4]) / (df[b8] + df[b4]) 
    return df

# Removes NaNs
def remove_nans(df):
   return df[~np.isnan(df).any(axis=1)]

def get_roa_raster(shp_path):
    files = [f'{RDIR}/out/all/{f}' for f in os.listdir(f"{RDIR}/out/all")]
    MERGED_DIR = f"{ODIR}/merged"
    Path(MERGED_DIR).mkdir(parents=True, exist_ok=True)
    out = shp_path.split("/")[-1].split(".gpkg")[0]
    g = gdal.Warp(f"{MERGED_DIR}/{out}.tif", files, format="GTiff",
             cutlineDSName=shp_path,
             cropToCutline=True)
    clipped_raster = rxr.open_rasterio(f"{MERGED_DIR}/{out}.tif")
    return clipped_raster


def apply_transform(df):
    if TRANSFORM == 'diff_bands':
        for col in range(1,13):
            df[col] = df[col+12] - df[col]
        df['diff_ndvi'] = df['ndvi_post'] - df['ndvi_pre']
        df = df[[*range(1,13), 'diff_ndvi']]
    return df

# Raster to numpy array, 
# Output: vector containing pre-NDVI for all qualified pixels + numpy array of dataset.
def prep_data(clipped):
    df = clipped.to_dataframe(name='band_value')
    df = df.reset_index()
    df.columns = ['band', 'y', 'x', 'spatial_ref', 'value']
    df = pd.pivot(df, index = ['y', 'x'], columns=['band'], values=['value']).reset_index()
    cols = [*df.columns.get_level_values(0)[0:2], *df.columns.get_level_values(1)[2:]]
    df.columns = df.columns.to_flat_index()
    df.columns = cols

    df = df.set_index(['y', 'x'])
    df = add_ndvi(df, 8, 4, "ndvi_pre")
    df = add_ndvi(df, 20, 16, "ndvi_post")


    temp = df.isna().any(axis=1)
    nas = df[temp]

    lt_cutoff = df[df['ndvi_pre'] < NDVI_CUTOFF]
    unqualified = pd.concat([nas, lt_cutoff])


    df = remove_nans(df)
    df = df[df['ndvi_pre'] > NDVI_CUTOFF]
    ndvis = df.reset_index()['ndvi_pre'] # save pre ndvis for future plotting

    
    df = apply_transform(df)

    unqualified = apply_transform(unqualified)
    # # Apply required data transformation
    # if TRANSFORM == 'diff_bands':
    #     for col in range(1,13):
    #         df[col] = df[col+12] - df[col]
    #     df['diff_ndvi'] = df['ndvi_post'] - df['ndvi_pre']
    #     df = df[[*range(1,13), 'diff_ndvi']]
   
    return df.reset_index(), unqualified.reset_index(), ndvis

# Get distances for each pixel from model centroids
def get_distances_and_scores(norm, model):
    CENTROIDS =  model.cluster_centers_
    DISTANCES = get_dist(norm, CENTROIDS)

    _n = norm.shape[1]
    _1_by_d = (1/DISTANCES)**(_n-1)
    _sigma_term = np.sum(_1_by_d, axis=1)
    _sigma_term = _sigma_term.reshape(_sigma_term.shape[0], 1)
    SCORES = np.divide(_1_by_d,_sigma_term)
    return DISTANCES, SCORES

# helper function to calculate euclidian distance between two vectors
def get_dist(a, b):
    aSumSquare = np.sum(np.square(a),axis=1)
    bSumSquare = np.sum(np.square(b),axis=1)
    mul = np.dot(a,b.T)
    dists = np.sqrt(aSumSquare[:,np.newaxis]+bSumSquare-2*mul)
    return dists

# Generate prediction for each pixel
def predict_k_means(df, model, scaler, unqualified):
    DATA=df.to_numpy()
    UNQ=unqualified.to_numpy() 
    X = DATA[:, 2:]
    NORM = scaler.transform(X)
    DISTANCES, SCORES = get_distances_and_scores(NORM, model)

    PREDS = model.predict(NORM)
    PREDS = np.array(PREDS)
    PREDS = PREDS.reshape(PREDS.shape[0], 1)
    RESULTS = DATA[:, [0,1,14]]
    RESULTS = np.hstack((RESULTS, PREDS, DISTANCES, SCORES))
    
    PREDS_UNQ = np.ones(len(unqualified)) * -1
    PREDS_UNQ = np.array(PREDS_UNQ)
    PREDS_UNQ = PREDS_UNQ.reshape(PREDS_UNQ.shape[0], 1)
    DISTANCES_UNQ = np.zeros(len(unqualified)*3).reshape((len(unqualified),3))
    SCORES_UNQ = np.zeros(len(unqualified)*3).reshape((len(unqualified),3))
    RESULTS_UNQ = UNQ[:, [0,1,14]]
    RESULTS_UNQ = np.hstack((RESULTS_UNQ, PREDS_UNQ, DISTANCES_UNQ, SCORES_UNQ))

    

    RESULTS = np.vstack((RESULTS, RESULTS_UNQ))
    RESULTS = pd.DataFrame(RESULTS, columns = ['y','x','ndvi','cluster', "dist_centroid_0", "dist_centroid_1", "dist_centroid_2", "score_centroid_0",  "score_centroid_1",  "score_centroid_2"])
    RESULTS = RESULTS.drop_duplicates(subset=['y', 'x'])
    RESULTS = RESULTS.sort_values(['y', 'x'], ascending=False)

    return RESULTS

# Save generated predictions
def save_tifs_pred(predictions, name, crs):
    PDIR = f"{ODIR}/predictions/{name}"
    Path(PDIR).mkdir(parents=True, exist_ok=True)
    predictions = predictions.set_index(['y', 'x']).to_xarray()
    predictions.cluster.rio.to_raster(f"{PDIR}/cluster.tif")
    predictions.dist_centroid_0.rio.to_raster(f"{PDIR}/d0.tif")
    predictions.dist_centroid_1.rio.to_raster(f"{PDIR}/d1.tif")
    predictions.dist_centroid_2.rio.to_raster(f"{PDIR}/d2.tif")
    predictions.score_centroid_0.rio.to_raster(f"{PDIR}/s0.tif")
    predictions.score_centroid_1.rio.to_raster(f"{PDIR}/s1.tif")
    predictions.score_centroid_2.rio.to_raster(f"{PDIR}/s2.tif")
    raw_files = [f"{PDIR}/{f}" for f in os.listdir(PDIR) if f != '.DS_Store']

    datasets = {f"predictions_{name}": ["cluster.tif"], "distances":["d0.tif", "d1.tif", "d2.tif"], "scores":["s0.tif", "s1.tif", "s2.tif"]}
    for s in datasets:
        files = (" ").join([f"{PDIR}/{f}" for f in datasets[s]])
        out_img = f"{PDIR}/{s}.tif"
        os.system(f"rio stack {files} -o {out_img}")
    for _f in raw_files:
        os.remove(_f)


# Save generated plots
def save_plots(predictions, name):
    fig, ax = plt.subplots(N, 1, dpi=70, figsize=(9,9))
    ax=ax.flatten()
    for i in range(0,N):
        data = predictions[predictions['cluster']==i]['ndvi']
        ax[i].hist(data, bins=100)
        ax[i].set_title(f"k={N}; cluster={i}")
    plt.tight_layout()
    plt.savefig(f'{IMGDIR}/{name}_ndvi.png')

# Save generated tables
def save_tables(predictions, name):
    counts = pd.DataFrame(predictions.groupby('cluster').count()['ndvi']/100).rename(columns={'ndvi': 'clustering_ha'})
    counts.to_csv(f"{TDIR}/{name}_acreage.csv")

# Save sample images with predictions for later use
def save_samples():
    np.random.seed(42)
    images = [f for f in os.listdir(IMGDIR) if f != '.DS_Store']
    for im in images:
        filename = im.split(".tif")[0]
        s = rasterio.open(f"{IMGDIR}/{im}")
        x_lb = (s.width//2) - (s.width//4)
        x_ub = (s.width//2) + (s.width//4)
        y_lb = (s.height//2) - (s.height//4)
        y_ub = (s.height//2) + (s.height//4)
        n_images = 8
        fig, ax = plt.subplots(3,n_images,figsize=(8*n_images,3*n_images), dpi=50)
        ax=ax.flatten()
        PDIR = f"{ODIR}/predictions/{filename}"
        for i in range(n_images):
            x = np.random.randint(x_lb, x_ub)
            y = np.random.randint(y_lb, y_ub)
            with rasterio.open(f"{IMGDIR}/{im}") as src:
                window = Window(x, y, 100, 100)
                pre = src.read((4,3,2), window=window)
                post = src.read((16,15,14), window=window)
                show(pre, ax=ax[i], adjust=True)
                show(post, ax=ax[n_images+i],  adjust=True)
            bounds = rasterio.windows.bounds(window, src.transform)
            bbox = box(minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3])
            pred_ = rxr.open_rasterio(f"{PDIR}/predictions.tif")
            pred_ = pred_.rio.write_crs("epsg:4326", inplace=True)
            pred_clip = pred_.rio.clip_box(minx=bounds[0], miny=bounds[1], maxx=bounds[2], maxy=bounds[3])
            pred_clip.plot(ax=ax[n_images+n_images+i], add_colorbar=False)
            ax[n_images+n_images+i].set_xticks([])
            ax[n_images+n_images+i].set_yticks([])
            ax[n_images+n_images+i].set(xlabel=None, ylabel=None)
        plt.tight_layout()
        plt.savefig(f'{IMGDIR}/{filename}_samples.png')

shps = [f for f in os.listdir(args.shp) if f != '.DS_Store']
for shp in shps:
    file_path = f'{args.shp}/{shp}'
    clipped = get_roa_raster(file_path)
    prediction_ready_data, unqualified, ndvis = prep_data(clipped)
    if prediction_ready_data.shape[0] == 0:
        print(f"No data based on NDVI cutoff. Skipping {shp}")
    else:
        predictions = predict_k_means(prediction_ready_data, model, scaler, unqualified)
        predictions['ndvi'] = ndvis

        print(shp)
        fname = shp.split(".gpkg")[0]
        predictions.to_csv(f"{ODIR}/{fname}.csv")

        save_tifs_pred(predictions, shp.split(".gpkg")[0], clipped.rio.crs)
        save_plots(predictions, shp.split(".gpkg")[0])
        save_tables(predictions, shp.split(".gpkg")[0])
        print(f"Process complete for {shp}")

save_samples()