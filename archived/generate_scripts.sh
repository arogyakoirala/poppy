year=$1
label=$2
cores=$3
env=$4



if [ env == 'dev' ]
then
    shp_in=../data/poppydata/inputs/aoi_nadali_qandahar
    mode_in=multi
    shp_out=../data/poppydata/inputs/aoi_nadali_qandahar
    mode_out=multi
    subset_in=../data/poppydata/inputs/aoi_nadali_qandahar
    results=../data/poppydata/outputs

else
    shp_in=/data/tmp/arogya/inputs/aoi_nadali_qandahar
    mode_in=multi
    shp_out=/data/tmp/arogya/inputs/grids_50km
    mode_out=multi
    subset_in=/data/tmp/arogya/inputs/subset
    results=/data/tmp/arogya/results    
fi


current_time=$(date "+%Y%m%d-%H%M")
# label=$1
echo >> script.sh
echo "---- Starting script generation; time: ${current_time} ---- " >> script.sh
echo "Modeling parameters: year = ${year}; label = ${label}; cores = ${cores}"  >> script.sh
echo "IO parameters: shp_in = ${shp_in}; shp_out = ${shp_out}; subset_in = ${subset_in}"  >> script.sh
echo >> script.sh

rm -rf script.sh

echo "nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=${cores} out=${results}/${label}-${year}-${current_time} shp_out=${shp_out} mode_out=multi > logs/${label}-${year}-${current_time}.out &


nohup ./fit_predict.sh model=kmeans n=3 mode_in=${mode_in} shp_in=${shp_in} mask=/data/tmp/arogya/inputs/mask.tif year=${year} cores=${cores} out=${results}/${label}-${year}-${current_time} shp_out=${shp_out} mode_out=${mode_out} > logs/${label}-${year}-${current_time}.all_dists.out &

echo Started fit predict process

while [ ! -f ${results}/${label}/models/COMPLETED ]
do
  echo waiting
  sleep 3
done

nohup ./predict.sh process=multi shp=${shp_in} model=${results}/${label}/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=3 year=${year} out=${results}/${label}-${year}-${current_time}/predictions interim=${results}/${label}-${year}-${current_time}/interim > logs/${label}.${current_time}.aoi_predict.out &

nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/subset model=${results}/${label}-${year}-${current_time}/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=10 year=${year} out=${results}/${label}-${year}-${current_time}/predictions interim=${results}/${label}-${year}-${current_time}/interim > logs/${label}.${current_time}.subset.out &" >> script.sh

chmod +x script.sh