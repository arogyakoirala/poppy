#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux


while getopts s:d:y:m:c: flag
do
    case "${flag}" in
        s) shp=${OPTARG};;
        d) data=${OPTARG};;
        y) year=${OPTARG};;
        m) model=${OPTARG};;
        c) cores=${OPTARG};;
    esac
done

declare -a missing=( "28" "92" "93" "96" "99"  "104"  "108"  "109"  "110"  "112"  "115"  "118"  "129"  "130"  "135"  "137"  "141"  "146"  "152"  "162"  "163"  "164"  "165"  "169"  "170"  "172"  "177"  "192"  "303"  "391"  "523"  "684"  "720"  "723"  "725"  "726"  "727"  "728"  "729"  "730"  "731"  "733"  "735"  "736"  "737"  "738"  "739"  "792"  "825"  "857"  "1033"  "1061"  "1149" )

dnq_path="$data/interim/dnq"
dnq_dirs=(`ls ${dnq_path}`)

N=$cores
for i in "${missing[@]}"; do
    ((j=j%N)); ((j++==0)) && wait
    new_data_dir="${dnq_path}/${dnq_dirs[$i]}"
    echo
    echo
    echo
    echo
    echo "Starting process for TILE: ${i}"
    echo $new_data_dir
    
    interim="$new_data_dir/interim"
    log="$new_data_dir/log.txt"
    rm -rf $interim
    mkdir $interim
    rm -rf $log
    

    shp="$data/interim/${dnq_dirs[$i]}.gpkg"
    name="kmeans_3_diff_bands"
    SECONDS=0

    echo $new_data_dir $shp $year $model $name
    
    ./poppy-dnq-download.sh -s $shp -d $new_data_dir -y $year -m $model -n $name > $log & 
    echo "Completed process for TILE: ${i}"
    duration=$SECONDS
    echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
    echo
    echo
    echo
    echo

done
