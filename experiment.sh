#!/bin/bash

source poppy-env/bin/activate

declare -a Cutoffs=("0.6" "0.2" "0")
declare -a Masks=("80" "75" "70" "65" "60")


for cutoff in "${Cutoffs[@]}"; do
    for mask in "${Masks[@]}"; do
        echo "Cutoff:" $cutoff
        echo "Mask %:" $mask

        python -u metrics_cutoff.py --pred_dir outputs/predictions/nadali-qandahar-r1-r2-2019-30day/predictions --csv inputs/poppy_1994-2021.csv  --year 2019 --cluster 0 --cutoff $cutoff --mask $mask --subset 2019_3 results2019_q3
        python -u metrics_cutoff.py --pred_dir outputs/predictions/nadali-qandahar-r1-r2-2020-30day/predictions --csv inputs/poppy_1994-2021.csv  --year 2020 --cluster 1 --cutoff $cutoff --mask $mask --subset 2020_3 results2020_q3
        python -u metrics_cutoff.py --pred_dir outputs/predictions/nadali-qandahar-r1-r2-2021-30day/predictions --csv inputs/poppy_1994-2021.csv  --year 2021 --cluster 2 --cutoff $cutoff --mask $mask --subset 2021_3 results2021_q3
    done
done
