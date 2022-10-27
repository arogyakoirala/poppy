#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux

# Set DATA DIR
DataDir="../data"
echo ${DataDir}

# Declare a string array with type
declare -a AllDistricts=("${DataDir}/inputs/2604.gpkg" "${DataDir}/inputs/1001.gpkg" "${DataDir}/inputs/2605.gpkg" "${DataDir}/inputs/1002.gpkg" "${DataDir}/inputs/2706.gpkg" "${DataDir}/inputs/1003.gpkg" "${DataDir}/inputs/1004.gpkg" "${DataDir}/inputs/1005.gpkg" "${DataDir}/inputs/1006.gpkg" "${DataDir}/inputs/1007.gpkg" "${DataDir}/inputs/1014.gpkg" "${DataDir}/inputs/1015.gpkg" "${DataDir}/inputs/1103.gpkg" "${DataDir}/inputs/1112.gpkg" "${DataDir}/inputs/1115.gpkg" "${DataDir}/inputs/1116.gpkg" "${DataDir}/inputs/1118.gpkg" "${DataDir}/inputs/112.gpkg" "${DataDir}/inputs/1124.gpkg" "${DataDir}/inputs/1703.gpkg" "${DataDir}/inputs/1905.gpkg" "${DataDir}/inputs/2302.gpkg" "${DataDir}/inputs/2416.gpkg" "${DataDir}/inputs/2304.gpkg" "${DataDir}/inputs/2601.gpkg" "${DataDir}/inputs/2305.gpkg" "${DataDir}/inputs/2306.gpkg" "${DataDir}/inputs/2307.gpkg" "${DataDir}/inputs/2308.gpkg" "${DataDir}/inputs/2311.gpkg" "${DataDir}/inputs/2312.gpkg" "${DataDir}/inputs/2406.gpkg" "${DataDir}/inputs/2407.gpkg" "${DataDir}/inputs/2415.gpkg" "${DataDir}/inputs/2707.gpkg" "${DataDir}/inputs/3106.gpkg" "${DataDir}/inputs/3409.gpkg" "${DataDir}/inputs/809.gpkg" "${DataDir}/inputs/820.gpkg" "${DataDir}/inputs/904.gpkg")

# Declare a string array with type
declare -a SelectDistricts=("${DataDir}/inputs/2604.gpkg" "${DataDir}/inputs/1001.gpkg" "${DataDir}/inputs/2605.gpkg" "${DataDir}/inputs/1002.gpkg" "${DataDir}/inputs/2706.gpkg" "${DataDir}/inputs/1003.gpkg" "${DataDir}/inputs/1004.gpkg" "${DataDir}/inputs/1005.gpkg" "${DataDir}/inputs/1006.gpkg" "${DataDir}/inputs/1007.gpkg" "${DataDir}/inputs/1014.gpkg" "${DataDir}/inputs/1015.gpkg" "${DataDir}/inputs/1103.gpkg" "${DataDir}/inputs/1112.gpkg" "${DataDir}/inputs/1115.gpkg" "${DataDir}/inputs/1116.gpkg" "${DataDir}/inputs/1118.gpkg" "${DataDir}/inputs/112.gpkg" "${DataDir}/inputs/1124.gpkg" "${DataDir}/inputs/1703.gpkg" "${DataDir}/inputs/1905.gpkg" "${DataDir}/inputs/2416.gpkg" "${DataDir}/inputs/2601.gpkg" "${DataDir}/inputs/2305.gpkg" "${DataDir}/inputs/2307.gpkg" "${DataDir}/inputs/2311.gpkg" "${DataDir}/inputs/2312.gpkg" "${DataDir}/inputs/2406.gpkg" "${DataDir}/inputs/2407.gpkg" "${DataDir}/inputs/2415.gpkg" "${DataDir}/inputs/2707.gpkg" "${DataDir}/inputs/3106.gpkg" "${DataDir}/inputs/3409.gpkg" "${DataDir}/inputs/809.gpkg" "${DataDir}/inputs/820.gpkg" "${DataDir}/inputs/904.gpkg")


declare -a StringArray=("${DataDir}/inputs/aoi.gpkg")
 
# Read the array values with space
for val in "${SelectDistricts[@]}"; do
    python poppy-preprocess.py ../data --mode grid --shp_path $val
    python poppy-preprocess.py ../data --mode backfill --shp_path $val
    python poppy-preprocess.py ../data --mode download --shp_path $val --n_cores 30
done