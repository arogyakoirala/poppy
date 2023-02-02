#!/bin/bash
# source env2/bin/activate
conda activate poppy-linux

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done

# use here your expected variables
echo "shp_in = $shp_in"
echo "shp_out = $shp_out"
echo "mask = $mask"
echo "mode_in = $mode_in"
echo "mode_out = $mode_out"
echo "year = $year"
echo "cores = $cores"
echo "sampling_rate = $sampling_rate"
echo "model = $model"
echo "n = $n"
echo "out = $out"

# rm -rf $interim

out_inputs="$out/inputs"
out_interim="$out/interim"
out_models="$out/models"
out_predictions="$out/predictions"




./download.sh process=$mode_in shp=$shp_in mask=$mask cores=$cores year=$year out=$out_inputs interim=$out_interim 
echo "###-----#### Downloaded sample for modeling"

if [[ $mode_in == 'multi' ]]
then
    rm -rf $out_inputs/sample.zarr
    python -u accumulate.py $out_inputs 
    echo "###-----#### All samples accumulated"
fi


mkdir $out_models
f="${out_inputs}/sample.zarr"
python -u model.py $f $model $n --out_dir $out_models
echo "###-----#### Modeling complete"

f="${out}/models/model-${model}-${n}"
rm -rf $out_interim
mkdir $out_interim

echo $f

./predict.sh process=$mode_out shp=$shp_out model=$f mask=$mask cores=$cores year=$year out=$out_predictions interim=$out_interim

echo "###-----#### Prediction complete"








# process='solo'
# mask=""
# cores="1"
# out="out"
# interim="interim"
# year="2019"
# type="kmeans"
# n_clust="3"




# while getopts p:s:m:c:y:t:n:o: flag
# do
#     case "${flag}" in
#         p) process=${OPTARG};;
#         s) in=${OPTARG};;
#         m) mask=${OPTARG};;
#         c) cores=${OPTARG};;
#         y) year=${OPTARG};;
#         t) type=${OPTARG};;
#         n) n_clust=${OPTARG};;
#         o) out=${OPTARG};;
#     esac
# done



# if [[ $process == 'solo' ]]
# then
#    ./download.sh -p solo -s $shp -m $mask -c $cores -y $year -o $out
#    python -u model.py $out/sample.zarr $type $n_clust
#    ./predict.sh -p solo -s $shp -m out/model-kmeans-3 -k $mask -c $cores -y $year
# else
#     N=$cores
#     echo "### Multi mode activated. Number of cores:" $cores
#     for entry in "$shp"/*
#     do

#         ((j=j%N)); ((j++==0)) && wait
#         base=${entry##*/}
#         base=${base%.*}
#         echo "### Staring process for:" $base
#         idir="${interim}/${base}"
#         odir="${out}/${base}"
#         if  [[ -n $mask ]]
#         then
#             python -u download.py --shp $shp/$base.gpkg --out_dir $odir --interim_dir $idir --n_cores 1 --year $year &
#         else
#             python -u download.py --shp $shp/$base.gpkg --mask $mask --out_dir $odir --interim_dir $idir --n_cores 1  --year $year &
#         fi
#     done
# fi
