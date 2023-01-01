import time
from utils.shapefile import ShapefileHelper
from utils.rasters import RasterGenerationHelper, MergeRasterSingleAoi, Masker, Sampler
# from utils.dates import BestDatesHelper
from utils.bestdates2 import DatesHelper
from utils.data import DataHelper
import multiprocessing
import argparse
import os
import shutil 
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("data_dir", help="What dir should I ue for generating data")
parser.add_argument("shp_path", help="Use a custom shapefile instead of aoi.gpkg")

parser.add_argument("--n_neighbors", help="Number of neighbors to use for KNN")
parser.add_argument("--upto_step", help="Tells the script to run upto specified step; One of 'grid', 'backfill', 'download', 'merge', 'mask', 'sample', 'prep_data'")
parser.add_argument("--from_step", help="Converse of upto. Tells the script to run from specified step; One of 'grid', 'backfill', 'download', 'merge', 'mask', 'sample', 'prep_data'")
parser.add_argument("--resolution-p", type=int, help="Resolution of parent tile (in metres)")
parser.add_argument("--resolution-c", type=int, help="Resolution of child tile (in metres)")
parser.add_argument("--n_cores", type=int, help="Number of cores to use")
parser.add_argument("--sample_size",  help="Sample size in percentage; default = 1.0")
parser.add_argument("--year",  help="year for which to download data")
parser.add_argument("--post_period_days", help="number of days after pre image that we look for a post image, eg [30,45]")
args = parser.parse_args()

#%% Define Parameters
DATA_DIR = args.data_dir
SHP_PATH = args.shp_path


YEAR = 2019
UPTO = 'prep_data'
FROM = 'grid'
N_CORES = 1
SAMPLE_SIZE = 1.0
N_NEIGHBORS = 3
POST_PERIOD_DAYS=[30,45]

# # Get parent and child grids
_RESOLUTION_P = 2500
_RESOLUTION_C = 250
_VECTOR_OUTPUT_DIR = f'{DATA_DIR}/interim'

    
if args.resolution_p:
    _RESOLUTION_P = args.resolution_p

if args.resolution_c:
    _RESOLUTION_C = args.resolution_c
    
# if args.out:
#     _VECTOR_OUTPUT_DIR = args.out
        
if args.upto_step:
    UPTO = args.upto_step
    FROM = ""

if args.from_step:
    FROM = args.from_step
    UPTO = ""
    
if args.n_cores:
    N_CORES = args.n_cores
    
if args.n_neighbors:
    N_NEIGHBORS = int(args.n_neighbors)

if args.sample_size:
    SAMPLE_SIZE = float(args.sample_size)

if args.year:
    YEAR = int(args.year)
    
if args.post_period_days:
    POST_PERIOD_DAYS = [int(el.strip()) for el in args.post_period_days.split(",")]


