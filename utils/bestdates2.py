import eeconvert as eeconvert
import ee
import geemap
import geopandas as gpd
import rasterio as rio
import numpy as np
from pathlib import Path
import os
import shutil
from shapely.geometry import Point
import numpy as np
import time
import multiprocessing as mp
from time import sleep
import random
import pandas as pd

from scipy import stats as st
from rasterio.mask import mask
from rasterio import features
from shapely.geometry import mapping, shape


from osgeo import gdal

vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)
gdal.BuildVRT('my.vrt', ['one.tif', 'two.tif'], options=vrt_options)

ee.Initialize()


class DatesHelper:
    def __init__(self, DATA_DIR, AOI, DATE_RANGE, n_cores = 1,  bypass=False):
        self.data_dir = DATA_DIR
        self.aoi = AOI
        self.date_range = DATE_RANGE
        self.n_cores = n_cores
        self.bypass=bypass
    
    
    def download_modis(self, parent, max_ndvi_image):
#         self.parent= gpd.read_file(f"{self.data_dir}/interim/parent_best_dates.gpkg")        
#         if os.path.exists(self.tile_dir):
#            shutil.rmtree(self.tile_dir)
        cpus = self.n_cores
        parent_chunks = np.array_split(parent, cpus)
        pool = mp.Pool(processes=cpus)
        chunk_processes = [pool.apply_async(self._download_modis_chunk, args=(max_ndvi_image, chunk, parent)) for chunk in parent_chunks]
        chunk_results = [chunk.get() for chunk in chunk_processes]
        print(os.listdir(self.tile_dir))
        
        
    
    def _download_modis_chunk(self, max_ndvi_image, gdf_chunk, gdf_complete):
        sleep(random.random()*2.0)
        
        for index,row in gdf_chunk.iterrows():
            aoi = ee.Geometry.Rectangle(row.geometry.bounds)
            geemap.ee_export_image(
                max_ndvi_image, 
                filename=f"{self.tile_dir}/{row.pgrid_id}.tif", 
                scale=250, 
                region=aoi, 
                file_per_band=False
            )
          

        
    def extract_best_dates(self, mask_tif=None, crop_proba=80, grid_path = None):
        start = time.time()
        # Get best date for each tile

        
        aoi = eeconvert.gdfToFc(gpd.read_file(self.aoi))
        afghanistan = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0").filter("ADM0_NAME == 'Afghanistan'");
        modis = ee.ImageCollection('MODIS/061/MOD13Q1').filter(ee.Filter.date(self.date_range[0], self.date_range[1]));
        dates = modis.map(lambda x: ee.Feature(None, {'date': x.date().format('YYYY-MM-dd')})).distinct('date').aggregate_array('date')        
        dates = dates.getInfo()
        
        ndvi = modis.select('NDVI');
        ndvi_array = ndvi.toArray();
        max_ndvi_date = ndvi_array.arrayArgmax();
        max_ndvi_image = ee.Image(max_ndvi_date).arrayProject([0]).arrayFlatten([['maxDate_start', 'band2']]).clip(aoi).select("maxDate_start");
        self.max_ndvi_image = max_ndvi_image
        # Remap values so '0' doesnt overlap with nodata        
        fromValues = []
        i = 0
        for date in dates:
            fromValues.append(i)
            i +=1

        toValues = []
        for val in fromValues:
            toValues.append(val+1)

        max_ndvi_image = max_ndvi_image.remap(**{
          "from": fromValues,
          "to": toValues,
          "defaultValue": 0,
          "bandName": 'maxDate_start'
        });
        
        
        # Create a value - date hashmap for future remapping
        self.date_dict = {}
        i = 1
        for date in dates:
            self.date_dict[str(i)] = date
            i+=1
        self.date_dict["0"] = -99
        print(f"-------- Done with MODIS best date calculation..")
        
        # Download modis tiles at parent resolution
        DATA_DIR = self.data_dir
        MODIS_DIR = f"{self.data_dir}/modis"
        self.modis_dir = MODIS_DIR
        if os.path.exists(MODIS_DIR):
            shutil.rmtree(MODIS_DIR)
        TILE_DIR = f"{self.modis_dir}/tiles" 
        self.tile_dir = TILE_DIR
        Path(TILE_DIR).mkdir(parents=True, exist_ok=True)
        Path(MODIS_DIR).mkdir(parents=True, exist_ok=True)
        
        if grid_path is None:
            grid_path = f"{self.data_dir}/parent.gpkg"
        parent = gpd.read_file(grid_path)        
        
        if not self.bypass:
            self.download_modis(parent, max_ndvi_image)
            self.fix_until_complete(grid_path=grid_path)    
        
        
        if os.path.exists(f"{MODIS_DIR}/interim/temp.vrt"):
            os.remove(f"{MODIS_DIR}/interim/temp.vrt")
        if os.path.exists(f"{MODIS_DIR}/interim/merged.tif"):
            os.remove(f"{MODIS_DIR}/interim/merged.tif")
        if os.path.exists(f"{MODIS_DIR}/interim/merged.gpkg"):
            os.remove(f"{MODIS_DIR}/interim/merged.gpkg")
        if os.path.exists(f"{MODIS_DIR}/interim/shell.tif"):
            os.remove(f"{MODIS_DIR}/interim/shell.tif")
        if os.path.exists(f"{MODIS_DIR}/interim/shell.tif"):
            os.remove(f"{MODIS_DIR}/interim/shell.gpkg")
        if os.path.exists(f"{MODIS_DIR}/interim/centroids.gpkg"):
            os.remove(f"{MODIS_DIR}/interim/centroids.gpkg")


        print(os.listdir(TILE_DIR))

        if len(os.listdir(TILE_DIR)) > 1:
            # Merge downloaded modis tiles into one
            # raw = [f"{TILE_DIR}/{f}" for f in os.listdir(TILE_DIR)]
            # print(raw)
            # vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)
            # gdal.BuildVRT(f'{MODIS_DIR}/temp.vrt', raw, options=vrt_options)
            os.system(f'find {TILE_DIR}  -maxdepth 1 -name "*.tif" -print0 | xargs -0 gdalbuildvrt -srcnodata "0" {MODIS_DIR}/temp.vrt')
            os.system(f'gdal_merge.py -o {MODIS_DIR}/merged.tif {MODIS_DIR}/temp.vrt')
        else:
            os.system(f'cp {TILE_DIR}/0.tif {MODIS_DIR}/merged.tif')
        print(f"-------- Merged tiles..")
        
        
        # Create shell GDF (workaround because polygonize doesn't uncombine tiles with same value)
        with rio.open(f"{MODIS_DIR}/merged.tif") as src:
            array = src.read(1)
            transform = src.transform
            crs = src.crs
            profile = src.profile

        h, w = array.shape

        new_array = np.arange(h*w).reshape(h,w)

        with rio.Env():

            # Write an array as a raster band to a new 8-bit file. For
            # the new file's profile, we start with the profile of the source
            profile = src.profile

            # And then change the band count to 1, set the
            # dtype to uint8, and specify LZW compression.
            profile.update(
                dtype=rio.uint32,
                count=1,
                compress='lzw')

            with rio.open(f'{MODIS_DIR}/shell.tif', 'w', **profile) as dst:
                dst.write(new_array.astype(rio.uint32), 1)
        
        print(f"-------- Shell GDF created..")        
    
        os.system(f'gdal_polygonize.py {MODIS_DIR}/shell.tif -b 1 -f "GPKG" {MODIS_DIR}/shell.gpkg OUTPUT DateCode')
        print(f"-------- Polygonized shell..")
        
        os.system(f'gdal_polygonize.py {MODIS_DIR}/merged.tif -b 1 -f "GPKG" {MODIS_DIR}/merged.gpkg OUTPUT DateCode')
        print(f"-------- Polygonized merged..")
        
        with rio.open(f"{MODIS_DIR}/merged.tif") as src:
            band1 = src.read(1)
            height = band1.shape[0]
            width = band1.shape[1]
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            xs, ys = rio.transform.xy(src.transform, rows, cols)
            lons = np.array(xs).flatten().tolist()
            lats = np.array(ys).flatten().tolist()

            df = pd.DataFrame({
                # "id": np.arange(0,len(lons))
                "lat": lats,
                "lon": lons
            })

            # print(list(zip(lons.flatten(), lats.flatten())))
            # points = gpd.GeoSeries(
            #     list(zip(lons.flatten(), lats.flatten()))).map(Point)

            # # use the feature loop in case shp is multipolygon
            # geoms = points.values
            # features = [i for i in range(len(geoms))]

            # out = gpd.GeoDataFrame(
            #     {'feature': features, 'geometry': geoms}, crs=src.crs)
            out = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
            out = out.set_crs(src.crs)
            
            out.to_file(f"{MODIS_DIR}/centroids.gpkg", driver="GPKG")
        merged = gpd.read_file(f"{MODIS_DIR}/merged.gpkg")
        centroids = gpd.read_file(f"{MODIS_DIR}/centroids.gpkg")
        centroids = centroids.sjoin(merged, how="inner", predicate='intersects')
        centroids = centroids[['geometry', 'DateCode']]
        print(f"-------- Created Centroids..")
        
        child = gpd.read_file(f"{self.data_dir}/child.gpkg")
        child.to_file(f"{self.data_dir}/child_bkp.gpkg", driver="GPKG")
        child = child.sjoin(centroids,  how="inner", predicate='intersects') ######################### change to centroids.
        child = child[['DateCode', 'geometry']]
        child['DateCode'] = child['DateCode'].astype(str)
        child = child.replace({"DateCode": self.date_dict})
        child = child.reset_index()
        child.columns = ["grid_id", "BSD", "geometry"]
        child.to_file(f"{self.data_dir}/child.gpkg", driver="GPKG")
        child = gpd.read_file(f"{self.data_dir}/child.gpkg")
        child = child[child['BSD'] != "-99"]
        child = child.reset_index()
        child = child[['index', 'BSD', 'geometry']]
        child.columns = ['grid_id', 'BSD', 'geometry']

        child.to_file(f"{self.data_dir}/child_non_modal.gpkg")


        if mask_tif is  None:
            print('Mask file missing')
            return False
        # Begin modal best date calculation
        mask_raster = rio.open(mask_tif)
        out_img, out_transform = mask(mask_raster, shapes=child.geometry, crop=True)
        out_img[out_img == 255] = 0
        is_valid = (out_img > crop_proba).astype(np.uint8)

        cropland = []
        for coords, value in features.shapes(is_valid, transform=out_transform):
            geom = shape(coords)
            cropland.append({"geometry": geom, "value" : value})

        cropland = gpd.GeoDataFrame(cropland).set_crs("epsg:4326")
        cropland = cropland[cropland['value']==1]

        joined = child.sjoin(cropland)
        if len(joined) > 0:
            modal_date = st.mode(joined[['BSD']].to_numpy().squeeze())[0][0]
            print("Modal best date:", modal_date)
            all_dates = sorted(list(np.unique(joined['BSD'])))

            print("All dates:",all_dates)
            new_bsd = all_dates[all_dates.index(modal_date)]
            print("new_best_date:", new_bsd)
            child['BSD'] = new_bsd
        else:
            return False
        # End modal best date calculation

        if len(child) > 0:
            child.to_file(f"{self.data_dir}/child.gpkg", driver="GPKG")
        print(f"-------- Saved child GDF. Completed!")
        return True

    def get_missing(self, grid_path=None):
        if grid_path is None:
            grid_path = f"{self.data_dir}/parent.gpkg"
        MODIS_DIR = f"{self.data_dir}/modis"
        TILES_DIR = MODIS_DIR + "/tiles"
        parent = gpd.read_file(grid_path)        
        all_ids_ = set(parent['pgrid_id'])
        downloaded_ids_ = set([int(file.split(".tif")[0]) for file in os.listdir(TILES_DIR)])
        missing = list(all_ids_ - downloaded_ids_)
        return missing
        
    def fix_until_complete(self, grid_path=None):
        complete = False
        if grid_path is None:
            grid_path = f"{self.data_dir}/parent.gpkg"
        while not complete:
            missing = self.get_missing(grid_path)
            if len(missing) > 0:
                print(f"#### Missing {len(missing)} tiles, redownloading..")
                parent= gpd.read_file(grid_path)        
#                 new_parent = parent[parent['pgrid_id'].isin(missing)]
                self.download_modis(parent, self.max_ndvi_image)
            else:
                print(f"#### Missing 0 tiles, proceeding to merge..")
                complete = True