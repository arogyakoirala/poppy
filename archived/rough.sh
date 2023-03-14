./download.sh process=solo shp=/data/tmp/arogya/inputs/nadali.gpkg mask=/data/tmp/arogya/inputs/mask.tif cores=20 year=2020 out=../test/inputs interim=../test/interim




nohup ./predict.sh process=solo shp=/data/tmp/arogya/inputs/aoi.gpkg model=/data/tmp/arogya/results/aoi_2020/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=5 year=2020 out=../data/2020_roa/predictions interim=../data/2020_roa/interim > logs/2020_roa.out &


nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=30 out=../aoi_2020 shp_out=/data/tmp/arogya/inputs/aoi.gpkg mode_out=solo > logs/aoi_2020.out &

nohup ./predict.sh process=solo shp=/data/tmp/arogya/inputs/aoi.gpkg model=/data/tmp/arogya/results/aoi_2020/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=1 year=2020 out=../aoi2020/predictions interim=../aoi2020/interim > logs/training_region.out &

scp arogya@fati.ischool.berkeley.edu:'/data/tmp/arogya/results/nadali_2020/predictions/1103_0/*.tif' .



./fit_predict.sh mode_in=solo shp_in=../poppydata/inputs/aoi.gpkg mask=../poppydata/inputs/mask.tif year=2020 cores=6 model=kmeans n=3 out=../zetest shp_out=../sample_tiles mode_out=multi


nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=25 out=/data/tmp/arogya/results/aoi_2020 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoi_2020.out &



scp arogya@fati.ischool.berkeley.edu:'/home/arogya/projects/afg-clustering/data/2020_roa/*.tif' .


nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2019 cores=25 out=/data/tmp/arogya/results/aoi_2019 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoi_2019.out &

# 60
distribution_2020_60dist99 = get_distribution_by_dist(11.545177773538338, "2020_60dist99.pkl", 60)
distribution_2020_60dist95 = get_distribution_by_dist(9.170721365915652, "2020_60dist95.pkl", 60)
distribution_2020_60dist90 = get_distribution_by_dist(8.08627100096902, "2020_60dist90.pkl", 60)
distribution_2020_60dist85 = get_distribution_by_dist(7.528400337266891, "2020_60dist85.pkl", 60)
distribution_2020_60dist80 = get_distribution_by_dist(7.150468868574022, "2020_60dist80.pkl", 60)



# # 65
distribution_2020_65dist99 = get_distribution_by_dist(11.545177773538338, "2020_65dist99.pkl", 65)
distribution_2020_65dist95 = get_distribution_by_dist(9.170721365915652, "2020_65dist95.pkl", 65)
distribution_2020_65dist90 = get_distribution_by_dist(8.08627100096902, "2020_65dist90.pkl", 65)
distribution_2020_65dist85 = get_distribution_by_dist(7.528400337266891, "2020_65dist85.pkl", 65)
distribution_2020_65dist80 = get_distribution_by_dist(7.150468868574022, "2020_65dist80.pkl", 65)

# 70
distribution_2020_70dist99 = get_distribution_by_dist(11.545177773538338, "2020_70dist99.pkl", 70)
distribution_2020_70dist95 = get_distribution_by_dist(9.170721365915652, "2020_70dist95.pkl", 70)
distribution_2020_70dist90 = get_distribution_by_dist(8.08627100096902, "2020_70dist90.pkl", 70)
distribution_2020_70dist85 = get_distribution_by_dist(7.528400337266891, "2020_70dist85.pkl", 70)
distribution_2020_70dist80 = get_distribution_by_dist(7.150468868574022, "2020_70dist80.pkl", 70)



# 75
distribution_2020_75dist99 = get_distribution_by_dist(11.545177773538338, "2020_75dist99.pkl", 75)
distribution_2020_75dist95 = get_distribution_by_dist(9.170721365915652, "2020_75dist95.pkl", 75)
distribution_2020_75dist90 = get_distribution_by_dist(8.08627100096902, "2020_75dist90.pkl", 75)
distribution_2020_75dist85 = get_distribution_by_dist(7.528400337266891, "2020_75dist85.pkl", 75)
distribution_2020_75dist80 = get_distribution_by_dist(7.150468868574022, "2020_75dist80.pkl", 75)

