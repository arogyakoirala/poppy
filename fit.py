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

# Specify parameters
MODEL = 'kmeans'
N = 3
TRANSFORM = 'diff_bands'
NDVI_CUTOFF = 0.4
NAME = ""

# Command line arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("shp", help="SHP")
parser.add_argument("rasters_dir", help="Rasters Dir")
parser.add_argument("out_dir", help="Out")
parser.add_argument("--name", help="Out")
args = parser.parse_args()

# Directory (input and output) declaration and setup
SDIR = args.shp
RDIR = args.rasters_dir 
IDIR = f'{RDIR}/interim'
candidates = [f for f in os.listdir(IDIR) if f != '.DS_Store']

ODIR = f"{args.out_dir}/{MODEL}-{N}"
if args.name:
    ODIR = f"{args.out_dir}/{MODEL}-{N}-{args.name}"
    
Path(ODIR).mkdir(parents=True, exist_ok=False)
IMGDIR = f"{ODIR}/images"
Path(IMGDIR).mkdir(parents=True, exist_ok=True)

TDIR = f"{ODIR}/tables"
Path(TDIR).mkdir(parents=True, exist_ok=True)

# Log file to store important information
f = open(f"{ODIR}/log.txt", "a")
start = time.time()
dt = datetime.fromtimestamp(start).strftime("%A, %B %d, %Y %I:%M:%S")
f.write(f"Started model fitting process at {dt}")

# Function to get clipped raster pertaining to a GeoDataFrame
def get_roa_raster(roa_shp):
    ROA = gpd.read_file(roa_shp).reset_index()

    clipped_rasters=[]
    for tile in candidates:
        TDIR = f'{IDIR}/{tile}'
        if 'NOCROP' in os.listdir(TDIR):
            pass
        else:
            tilegdf = gpd.read_file(f'{TDIR}/child.gpkg')
            tilegdf['dissolvefield'] = 1
            tilegdf = tilegdf.dissolve(by='dissolvefield').reset_index()
            # geom = tilegdf.geometry.unary_union

            if ROA.intersects(tilegdf, align=True)[0] == True:
                clip_region=ROA.intersection(tilegdf, align=True)
                full_raster = rxr.open_rasterio(f'{TDIR}/{tile}.tif')
                clipped_raster = full_raster.rio.clip(clip_region.geometry.apply(mapping), clip_region.crs)
                clipped_rasters.append(clipped_raster)

    clipped_raster = merge_arrays(clipped_rasters)
    return clipped_raster

# Adds NDVI Values to data
def add_ndvi(df, b8, b4, label):
    df[label] = (df[b8] - df[b4]) / (df[b8] + df[b4]) 
    return df

# Removes NaNs
def remove_nans(df):
   return df[~np.isnan(df).any(axis=1)]


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
    df = remove_nans(df)
    df = df[df['ndvi_pre'] > NDVI_CUTOFF]
    ndvis = df.reset_index()['ndvi_pre'] # save pre ndvis for future plotting

    # Apply required data transformation
    if TRANSFORM == 'diff_bands':
        for col in range(1,13):
            df[col] = df[col+12] - df[col]
        df['diff_ndvi'] = df['ndvi_post'] - df['ndvi_pre']
        df = df[[*range(1,13), 'diff_ndvi']]
   
    return df, ndvis


# Helper function to zave numpy array to disk (reqd when using multiple input shapefiles)
def save_zarr(df, path):
    if os.path.exists(path):
        z = zarr.open(path, mode='a')
        z.append(df.to_numpy())
    else:
        zarr.save(path, df.to_numpy()) 

# Saves Xarray dataset to raster
def save_tifs_raw(raw, name):
    raw.rio.to_raster(f"{IMGDIR}/{name}.tif")



# Model step 1: Ready data for modeling
# Look at all shapefiles in $SDIR
# For each shapefile:
#      1. Generate Raster
#      2. Save generated raster, for later review
#      3. Generate numpy array and save for modeling step
for shp in [f for f in os.listdir(args.shp) if f != '.DS_Store']:
    file_path = f'{args.shp}/{shp}'
    f.write(f"\nUsing shapefile: {file_path}")
    clipped = get_roa_raster(file_path) # save this file if possible
    save_tifs_raw(clipped, shp.split(".gpkg")[0])
    model_ready_data, _ = prep_data(clipped)
    save_zarr(model_ready_data, f"{ODIR}/raw.zarr")

f.write(f"\nCompleted data preparation in {np.round(time.time()-start, 3)} seconds ({np.round((time.time()-start)/60,2)} minutes)")

