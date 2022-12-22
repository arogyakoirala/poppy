#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux

while getopts s:y:d:m:c:n flag
do
    case "${flag}" in
        s) shp=${OPTARG};;
        y) year=${OPTARG};;
        d) data=${OPTARG};;
        m) model=${OPTARG};;
        c) cores=${OPTARG};;
        n) name=${OPTARG};;
    esac
done

echo "shp_path: $shp";
echo "year: $year";
echo "data_dir: $data";
echo "model: $model";
echo "cores: $cores";


declare -a Districts=("1001" "817" "1002" "1706" "813" "822" "1003" "1011" "1004" "1015" "814" "806" "820" "1612" "1118" "1013" "809" "1014" "802" "808" "2111" "1007" "804" "1703" "815" "1312" "2312" "1710" "816" "1813" "1606" "2404" "3401" "1005" "1006" "1010" "1607" "1116" "1009" "2416" "1126" "805" "1315" "803" "905" "901" "2401" "904" "1707" "1901" "1111" "1102" "903" "1124" "1711" "1302" "2301" "902" "1125" "1113" "2505" "1307" "1704" "1115" "3102" "1907" "1708" "2415" "112" "1705" "3106" "1103" "1112" "2406" "2302" "1123" "2405" "1803" "2605" "605" "2304" "2709" "2601" "2106" "1605" "2604" "1608" "1902" "3404" "2004" "2303" "1807" "1609" "3409" "3408" "1808" "3101" "1905" "2507" "2102" "1805" "1702" "2309" "3407" "1701" "2603" "2110" "1804" "2012" "2407" "2703" "1802" "1809" "2602" "2006" "2413" "2305" "2403" "2101" "2108" "1903" "2705" "3402" "2412" "2402" "2707" "2306" "2307" "2308" "2702" "2706" "1906" "2710" "2109" "2105" "2411" "2408" "3103" "2014" "2103" "1904" "2205" "2310" "2311" "2313" "2203")

# declare -a Districts=("817")

for district in "${Districts[@]}"; do

    echo "#### Starting process for DIST: ${district}"
    echo
    echo
    echo
    echo

    shp="/data/tmp/arogya/data/inputs/districts/districts/${district}.gpkg"
    name="${district}_kmeans_3_diff_bands"
    python -u poppy-preprocess.py $data $shp --upto_step download --year $year --n_cores $cores
    python -u poppy-fix-downloads.py $data --n_cores $cores
    python -u poppy-predict.py $data $shp $model diff_bands --model_type kmeans --num 3 --name $name

    echo "#### Completed process for DIST: ${district}\n\n\n"
    echo
    echo
    echo
    echo
    

done