# 80
distribution_2020_80dist99 = get_distribution_by_dist(11.545177773538338, "2020_80dist99.pkl", 80)
distribution_2020_80dist95 = get_distribution_by_dist(9.170721365915652, "2020_80dist95.pkl", 80)
distribution_2020_80dist90 = get_distribution_by_dist(8.08627100096902, "2020_80dist90.pkl", 80)
distribution_2020_80dist85 = get_distribution_by_dist(7.528400337266891, "2020_80dist85.pkl", 80)
distribution_2020_80dist80 = get_distribution_by_dist(7.150468868574022, "2020_80dist80.pkl", 80)



# 85
distribution_2020_85dist99 = get_distribution_by_dist(11.545177773538338, "2020_85dist99.pkl", 85)
distribution_2020_85dist95 = get_distribution_by_dist(9.170721365915652, "2020_85dist95.pkl", 85)
distribution_2020_85dist90 = get_distribution_by_dist(8.08627100096902, "2020_85dist90.pkl", 85)
distribution_2020_85dist85 = get_distribution_by_dist(7.528400337266891, "2020_85dist85.pkl", 85)
distribution_2020_85dist80 = get_distribution_by_dist(7.150468868574022, "2020_85dist80.pkl", 85)

# 90
distribution_2020_90dist99 = get_distribution_by_dist(11.545177773538338, "2020_90dist99.pkl", 90)
distribution_2020_90dist95 = get_distribution_by_dist(9.170721365915652, "2020_90dist95.pkl", 90)
distribution_2020_90dist90 = get_distribution_by_dist(8.08627100096902, "2020_90dist90.pkl", 90)
distribution_2020_90dist85 = get_distribution_by_dist(7.528400337266891, "2020_90dist85.pkl", 90)
distribution_2020_90dist80 = get_distribution_by_dist(7.150468868574022, "2020_90dist80.pkl", 90)


# 95
distribution_2020_95dist99 = get_distribution_by_dist(11.545177773538338, "2020_95dist99.pkl", 95)
distribution_2020_95dist95 = get_distribution_by_dist(9.170721365915652, "2020_95dist95.pkl", 95)
distribution_2020_95dist90 = get_distribution_by_dist(8.08627100096902, "2020_95dist90.pkl", 95)
distribution_2020_95dist85 = get_distribution_by_dist(7.528400337266891, "2020_95dist95.pkl", 95)
distribution_2020_95dist80 = get_distribution_by_dist(7.150468868574022, "2020_95dist80.pkl", 95)


[901,1005,1115,1307,1605,1701,1702,1705,1809,1902,1905,1907,2004,2014,2102,2109,2110,2111,2205,2304,2305,2306,2310,2311,2403,2412,2415,2707,2710,3102,3402,3407]



[
 cp grids_50km/901*.gpkg missing2019
 cp grids_50km/1005*.gpkg missing2019
 cp grids_50km/1115*.gpkg missing2019
 cp grids_50km/1307*.gpkg missing2019
 cp grids_50km/1605*.gpkg missing2019
 cp grids_50km/1701*.gpkg missing2019
 cp grids_50km/1702*.gpkg missing2019
 cp grids_50km/1705*.gpkg missing2019
 cp grids_50km/1809*.gpkg missing2019
 cp grids_50km/1902*.gpkg missing2019
 cp grids_50km/1905*.gpkg missing2019
 cp grids_50km/1907*.gpkg missing2019
 cp grids_50km/2004*.gpkg missing2019
 cp grids_50km/2014*.gpkg missing2019
 cp grids_50km/2102*.gpkg missing2019
 cp grids_50km/2109*.gpkg missing2019
 cp grids_50km/2110*.gpkg missing2019
 cp grids_50km/2111*.gpkg missing2019
 cp grids_50km/2205*.gpkg missing2019
 cp grids_50km/2304*.gpkg missing2019
 cp grids_50km/2305*.gpkg missing2019
 cp grids_50km/2306*.gpkg missing2019
 cp grids_50km/2310*.gpkg missing2019
 cp grids_50km/2311*.gpkg missing2019
 cp grids_50km/2403*.gpkg missing2019
 cp grids_50km/2412*.gpkg missing2019
 cp grids_50km/2415*.gpkg missing2019
 cp grids_50km/2707*.gpkg missing2019
 cp grids_50km/2710*.gpkg missing2019
 cp grids_50km/3102*.gpkg missing2019
 cp grids_50km/3402*.gpkg missing2019
 cp grids_50km/3407*.gpkg missing2019
 
 ]


