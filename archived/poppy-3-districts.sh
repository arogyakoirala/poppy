# python -u poppy-preprocess.py ../data /data/tmp/arogya/data/inputs/2302.gpkg --upto_step download --year 2019 --sample_size 0.25 --n_cores 10 --post_period_days 30,45

# python poppy-predict.py  ../data /data/tmp/arogya/data/inputs/2302.gpkg /data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands diff_bands --model_type kmeans --num 3 --name 2302_kmeans_3_diff_bands 

# python -u poppy-preprocess.py ../data /data/tmp/arogya/data/inputs/1906.gpkg --upto_step download --year 2019 --sample_size 0.25 --n_cores 10 --post_period_days 30,45

# python poppy-predict.py  ../data /data/tmp/arogya/data/inputs/1906.gpkg /data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands diff_bands --model_type kmeans --num 3 --name 1906_kmeans_3_diff_bands 

python -u poppy-preprocess.py ../data /data/tmp/arogya/data/inputs/2308.gpkg --upto_step download --year 2019 --sample_size 0.25 --n_cores 10 --post_period_days 30,45

python poppy-predict.py  ../data /data/tmp/arogya/data/inputs/2308.gpkg /data/tmp/arogya/data/outputs/models/kmeans_3_diff_bands diff_bands --model_type kmeans --num 3 --name 2308_kmeans_3_diff_bands 