Path(_VECTOR_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

if UPTO in ['grid', 'backfill', 'download','merge', 'mask', 'sample', 'prep_data'] or FROM in ['grid']:
    start = time.time()
    print("--- Generating grids...")
    sh = ShapefileHelper(SHP_PATH, _VECTOR_OUTPUT_DIR)
    sh.make_grid(resolution=_RESOLUTION_P, name="parent", id_col="pgrid_id")
    sh.make_grid(resolution=_RESOLUTION_C, name="child")
    sh.make_grid(resolution=25000, name="parent_best_dates", id_col="pgrid_id")
    sh.make_grid(resolution=10000, name="parent_10", id_col="pgrid_id")
    print(f"#### Grid Gen Complete in {(time.time() - start)} ####")
    

if UPTO in ['backfill', 'download', 'merge', 'mask', 'sample', 'prep_data'] or FROM in ['grid', 'backfill']:
    print("--- Backfilling dates..")
    # Fill best dates for missing tiles
    start = time.time()
    _BEST_DATES_PATH = f'{DATA_DIR}/inputs/best_dates.csv'
    _PATH_TO_CHILD_GRID = f'{_VECTOR_OUTPUT_DIR}/child.gpkg'

    bd = DatesHelper(DATA_DIR, SHP_PATH, [f'{YEAR}-01-01', f'{YEAR}-06-15'], n_cores=1, bypass=False) # set bypass = False in prod
    bd.extract_best_dates()
#     bd = BestDatesHelper(_PATH_TO_CHILD_GRID, n_cores = 1, year = YEAR)
#     bd = BestDatesHelper(_BEST_DATES_PATH, _PATH_TO_CHILD_GRID, _VECTOR_OUTPUT_DIR, "child", YEAR, n_neighbors=N_NEIGHBORS, diagnose=True)
#     bd.fill_empty_dates()
    
    print(f"#### Backfill Complete in {(time.time() - start)} ####")
    

if UPTO in ['download','merge', 'mask', 'sample', 'prep_data'] or FROM in ['grid', 'backfill', 'download']:
    print(f"--- Downloading images.. | Post Period days - {POST_PERIOD_DAYS[0]} to {POST_PERIOD_DAYS[1]} days")
    start = time.time()
    
    _TILE_OUTPUT_DIR = f'{DATA_DIR}/interim/tiles'
    _PATH_TO_PARENT_GRID = f"{_VECTOR_OUTPUT_DIR}/parent.gpkg"
    _PATH_TO_CHILD_GRID = f"{_VECTOR_OUTPUT_DIR}/child.gpkg"
    _N_CORES = N_CORES
    
#     if os.path.exists(_TILE_OUTPUT_DIR):
#         shutil.rmtree(_TILE_OUTPUT_DIR)
        
    Path(_TILE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    rgh = RasterGenerationHelper(_PATH_TO_PARENT_GRID, _PATH_TO_CHILD_GRID, _TILE_OUTPUT_DIR, _N_CORES, clean = False, post_period_days = POST_PERIOD_DAYS)
    rgh.get_rasters()
    print(f"#### Download Complete in {(time.time() - start)}  ####")
    
if UPTO in ['merge', 'mask', 'sample', 'prep_data'] or FROM in ['grid', 'backfill', 'download','merge']:
    print("--- Merging images.." )
    start = time.time()
    _TILE_OUTPUT_DIR = f'{DATA_DIR}/interim/tiles'
    mrs = MergeRasterSingleAoi(DATA_DIR, SHP_PATH, _TILE_OUTPUT_DIR)
    mrs.merge()
    print(f"#### Merge Complete in {(time.time() - start)} ####")
    

if UPTO in ['mask', 'sample', 'prep_data'] or FROM in ['grid', 'backfill', 'download','merge', 'mask']:
    print("--- Masking images..")
    start = time.time()
#     _CROP_MASK_PATH = f'{DATA_DIR}/inputs/{YEAR}_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif'
#     _CROP_MASK_PATH = f'/data/tmp/arogya/data/inputs/2019_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif'
    _CROP_MASK_PATH = f'/data/tmp/arogya/data/inputs/updated_mask.tif'
    _INPUT_RASTER_PATH = f'{DATA_DIR}/interim/merged.tif'
    masker = Masker(DATA_DIR, SHP_PATH, _INPUT_RASTER_PATH, _CROP_MASK_PATH)
    masker.mask()
    print(f"#### Mask Complete in {(time.time() - start)} ####")
    

if UPTO in ['sample', 'prep_data'] or FROM in ['grid', 'backfill', 'download','merge', 'mask', 'sample']:
    print("--- Preparing sample..")   
    start = time.time()
    sampler = Sampler(DATA_DIR, f'{DATA_DIR}/interim/masked.tif')
    sampler.sample_zarr(SAMPLE_SIZE)
    print(f"#### Sampling Complete in {(time.time() - start)} ####")
    
    
# if UPTO in ['prep_data'] or FROM in ['grid', 'backfill', 'download','merge', 'mask', 'sample', 'prep_data']:
#     print("--- Prep datasets..")
#     start = time.time()
#     dh = DataHelper(DATA_DIR, f'{DATA_DIR}/interim/sample.tgz')
#     dh.save(dh.diff_bands(), "diff_bands")
#     print(f"#### Data Prep Complete in {(time.time() - start)} ####")
    
    