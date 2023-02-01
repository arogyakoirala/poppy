#!/bin/bash
source env2/bin/activate
# conda activate poppy-linux

# process='solo'
# mask=""
# cores="1"
# out="out"
# # interim="../2308_interim"
# year="2019"

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done


echo "shp = $shp"
echo "out = $out"
echo "cores = $cores"
echo "mask = $mask"
echo "year = $year"

echo "interim = $interim"


if [[ $process == 'solo' ]]
then
        python -u download.py --shp $shp --mask $mask --out_dir $out --n_cores $cores --year $year --interim_dir $interim
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
       
            python -u download.py --shp $shp/$base.gpkg --mask $mask --out_dir $odir --interim_dir $idir --n_cores 1  --year $year &
    done
fi