cp grids_50km/112* missing2020/
cp grids_50km/802* missing2020/
cp grids_50km/806* missing2020/
cp grids_50km/901* missing2020/
cp grids_50km/1112* missing2020/
cp grids_50km/1124* missing2020/
cp grids_50km/1701* missing2020/
cp grids_50km/1802* missing2020/
cp grids_50km/1905* missing2020/
cp grids_50km/2012* missing2020/
cp grids_50km/2205* missing2020/
cp grids_50km/2305* missing2020/
cp grids_50km/2307* missing2020/
cp grids_50km/2310* missing2020/
cp grids_50km/2311* missing2020/
cp grids_50km/2313* missing2020/
cp grids_50km/2405* missing2020/
cp grids_50km/2408* missing2020/
cp grids_50km/2412* missing2020/
cp grids_50km/2507* missing2020/
cp grids_50km/2602* missing2020/
cp grids_50km/2604* missing2020/
cp grids_50km/2605* missing2020/
cp grids_50km/2709* missing2020/
cp grids_50km/3102* missing2020/
cp grids_50km/3402* missing2020/
cp grids_50km/3407* missing2020/


cp  grids_50km/1115_0.gpkg missing2019_r2
cp  grids_50km/1907_1.gpkg missing2019_r2
cp  grids_50km/1905_2.gpkg missing2019_r2
cp  grids_50km/2111_0.gpkg missing2019_r2
cp  grids_50km/2305_0.gpkg missing2019_r2
cp  grids_50km/2205_5.gpkg missing2019_r2
cp  grids_50km/2306_3.gpkg missing2019_r2
cp  grids_50km/2306_1.gpkg missing2019_r2
cp  grids_50km/2305_1.gpkg missing2019_r2
cp  grids_50km/2205_2.gpkg missing2019_r2
cp  grids_50km/2304_1.gpkg missing2019_r2
cp  grids_50km/2310_0.gpkg missing2019_r2
cp  grids_50km/2311_7.gpkg missing2019_r2
cp  grids_50km/2403_0.gpkg missing2019_r2
cp  grids_50km/2412_0.gpkg missing2019_r2
cp  grids_50km/2412_2.gpkg missing2019_r2
cp  grids_50km/2415_0.gpkg missing2019_r2
cp  grids_50km/2707_2.gpkg missing2019_r2
cp  grids_50km/3102_1.gpkg missing2019_r2
cp  grids_50km/3402_2.gpkg missing2019_r2
cp  grids_50km/2710_4.gpkg missing2019_r2
cp  grids_50km/3407_0.gpkg missing2019_r2
cp  grids_50km/901_0.gpkg missing2019_r2


cp   grids_50km/1905_2.gpkg missing2020_r2 
cp   grids_50km/2405_2.gpkg missing2020_r2 
cp   grids_50km/2602_1.gpkg missing2020_r2 
cp   grids_50km/2507_1.gpkg missing2020_r2 
cp   grids_50km/2604_2.gpkg missing2020_r2 
cp   grids_50km/2605_2.gpkg missing2020_r2 
cp   grids_50km/2709_0.gpkg missing2020_r2 
cp   grids_50km/3404_3.gpkg missing2020_r2 
cp   grids_50km/3102_1.gpkg missing2020_r2 
cp   grids_50km/3402_1.gpkg missing2020_r2 
cp   grids_50km/806_0.gpkg missing2020_r2 
cp   grids_50km/901_0.gpkg missing2020_r2 
cp   grids_50km/802_0.gpkg missing2020_r2 


1905_2
2405_2
2602_1
2507_1
2604_2
2605_2
2709_0
3404_3
3102_1
3402_1
806_0
901_0
802_0


