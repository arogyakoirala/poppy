# killall -u arogya
rm -rf logs/dnq_mrs.out
rm -rf /data/tmp/arogya/data_mls19/dnq
rm -rf /data/tmp/arogya/data_mls19/dnq_outputs
# python poppy-ready-folders.py /data/tmp/arogya/data_mls19 /data/tmp/arogya/data_mls19/inputs/districts/districts/
# nohup ./poppy-dnq.sh -s /data/tmp/arogya/data_mls19/dnq -o /data/tmp/arogya/data_mls19/outputs/predictions -y 2019 -c 25 -m /data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands > logs/dnq.out &


