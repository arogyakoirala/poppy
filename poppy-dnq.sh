#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux

while getopts s:o:y:c:m: flag
do
    case "${flag}" in
        s) shps=${OPTARG};;
        o) outdir=${OPTARG};;
        y) year=${OPTARG};;
        c) cores=${OPTARG};;
        m) model=${OPTARG};;
    esac
done

echo "shps_path: $shp";
echo "year: $year";
echo "outdir: $outdir";
echo "model: $model";
echo "cores: $cores";

# python -u poppy-ready-folders.py $shps --out_dir $outdir

dnq_dirs=(`ls ${outdir}`)
N=$cores
for ((i=1; i <= ${#dnq_dirs[@]}-1; i++)); do
    ((j=j%N)); ((j++==0)) && wait
    new_data_dir="${outdir}/${dnq_dirs[$i]}"
    echo
    echo
    echo
    echo
    echo "Starting process for TILE: ${i}"
    shp="$shps/${dnq_dirs[$i]}.gpkg"
    name="kmeans_3_diff_bands"
    SECONDS=0
    echo $new_data_dir $shp $year $model $name
    log="$new_data_dir/log.txt"
    ./poppy-dnq-download.sh -s $shp -d $new_data_dir -y $year -m $model -n $name > $log & 
    echo "Logfile: ${log}"
    echo
    echo
    echo
    echo
done