# 60
distribution_2020_60dist99 = get_distribution_by_dist(11.545177773538338, "2020_60dist99.pkl", 60)
distribution_2020_60dist95 = get_distribution_by_dist(9.170721365915652, "2020_60dist95.pkl", 60)
distribution_2020_60dist90 = get_distribution_by_dist(8.08627100096902, "2020_60dist90.pkl", 60)
distribution_2020_60dist85 = get_distribution_by_dist(7.528400337266891, "2020_60dist85.pkl", 60)
distribution_2020_60dist80 = get_distribution_by_dist(7.150468868574022, "2020_60dist80.pkl", 60)

# 65
distribution_2020_65dist99 = get_distribution_by_dist(11.545177773538338, "2020_65dist99.pkl", 65)
distribution_2020_65dist95 = get_distribution_by_dist(9.170721365915652, "2020_65dist95.pkl", 65)
distribution_2020_65dist90 = get_distribution_by_dist(8.08627100096902, "2020_65dist90.pkl", 65)
distribution_2020_65dist85 = get_distribution_by_dist(7.528400337266891, "2020_65dist85.pkl", 65)
distribution_2020_65dist80 = get_distribution_by_dist(7.150468868574022, "2020_65dist80.pkl", 65)

# 70
distribution_2020_70dist99 = get_distribution_by_dist(11.545177773538338, "2020_70dist99.pkl", 70)
distribution_2020_70dist95 = get_distribution_by_dist(9.170721365915652, "2020_70dist95.pkl", 70)
distribution_2020_70dist90 = get_distribution_by_dist(8.08627100096902, "2020_70dist90.pkl", 70)
distribution_2020_70dist85 = get_distribution_by_dist(7.528400337266891, "2020_70dist85.pkl", 70)
distribution_2020_70dist80 = get_distribution_by_dist(7.150468868574022, "2020_70dist80.pkl", 70)


# 75
distribution_2020_75dist99 = get_distribution_by_dist(11.545177773538338, "2020_75dist99.pkl", 75)
distribution_2020_75dist95 = get_distribution_by_dist(9.170721365915652, "2020_75dist95.pkl", 75)
distribution_2020_75dist90 = get_distribution_by_dist(8.08627100096902, "2020_75dist90.pkl", 75)
distribution_2020_75dist85 = get_distribution_by_dist(7.528400337266891, "2020_75dist85.pkl", 75)
distribution_2020_75dist80 = get_distribution_by_dist(7.150468868574022, "2020_75dist80.pkl", 75)

# 80
distribution_2020_80dist99 = get_distribution_by_dist(11.545177773538338, "2020_80dist99.pkl", 80)
distribution_2020_80dist95 = get_distribution_by_dist(9.170721365915652, "2020_80dist95.pkl", 80)
distribution_2020_80dist90 = get_distribution_by_dist(8.08627100096902, "2020_80dist90.pkl", 80)
distribution_2020_80dist85 = get_distribution_by_dist(7.528400337266891, "2020_80dist85.pkl", 80)
distribution_2020_80dist80 = get_distribution_by_dist(7.150468868574022, "2020_80dist80.pkl", 80)



# 85
distribution_2020_85dist99 = get_distribution_by_dist(11.545177773538338, "2020_85dist99.pkl", 85)
distribution_2020_85dist95 = get_distribution_by_dist(9.170721365915652, "2020_85dist95.pkl", 85)
distribution_2020_85dist90 = get_distribution_by_dist(8.08627100096902, "2020_85dist90.pkl", 85)
distribution_2020_85dist85 = get_distribution_by_dist(7.528400337266891, "2020_85dist85.pkl", 85)
distribution_2020_85dist80 = get_distribution_by_dist(7.150468868574022, "2020_85dist80.pkl", 85)

# 90
distribution_2020_90dist99 = get_distribution_by_dist(11.545177773538338, "2020_90dist99.pkl", 90)
distribution_2020_90dist95 = get_distribution_by_dist(9.170721365915652, "2020_90dist95.pkl", 90)
distribution_2020_90dist90 = get_distribution_by_dist(8.08627100096902, "2020_90dist90.pkl", 90)
distribution_2020_90dist85 = get_distribution_by_dist(7.528400337266891, "2020_90dist85.pkl", 90)
distribution_2020_90dist80 = get_distribution_by_dist(7.150468868574022, "2020_90dist80.pkl", 90)


