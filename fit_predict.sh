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

echo
echo
echo
echo "###---#### Starting model fitting and prediction step"
echo
echo "Model fitting parameters:"
echo "mode_in = $mode_in"
echo "shp_in = $shp_in"
echo "shp_out = $shp_out"
echo "model = $model"
echo "n = $n"
echo
echo "Prediction step parameters:"
echo "mode_out = $mode_out"
echo "out = $out"
echo
echo "Common parameters:"
echo "mask = $mask"
echo "year = $year"
echo "cores = $cores"
echo


out_inputs="$out/inputs"
out_interim="$out/interim"
out_models="$out/models"
out_predictions="$out/predictions"


rm -rf .__download

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

# echo $f

./predict.sh process=$mode_out shp=$shp_out model=$f mask=$mask cores=$cores year=$year out=$out_predictions interim=$out_interim

echo "###-----#### Prediction complete"



