#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux


while getopts s:d:y:m:n: flag
do
    case "${flag}" in
        s) shp=${OPTARG};;
        d) data=${OPTARG};;
        y) year=${OPTARG};;
        m) model=${OPTARG};;
        n) name=${OPTARG};;
    esac
done

echo $shp
python -u poppy-preprocess.py $data $shp --upto_step download --year $year --n_cores 1
python -u poppy-fix-downloads.py $data --n_cores 1
python -u poppy-predict.py $data $shp $model --model_type kmeans --num 3 --name $name 
print("########## DISTRICT PREDICTION PROCESS COMPLETE")


