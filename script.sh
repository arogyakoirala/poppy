nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/aoimodal-2020-20230301-0106 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoimodal-2020-20230301-0106.out &


nohup ./fit_predict.sh model=kmeans n=3 mode_in= shp_in=/data/tmp/arogya/inputs/aoi_nadali_qandahar mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/aoimodal-2020-20230301-0106 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoimodal-2020-20230301-0106.all_dists.out &

echo Started fit predict process

while [ ! -f /data/tmp/arogya/results/aoimodal/models/COMPLETED ]
do
  echo waiting
  sleep 3
done

nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/aoi_nadali_qandahar model=/data/tmp/arogya/results/aoimodal/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=3 year=2020 out=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/predictions interim=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/interim > logs/aoimodal.20230301-0106.aoi_predict.out &

nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/subset model=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=10 year=2020 out=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/predictions interim=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/interim > logs/aoimodal.20230301-0106.subset.out &
