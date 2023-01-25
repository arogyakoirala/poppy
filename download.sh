#!/bin/bash
source env2/bin/activate
# conda activate poppy-linux

process='solo'
mask=""
cores="1"
out="out"
interim="interim"
year="2019"

while getopts p:s:m:o:c:i:y: flag
do
    case "${flag}" in
        p) process=${OPTARG};;
        s) shp=${OPTARG};;
        m) mask=${OPTARG};;
        o) out=${OPTARG};;
        c) cores=${OPTARG};;
        i) interim=${OPTARG};;
        y) year=${OPTARG};;
    esac
done

if [[ $process == 'solo' ]]
then
    if  [[ -n $mask ]]
    then
        python -u download.py --shp $shp --out_dir $out --n_cores $cores --year $year
    else
        python -u download.py --shp $shp --mask $mask --out_dir $out --n_cores $cores --year $year
    fi
else
    N=$cores
    echo "### Multi mode activated. Number of cores:" $cores
    for entry in "$shp"/*
    do

        ((j=j%N)); ((j++==0)) && wait
        base=${entry##*/}
        base=${base%.*}
        echo "### Staring process for:" $base
        idir="${interim}/${base}"
        odir="${out}/${base}"
        if  [[ -n $mask ]]
        then
            python -u download.py --shp $shp/$base.gpkg --out_dir $odir --interim_dir $idir --n_cores 1 --year $year &
        else
            python -u download.py --shp $shp/$base.gpkg --mask $mask --out_dir $odir --interim_dir $idir --n_cores 1  --year $year &
        fi
    done
fi