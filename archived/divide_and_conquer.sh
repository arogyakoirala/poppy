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

# Generate tifs at the tile level
# 4,92,97, 129, 130
for ((i=130; i < ${#dnq_dirs[@]}-1; i++)); do
  if [ $i!=4 ]; then
      new_data_dir="${dnq_path}/${dnq_dirs[$i]}"
      echo $new_data_dir

      shp="$data/interim/${dnq_dirs[$i]}.gpkg"
      name="kmeans_3_diff_bands"
      SECONDS=0
      echo "Starting process for TILE: ${i}"
      echo
      echo
      echo
      echo
      python -u poppy-preprocess.py $new_data_dir $shp --upto_step download --year $year --n_cores $cores 
      python -u poppy-fix-downloads.py $new_data_dir --n_cores $cores
      python -u poppy-predict.py $new_data_dir $shp $model diff_bands --model_type kmeans --num 3 --name $name 
      echo "Completed process for TILE: ${i}"
      duration=$SECONDS
      echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
      echo
      echo
      echo
      echo
  fi
done

# # arr=(~/myDir/*)

