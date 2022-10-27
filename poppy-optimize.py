import argparse
from utils.data import ModelingHelper


parser = argparse.ArgumentParser()
parser.add_argument("data_dir")
parser.add_argument("data_file_suffix")
parser.add_argument("--name")
parser.add_argument("--model_type", help="Type of model")
parser.add_argument("--n", type=int, help="N for the model")
parser.add_argument("--drop_ndvi_pre", action=argparse.BooleanOptionalAction)
args = parser.parse_args()         

MODEL_TYPE = "kmeans"
N = 3
DATA_FILE_SUFFIX = args.data_file_suffix
DATA_DIR = args.data_dir
DROP_NDVI_PRE = False

if args.model_type:
    MODEL_TYPE = args.model_type

if args.n:
    N = args.n

RUN_NAME = f"{MODEL_TYPE}_{N}_{DATA_FILE_SUFFIX}"
if args.name:
    RUN_NAME = args.name
    
if args.drop_ndvi_pre:
    DROP_NDVI_PRE = args.drop_ndvi_pre


DATA_FILE_PATH = f"{DATA_DIR}/interim/data_{DATA_FILE_SUFFIX}.tgz"

mh = ModelingHelper(DATA_DIR, DATA_FILE_PATH, RUN_NAME)
model = mh.fit(mh.raw, MODEL_TYPE, N, DROP_NDVI_PRE)
# scaler = mh.load_scaler(MODEL_TYPE, N)
# results = mh.predict(mh.raw, model, scaler)
# mh.save_raster(results, f"{MODEL_TYPE}_N_{N}_{DATA_FILE_SUFFIX}")
# mh.save_ndvi_plot(results, MODEL_TYPE, N, f"{MODEL_TYPE}_N_{N}_{DATA_FILE_SUFFIX}")
