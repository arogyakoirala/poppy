#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux


while getopts s:d:y:c:m: flag
do
    case "${flag}" in
        s) shp=${OPTARG};;
        d) data=${OPTARG};;
        y) year=${OPTARG};;
        c) cores=${OPTARG};;
        m) model=${OPTARG};;
    esac
done

echo "shp_path: $shp";
echo "year: $year";
echo "data_dir: $data";
echo "model: $model";
echo "cores: $cores";

interim="$data/interim"
rm -rf $interim
python -u poppy-ready-tile-folders.py $data $shp

dnq_path="$data/interim/dnq"
dnq_dirs=(`ls ${dnq_path}`)

N=$cores
for ((i=0; i <= ${#dnq_dirs[@]}-1; i++)); do
    ((j=j%N)); ((j++==0)) && wait
    new_data_dir="${dnq_path}/${dnq_dirs[$i]}"
    echo
    echo
    echo
    echo
    echo "Starting process for TILE: ${i}"
    shp="$data/interim/${dnq_dirs[$i]}.gpkg"
    name="kmeans_3_diff_bands"
    SECONDS=0
    echo $new_data_dir $shp $year $model $name
    log="$new_data_dir/log.txt"
    ./poppy-dnq-download.sh -s $shp -d $new_data_dir -y $year -m $model -n $name > $log & 
    echo "Logfile: ${log}"
    
done