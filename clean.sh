# killall -u arogya
rm -rf logs/dnq.out
rm -rf /data/tmp/arogya/data_dec/dnq
rm -rf /data/tmp/arogya/data_dec/dnq_outputs
# python poppy-ready-folders.py /data/tmp/arogya/data_dec /data/tmp/arogya/data_dec/inputs/districts/districts/
# nohup ./poppy-dnq.sh -s /data/tmp/arogya/data_dec/dnq -o /data/tmp/arogya/data_dec/outputs/predictions -y 2019 -c 25 -m /data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands > logs/dnq.out &
