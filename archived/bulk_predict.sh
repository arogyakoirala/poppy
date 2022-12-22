#!/bin/bash
source /usr/local/anaconda3/condabin/conda
conda activate poppy-linux

declare -a Datasets=("diff_bands")
declare -a Models=("kmeans")
declare -a Ns=("3")
declare -a Districts=("2604" "1001" "2605" "1002" "2706" "1003" "1004" "1005" "1006" "1007" "1014" "1015" "1103" "1112" "1115" "1116" "1118" "112" "1124" "1703" "1905" "2302" "2416" "2304" "2601" "2305" "2306" "2307" "2308" "2311" "2312" "2406" "2407" "2415" "3106" "3409" "809" "820" "904")

# Done with "2308" "2305" "1112" "1114" "112" "203" "204" "205" "206" "604" "605" "802" "803" "804" "805" "806" "807" "808" "809" "810" "813" "814" "815" "816" "817" "819" "820" "822" "901" "902" "903" "904" "905" "1001" "1002" "1003" "1004" "1005" "1006" "1007" "1008" "1009" "1010" "1011" "1012" "1013" "1014" "1015" "1101" "1102" "1103" "1113"  "1115" "1116" "1118" "1123" "1124" "1125" "1126" "1201" "1206" "1207" "1208" "1302" "1307" "1310" "1312" "1315" "1503" "1504" "1605" "1606" "1607" "1608" "1609" "1612" "1701" "1703" "1706" "1707" "1708" "1711" "1802" "1803" "1804" "1805" "1807" "1808" "1809" "1813" "1901" "1902" "1903"
# Removed "2306" "1905"

declare -a Districts177=("1904"   "1906" "1907" "2003" "2004" "2006" "2007" "2011" "2012" "2014" "2101" "2102" "2103" "2104" "2105" "2106" "2107" "2108" "2109" "2111" "2203" "2205" "2301" "2302" "2303" "2304" "2307" "2309" "2310" "2311" "2312" "2313" "2401" "2402" "2403" "2404" "2405" "2406" "2407" "2408" "2411" "2412" "2413" "2414" "2415" "2416" "2501" "2504" "2505" "2506" "2507" "2508" "2509" "2510" "2601" "2602" "2603" "2604" "2605" "2701" "2702" "2703" "2705" "2706" "2707" "2709" "2710" "3101" "3102" "3103" "3105" "3106" "3107" "3401" "3402" "3403" "3404" "3405" "3406" "3407" "3408" "3409")


declare -a Subset=("2308", "2304")
echo "=========================== We're here!"

# for dataset in "${Datasets[@]}"; do
#     for model in "${Models[@]}"; do
#         for n in "${Ns[@]}"; do
#             echo "=========================== Training model" $dataset $model $n 
#             python -u poppy-optimize.py /data/tmp/arogya/afg_updated $dataset  --model_type $model --n $n
# #             for district in "${Districts[@]}"; do
# #                 declare -a ModelPath="/data/tmp/arogya/afg_updated/outputs/models/${model}_${n}_${dataset}"
# #                 declare -a AoiPath="/data/tmp/arogya/afg_updated/inputs/${district}.gpkg"
# #                 declare -a DataPath="/data/tmp/arogya/afg_updated"
# #                 declare -a ModelName="${model}_${n}_${dataset}_${district}"
# #                 echo "=========================== Predicting model" $dataset $model $n $district $AoiPath
# #                 python -u poppy-predict.py $DataPath $AoiPath $ModelPath $dataset --model_type $model --num $n --name $ModelName --dist $district
# #             done
#         done
#     done
# done

for district in "${Districts177[@]}"; do
    count=1
    for dataset in "${Datasets[@]}"; do
        for model in "${Models[@]}"; do
            for n in "${Ns[@]}"; do
                declare -a ModelPath="/data/tmp/arogya/data/outputs/models/${model}_${n}_${dataset}"
                declare -a AoiPath="/data/tmp/arogya/data/inputs/${district}.gpkg"
                declare -a DataPath="/data/tmp/arogya/data"
                declare -a ModelName="${model}_${n}_${dataset}_${district}"
                if [[ $count -gt 1 ]]
                then
                    echo "=========================== Predicting model" $dataset $model $n $district $AoiPath
                    python -u poppy-predict.py $DataPath $AoiPath $ModelPath $dataset --model_type $model --num $n --name $ModelName --dist $district --skip_raster_generation
                else
                    echo "=========================== Predicting model" $dataset $model $n $district $AoiPath
                    python -u poppy-predict.py $DataPath $AoiPath $ModelPath $dataset --model_type $model --num $n --name $ModelName --dist $district
                fi
                ((count=count+1))
                echo "======================================" "**DONE**: "  $dataset $model $n $district 
            done
        done
    done
done