# 95
distribution_2020_95dist99 = get_distribution_by_dist(11.545177773538338, "2020_95dist99.pkl", 95)
distribution_2020_95dist95 = get_distribution_by_dist(9.170721395915952, "2020_95dist95.pkl", 95)
distribution_2020_95dist90 = get_distribution_by_dist(8.08627100096902, "2020_95dist90.pkl", 95)
distribution_2020_95dist85 = get_distribution_by_dist(7.528400337266891, "2020_95dist95.pkl", 95)
distribution_2020_95dist80 = get_distribution_by_dist(7.150468869574022, "2020_95dist80.pkl", 95)




nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/missing2020_r2 model=/data/tmp/arogya/results/aoi_2020/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=15 year=2020 out=/data/tmp/arogya/results/missing2020_r2/predictions interim=/data/tmp/arogya/results/missing2020_r2/interim > logs/2020_missing_r2.out &


nohup ./predict.sh process=solo shp=/data/tmp/arogya/inputs/aoi.gpkg model=/data/tmp/arogya/results/aoimodal2020_v2/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=5 year=2020 out=../data/2020_modalroa/predictions interim=../data/2020_modalroa/interim > logs/2020_modalroa.out &

# Remove old files
rm -rf /data/tmp/arogya/results/test
mkdir  /data/tmp/arogya/results/test

# Go to incomplete predictions folder
find . -type f \( -name '*.tif' -o -name '*.csv' -o -name '*.png' \) |
tar -cf - -T - |
tar -xf - -C /data/tmp/arogya/results/test/

