#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux

while getopts s:o:y:c:m: flag
do
    case "${flag}" in
        s) shps=${OPTARG};;
        o) outdir=${OPTARG};;
    esac
done

echo "shps_path: $shps";
echo "outdir: $outdir";


dnq_dirs=(`ls ${shps}`)

N=1
for ((i=0; i <= ${#dnq_dirs[@]}-1; i++)); do
    ((j=j%N)); ((j++==0)) && wait
    echo ${dnq_dirs[$i]}
    shp_path="$shps/${dnq_dirs[$i]}"
    
    echo $outdir $shp_path
    python sample.py ${outdir} ${shp_path} --n_cores 1
done