# Model fitting - start
DATA = zarr.open(f"{ODIR}/raw.zarr")[:]
f.write(f"\n\nStarting modeling step, data dimensions: {DATA.shape} ")

# Normalize
scaler = StandardScaler()
scaler.fit(DATA)
norm = scaler.transform(DATA)

# Save scaler from training data for later use
with open(f'{ODIR}/scaler.pkl', 'wb') as fi:
    pickle.dump(scaler, fi)

if MODEL=='kmeans':
    model = KMeans(n_clusters=N, n_init=10)
    model.fit(norm)

# Save model for later use
with open(f'{ODIR}/model.pkl', 'wb') as fi:
    pickle.dump(model, fi)

# Model fitting - end
f.write(f"\nCompleted model fitting in {np.round(time.time()-start, 3)} seconds ({np.round((time.time()-start)/60,2)} minutes)")



# Extra Step: Predict on modeling regions, for later review
f.write(f"\n\nStarting prediction step")

# helper function to calculate euclidian distance between two vectors
def getDistances(a, b):
    aSumSquare = np.sum(np.square(a),axis=1)
    bSumSquare = np.sum(np.square(b),axis=1)
    mul = np.dot(a,b.T)
    dists = np.sqrt(aSumSquare[:,np.newaxis]+bSumSquare-2*mul)
    return dists

# Get distances for each pixel from model centroids
def get_distances_and_scores(norm, model):
    CENTROIDS =  model.cluster_centers_
    DISTANCES = getDistances(norm, CENTROIDS)

    _n = norm.shape[1]
    _1_by_d = (1/DISTANCES)**(_n-1)
    _sigma_term = np.sum(_1_by_d, axis=1)
    _sigma_term = _sigma_term.reshape(_sigma_term.shape[0], 1)
    SCORES = np.divide(_1_by_d,_sigma_term)
    return DISTANCES, SCORES

# Generate prediction for each pixel
def predict_k_means(df):
    DATA=df.to_numpy()
    X = DATA[:, 2:]
    NORM = scaler.transform(X)
    DISTANCES, SCORES = get_distances_and_scores(NORM, model)

    PREDS = model.predict(NORM)
    PREDS = np.array(PREDS)
    PREDS = PREDS.reshape(PREDS.shape[0], 1)
    RESULTS = DATA[:, [0,1,14]]
    RESULTS = np.hstack((RESULTS, PREDS, DISTANCES, SCORES))
    RESULTS = pd.DataFrame(RESULTS, columns = ['y','x','ndvi','cluster', "dist_centroid_0", "dist_centroid_1", "dist_centroid_2", "score_centroid_0",  "score_centroid_1",  "score_centroid_2"])
    RESULTS = RESULTS.drop_duplicates(subset=['y', 'x'])
    RESULTS = RESULTS.sort_values(['y', 'x'], ascending=False)
    return RESULTS

# Save generated predictions
def save_tifs_pred(predictions, name):
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

    datasets = {"predictions": ["cluster.tif"], "distances":["d0.tif", "d1.tif", "d2.tif"], "scores":["s0.tif", "s1.tif", "s2.tif"]}
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
        print(data)
        print(type(data))
        data.to_csv(f'{IMGDIR}/{name}_cluster{i}.csv')
        print(f'Saved CSV to: {IMGDIR}/{name}_cluster{i}.csv')
    plt.tight_layout()
    plt.savefig(f'{IMGDIR}/{name}_ndvi.png')

# Save generated tables
def save_tables(predictions, name):
    counts = pd.DataFrame(predictions.groupby('cluster').count()['ndvi']/100).rename(columns={'ndvi': 'clustering_ha'})
    counts.to_csv(f"{TDIR}/{name}_acreage.csv")

## Actual prediction step
for shp in [f for f in os.listdir(args.shp) if f != '.DS_Store']:
    file_path = f'{args.shp}/{shp}'
    f.write(f"\nUsing shapefile: {file_path}")
    clipped = get_roa_raster(file_path)
    prediction_ready_data, ndvis = prep_data(clipped)
    prediction_ready_data = prediction_ready_data.reset_index()
    # save_plots(prediction_ready_data, shp.split(".gpkg")[0])
    predictions = predict_k_means(prediction_ready_data)
    predictions['ndvi'] = ndvis
    save_plots(predictions, shp.split(".gpkg")[0])
    save_tables(predictions, shp.split(".gpkg")[0])
    save_tifs_pred(predictions, shp.split(".gpkg")[0])

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

save_samples()

f.write(f"\nCompleted prediction in {np.round(time.time()-start, 3)} seconds ({np.round((time.time()-start)/60,2)} minutes)")
f.close()