\cp -r ../../test/* ../../aoi_2019/predictions/


Wq=torch.tensor(nn.Linear(self.input_embedding_size, self.query_key_size)).to(device)
Wk=torch.tensor(nn.Linear(self.input_embedding_size, self.query_key_size)).to(device)
Wv=torch.tensor(nn.Linear(self.input_embedding_size, self.input_embedding_size)).to(device)




cp /data/tmp/arogya/inputs/grids_50km/2308* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2302* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2312* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2303* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2306* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2304* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2407* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2601* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1905* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1906* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2105* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2311* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1903* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2307* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1904* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2313* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2111* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/2416* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1115* /data/tmp/arogya/inputs/HFPdistricts2020/
cp /data/tmp/arogya/inputs/grids_50km/1606* /data/tmp/arogya/inputs/HFPdistricts2020/



# 2019

cp /data/tmp/arogya/inputs/grids_50km/2308* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2302* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2312* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2303* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2306* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2304* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2407* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2601* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/1905* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2605* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/1906* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2307* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/1608* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2105* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2311* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2111* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2416* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/1606* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/1607* /data/tmp/arogya/inputs/HFPdistricts2019/ 
cp /data/tmp/arogya/inputs/grids_50km/2106* /data/tmp/arogya/inputs/HFPdistricts2019/ 


nohup ./fit_predict.sh model=kmeans n=3 mode_in=multi shp_in=/data/tmp/arogya/inputs/HFPgrids2020 mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/HFPgrids2020 shp_out=/data/tmp/arogya/inputs/HFPdistricts2020 mode_out=multi > logs/HFPgrids2020.out &


## to run
nohup ./fit_predict.sh model=kmeans n=3 mode_in=multi shp_in=/data/tmp/arogya/inputs/HFPgrids2019 mask=/data/tmp/arogya/inputs/mask.tif year=2019 cores=20 out=/data/tmp/arogya/results/HFPgrids2019 shp_out=/data/tmp/arogya/inputs/HFPdistricts2019 mode_out=multi > logs/HFPgrids2019.out &



./fit_predict.sh mode_in=multi shp_in=../data/poppydata/inputs/roa_nontiled mask=../data/poppydata/inputs/mask.tif year=2020 cores=6
model=kmeans n=3 out=../data/poppydata/roamrs_2020 shp_out=../data/poppydata/inputs/roa_nontiled mode_out=multi


./fit_predict.sh mode_in=multi shp_in=../data/poppydata/inputs/roa_nontiled mask=../data/poppydata/inputs/mask.tif year=2020 cores=6 model=kmeans n=3 out=../data/poppydata/roa_nontiled2020 shp_out=../data/poppydata/inputs/roa_nontiled mode_out=multi


nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/aoimodal2020 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoimodal2020.out &

nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/aoimodal2020 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoimodal2020.out &


nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/incomplete_aoimodal model=/data/tmp/arogya/results/aoimodal2020/models/model-kmeans-3/ mask=/data/tmp/arogya/inputs/mask.tif cores=15 year=2020 out=/data/tmp/arogya/results/aoimodal2020_missing/predictions interim=/data/tmp/arogya/results/aoimodal2020_missing/interim > logs/aoimodal2020_missing.out &


nohup ./predict.sh process=solo shp=../data/poppydata/inputs/1115_1.gpkg model=../models mask=../data/poppydata/inputs/mask.tif  year=2020 out=../data/poppydata/aoimodal1103/predictions interim=../data/poppydata/aoimodal1103/predictions > logs/aoimodal2020_missing.out &



# nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/aoi.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/aoimodal2020_v2 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/aoimodal2020_v2.out &

year=2020
label=aoimodal-2020-02-28-2020
cores=20

# label=$1
./fit_predict.sh model=kmeans n=3 mode_in=multi shp_in=/data/tmp/arogya/inputs/aoi_nadali_qandahar mask=/data/tmp/arogya/inputs/mask.tif year=$year cores=$cores out=/data/tmp/arogya/results/$label shp_out=/data/tmp/arogya/inputs/subset mode_out=multi > logs/${label}_modeling.out &

nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/aoi_nadali_qandahar model=/data/tmp/arogya/results/$label/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=$cores year=$year out=../data/$label/predictions interim=../data/$label/interim > logs/${label}_subset_predict.out &

nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/aoi_nadali_qandahar model=/data/tmp/arogya/results/$label/models/model-kmeans-3 mask=/data/tmp/arogya/inputs/mask.tif cores=$cores year=$year out=../data/$label/predictions interim=../data/$label/interim > logs/${label}_full_predict.out &



cp 1004_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1112_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1103_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1102_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1007_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1111_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1103_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1005_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1302_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1124_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1124_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1123_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1307_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1124_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1118_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1112_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1125_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1113_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1126_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1115_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1113_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1702_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1701_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1702_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1804_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1705_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1711_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1904_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1904_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1904_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1813_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2006_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1905_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2004_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1906_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1907_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2004_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1906_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 1907_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2012_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2101_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2103_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2101_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2014_6.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2014_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2109_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2105_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2106_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_14.gpk /data/tmp/arogya/inputs/incomplete/
cp 2203_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_6.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_7.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_8.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_10.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_9.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2205_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2205_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2203_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2306_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2205_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2305_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2205_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2205_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2307_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2309_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2310_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2308_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_7.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_9.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_6.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_10.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2311_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2313_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2403_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2406_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2404_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2407_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2402_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2402_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2406_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2402_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2405_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2407_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2408_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2408_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2413_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2415_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2408_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2408_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2412_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2413_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2411_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2412_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2408_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2603_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2603_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2603_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2602_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2604_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2507_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2507_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2601_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2601_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2601_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2605_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2703_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2705_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2706_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2706_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2702_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2703_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3102_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2710_4.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2710_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3103_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2709_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2707_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3103_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2707_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3101_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 2707_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3402_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3402_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3402_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3409_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3407_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3402_3.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3408_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3404_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3404_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3402_5.gpkg /data/tmp/arogya/inputs/incomplete/
cp 3409_1.gpkg /data/tmp/arogya/inputs/incomplete/
cp 822_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 605_2.gpkg /data/tmp/arogya/inputs/incomplete/
cp 901_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 605_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 816_0.gpkg /data/tmp/arogya/inputs/incomplete/
cp 902_0.gpkg /data/tmp/arogya/inputs/incomplete/


nohup ./predict.sh process=multi shp=/data/tmp/arogya/inputs/incomplete model=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/models/model-kmeans-3/ mask=/data/tmp/arogya/inputs/mask.tif cores=15 year=2020 out=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/predictions interim=/data/tmp/arogya/results/aoimodal-2020-20230301-0106/interim > logs/aoimodal-2020-20230301-0106-incomplete.out &


rm -rf 1004_0
rm -rf 1112_0
rm -rf 1103_1
rm -rf 1102_0
rm -rf 1007_0
rm -rf 1111_0
rm -rf 1103_0
rm -rf 1005_0
rm -rf 1302_0
rm -rf 1124_0
rm -rf 1124_2
rm -rf 1123_0
rm -rf 1307_0
rm -rf 1124_1
rm -rf 1118_0
rm -rf 1112_1
rm -rf 1125_0
rm -rf 1113_0
rm -rf 1126_0
rm -rf 1115_0
rm -rf 1113_1
rm -rf 1702_1
rm -rf 1701_2
rm -rf 1702_2
rm -rf 1804_0
rm -rf 1705_1
rm -rf 1711_0
rm -rf 1904_1
rm -rf 1904_5
rm -rf 1904_2
rm -rf 1813_0
rm -rf 2006_1
rm -rf 1905_2
rm -rf 2004_1
rm -rf 1906_0
rm -rf 1907_1
rm -rf 2004_0
rm -rf 1906_2
rm -rf 1907_0
rm -rf 2012_1
rm -rf 2101_4
rm -rf 2103_2
rm -rf 2101_1
rm -rf 2014_6
rm -rf 2014_1
rm -rf 2109_2
rm -rf 2105_2
rm -rf 2106_2
rm -rf 2203_1
rm -rf 2203_2
rm -rf 2203_6
rm -rf 2203_0
rm -rf 2203_1
rm -rf 2203_7
rm -rf 2203_8
rm -rf 2203_10
rm -rf 2203_5
rm -rf 2203_9
rm -rf 2205_0
rm -rf 2205_1
rm -rf 2203_4
rm -rf 2306_3
rm -rf 2205_5
rm -rf 2305_0
rm -rf 2205_3
rm -rf 2205_4
rm -rf 2307_0
rm -rf 2310_0
rm -rf 2310_2
rm -rf 2310_1
rm -rf 2310_3
rm -rf 2310_4
rm -rf 2309_0
rm -rf 2310_5
rm -rf 2308_0
rm -rf 2311_7
rm -rf 2313_0
rm -rf 2313_9
rm -rf 2313_2
rm -rf 2311_0
rm -rf 2313_6
rm -rf 2313_4
rm -rf 2311_1
rm -rf 2311_2
rm -rf 2313_1
rm -rf 2311_4
rm -rf 2313_10
rm -rf 2313_3
rm -rf 2311_5
rm -rf 2313_5
rm -rf 2403_0
rm -rf 2406_0
rm -rf 2404_0
rm -rf 2407_1
rm -rf 2402_1
rm -rf 2402_2
rm -rf 2406_2
rm -rf 2402_0
rm -rf 2405_2
rm -rf 2407_0
rm -rf 2408_4
rm -rf 2408_3
rm -rf 2413_1
rm -rf 2415_0
rm -rf 2408_2
rm -rf 2408_0
rm -rf 2412_1
rm -rf 2413_0
rm -rf 2411_2
rm -rf 2412_2
rm -rf 2408_1
rm -rf 2603_2
rm -rf 2603_3
rm -rf 2603_1
rm -rf 2602_3
rm -rf 2604_1
rm -rf 2507_2
rm -rf 2507_0
rm -rf 2601_2
rm -rf 2601_1
rm -rf 2601_0
rm -rf 2605_2
rm -rf 2703_1
rm -rf 2705_1
rm -rf 2706_3
rm -rf 2706_4
rm -rf 2702_1
rm -rf 2703_2
rm -rf 3102_0
rm -rf 2710_4
rm -rf 2710_2
rm -rf 3103_0
rm -rf 2709_0
rm -rf 2707_1
rm -rf 3103_3
rm -rf 2707_3
rm -rf 3101_1
rm -rf 2707_2
rm -rf 3402_2
rm -rf 3402_0
rm -rf 3402_1
rm -rf 3409_3
rm -rf 3407_1
rm -rf 3402_3
rm -rf 3408_1
rm -rf 3404_2
rm -rf 3404_1
rm -rf 3402_5
rm -rf 3409_1
rm -rf 822_0
rm -rf 605_2
rm -rf 901_0
rm -rf 605_0
rm -rf 816_0
rm -rf 902_0
