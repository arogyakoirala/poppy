#!/bin/bash
source env2/bin/activate
# conda activate poppy-linux

process='solo'
mask=""
cores="1"
out="out"
interim="interim"
year="2019"

while getopts p:s:m:k:o:c:i:y: flag
do
    case "${flag}" in
        p) process=${OPTARG};;
        s) shp=${OPTARG};;
        m) model=${OPTARG};;
        k) mask=${OPTARG};;
        o) out=${OPTARG};;
        c) cores=${OPTARG};;
        i) interim=${OPTARG};;
        y) year=${OPTARG};;
    esac
done

echo $process 
echo $shp 
echo $model 
echo $mask 
echo $out 
echo $interim 
echo $cores 
echo $year

if [[ $process == 'solo' ]]
then
    if  [[ -n $mask ]]
    then
        python -u predict.py $shp $model --out_dir $out --year $year
    else
        python -u predict.py  $shp $model --mask $mask --out_dir $out --year $year
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
            python -u predict.py $shp/$base.gpkg $model --out_dir $odir --interim_dir $idir --year $year &
        else
            python -u predict.py $shp/$base.gpkg $model --mask $mask --out_dir $odir --interim_dir $idir --year $year &
        fi
    done
fi