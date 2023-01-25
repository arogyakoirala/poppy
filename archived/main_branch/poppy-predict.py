import argparse
import gc
parser = argparse.ArgumentParser()
parser.add_argument("data_dir")
parser.add_argument("shp_path")
parser.add_argument("model_path")
# parser.add_argument("data_file_suffix")
# parser.add_argument("--tiles_path")
parser.add_argument("--model_type")
parser.add_argument("--num")
parser.add_argument("--year")
parser.add_argument("--name")
parser.add_argument("--dist")
parser.add_argument("--skip_raster_generation", action=argparse.BooleanOptionalAction)
args = parser.parse_args()       



from utils.rasters import MergeRasterSingleAoi, Masker, Sampler
from utils.data import ModelingHelper, DataHelper
from pathlib import Path
import os
import shutil

DATA_DIR = args.data_dir
SHP_PATH = args.shp_path
MODEL_PATH = args.model_path
DATA_FILE_SUFFIX = "diff_bands"
TILES_PATH = f"{DATA_DIR}/interim/tiles"
YEAR = '2019'
NAME = MODEL_PATH.split("/")[-1]
SKIP_RASTER_GENERATION = False
N = 3
MODEL_TYPE = 'kmeans'
DIST = '2308'

    
print(f"data_dir={DATA_DIR}, shp_path={SHP_PATH}, model_path = {MODEL_PATH}, df_suffix={DATA_FILE_SUFFIX}, tiles_path={TILES_PATH}, year={YEAR}, name={NAME}, N={N}, SKIP_RASTER_GENERATION={SKIP_RASTER_GENERATION}, MODEL_TYPE={MODEL_TYPE}, DIST={DIST}")

if args.year:
    YEAR = args.year
if args.name:
    NAME = args.name
if args.skip_raster_generation:
    SKIP_RASTER_GENERATION = True
if args.model_type:
    MODEL_TYPE=args.model_type
if args.num:
    N=int(args.num)
if args.dist:
    DIST = args.dist
# if args.tiles_path:
#     TILES_PATH = arg.tiles_path



if not SKIP_RASTER_GENERATION:
    
    
    if os.path.exists(f"{DATA_DIR}/interim/temp"):
        shutil.rmtree(f"{DATA_DIR}/interim/temp")
        
    if os.path.exists(f"{DATA_DIR}/interim/temp.vrt"):
        os.remove(f"{DATA_DIR}/interim/temp.vrt")
    
    if os.path.exists(f"{DATA_DIR}/interim/temp.tif"):
        os.remove(f"{DATA_DIR}/interim/temp.tif")
    
    if os.path.exists(f"{DATA_DIR}/interim/merged.tif"):
        os.remove(f"{DATA_DIR}/interim/merged.tif")
        
    if os.path.exists(f"{DATA_DIR}/interim/masked.tif"):
        os.remove(f"{DATA_DIR}/interim/masked.tif")
    
    
    print("In Merger")
    
    # Create mereged raster for AOI
    mrs = MergeRasterSingleAoi(DATA_DIR, SHP_PATH, TILES_PATH)
    mrs.merge("temp")

    # Create Masked Raster for AOI
#     _CROP_MASK_PATH = f'{DATA_DIR}/inputs/{YEAR}_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif'
#     _CROP_MASK_PATH = f'/data/tmp/arogya/data/inputs/2019_E060N40_PROBAV_LC100_global_v3.0.1_2019.tif'
    _CROP_MASK_PATH = f'/data/tmp/arogya/data/inputs/updated_mask.tif'

    _INPUT_RASTER_PATH = f'{DATA_DIR}/interim/temp.tif'
    print("In Masker")

    masker = Masker(DATA_DIR, SHP_PATH, _INPUT_RASTER_PATH, _CROP_MASK_PATH)
    masker.mask("temp")

print("In Sampler")
sampler = Sampler(DATA_DIR, f'{DATA_DIR}/interim/temp.tif')
sampler.sample(1, sample_filename = "temp", save_full=False)

dh = DataHelper(DATA_DIR, f'{DATA_DIR}/interim/temp.tgz')

if DATA_FILE_SUFFIX=="diff_bands":
    dh.save(dh.diff_bands(), "diff_bands", filename=f'{DATA_DIR}/interim/temp.tgz')
if DATA_FILE_SUFFIX=="pre_only":
    dh.save(dh.pre_only(), "pre_only", filename=f'{DATA_DIR}/interim/temp.tgz')
if DATA_FILE_SUFFIX=="post_only":
    dh.save(dh.post_only(), "post_only", filename=f'{DATA_DIR}/interim/temp.tgz')
if DATA_FILE_SUFFIX=="ndvi_and_day":
    dh.save(dh.ndvi_and_day(), "ndvi_and_day", filename=f'{DATA_DIR}/interim/temp.tgz')
if DATA_FILE_SUFFIX=="diff_all":
    dh.save(dh.ndvi_and_day(), "diff_all", filename=f'{DATA_DIR}/interim/temp.tgz')

    
    
_DATA_FILE_PATH = f'{DATA_DIR}/interim/temp.tgz'
mh = ModelingHelper(DATA_DIR, _DATA_FILE_PATH, "dummy")
model = mh.load_model(f"{MODEL_PATH}/model.pickle")
scaler = mh.load_scaler(f"{MODEL_PATH}/scaler.pickle")

results = mh.predict(mh.raw, model, scaler)

Path(f"{DATA_DIR}/outputs/predictions/{NAME}").mkdir(parents=True, exist_ok=True)

mh.save_raster(results, f"{DATA_DIR}/outputs/predictions/{NAME}/{NAME}")
mh.save_comparison_results(results, DIST, YEAR, f"{DATA_DIR}/outputs/predictions/{NAME}/{NAME}")
mh.save_ndvi_plot(results, MODEL_TYPE, N, f"{DATA_DIR}/outputs/predictions/{NAME}/{NAME}")

mrs=None
masker=None
sampler=None
dh=None
mh=None
model=None
scaler=None
results=None
gc.collect(generation=2)