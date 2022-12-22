MISSING_SHPS = ["2003", "2007", "2011", "2104", "2107", "2414", "2501", "2504", "2506","2508", "2509",  "2510",  "2701", "3105", "3107", "3403", "3405", "3406", ]
DISTRICTS = ["1904", "2308", "2304", "1906", "1907",  "2004", "2006",  "2012", "2014", "2101", "2102", "2103",  "2105", "2106",  "2108", "2109", "2111", "2203", "2205", "2301", "2302", "2303", "2304", "2307", "2309", "2310", "2311", "2312", "2313", "2401", "2402", "2403", "2404", "2405", "2406", "2407", "2408", "2411", "2412", "2413", "2415", "2416",   "2505",  "2507", "2601", "2602", "2603", "2604", "2605",  "2702", "2703", "2705", "2706", "2707", "2709", "2710", "3101", "3102", "3103",  "3106",  "3401", "3402",  "3404",  "3407", "3408", "3409"]

import geopandas as gpd
import os
import multiprocessing as mp
import numpy as np

DATA_DIR="/data/tmp/arogya/tmp"
DNQ_DIR=f"{DATA_DIR}/interim/dnq"

folders = sorted([d for d in os.listdir(DNQ_DIR) if ".gpkg" not in d])


successfull = "but moving on.."

def check(i):
    d = folders[i]
    f = f"{DNQ_DIR}/{d}/log.txt"
    with open(f, 'r') as f2:
        if 'but moving' in f2.read():
            return True
        return False
count=0
missing=[]
i_s = []
for i in range(1150):
    if check(i):
        count+=1
        missing.append(folders[i])
        i_s.append(i)


def predict():
    cpus = 15
    parent_chunks = np.array_split(DISTRICTS, cpus)
    pool = mp.Pool(processes=cpus)
    chunk_processes = [pool.apply_async(predict_chunk, args=(chunk, DISTRICTS)) for chunk in parent_chunks]
    chunk_results = [chunk.get() for chunk in chunk_processes]

def predict_chunk(DISTRICTS, all_dists):
    for dist in DISTRICTS:
        DATA_DIR = '/data/tmp/arogya/tmp/'
        GRID = '/data/tmp/arogya/tmp/interim/grid.gpkg'
        SHP = f'/data/tmp/arogya/tmp/inputs/{dist}.gpkg'
        YEAR = '2019'
        MODEL_PATH = '/data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands'


        grid = gpd.read_file(GRID)
        shp = gpd.read_file(SHP)
        joined = grid.sjoin(shp)
        grid_ids = list(joined['grid_id'])
        print(f"Starting process for {dist}, there are {len(grid_ids)} tiles: {grid_ids}")

        for tile in grid_ids:
            if tile in missing:
                print(f"Encountered missing tile ID: {tile}, moving on..")
            else:
                DATA_DIR_ = f"/data/tmp/arogya/tmp/interim/dnq/{tile}"
                SHP_PATH_ = f"/data/tmp/arogya/tmp/interim/{tile}.gpkg"
                DATA_FILE_SUFFIX = "diff_bands"
                TILES_PATH = f"{DATA_DIR_}/interim/tiles"
                NAME = MODEL_PATH.split("/")[-1]
                SKIP_RASTER_GENERATION = False
                N = 3
                MODEL_TYPE = 'kmeans'    
                os.system(f"python -u poppy-predict.py {DATA_DIR_} {SHP_PATH_} {MODEL_PATH}")
        print(f"###### FINISHED PREDICTING FOR: {dist}")

predict()
    
