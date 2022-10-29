import eeconvert as eeconvert
import ee
import geemap
import geopandas as gpd
import rasterio as rio
import numpy as np
import rasterio.features as features
from pathlib import Path
import os
import shutil
from shapely.geometry import Point
import numpy as np
import time
import multiprocessing as mp
from time import sleep
import random

ee.Initialize()


class DatesHelper:
    def __init__(self, DATA_DIR, AOI, DATE_RANGE, n_cores = 10,  bypass=False):
        self.data_dir = DATA_DIR
        self.aoi = AOI
        self.date_range = DATE_RANGE
        self.n_cores = n_cores
        self.bypass=bypass
    
    
    def download_modis(self, max_ndvi_image):
        parent = gpd.read_file(f"{self.data_dir}/interim/parent_best_dates.gpkg")        

        cpus = self.n_cores
        parent_chunks = np.array_split(parent, cpus)
        pool = mp.Pool(processes=cpus)
        chunk_processes = [pool.apply_async(self._download_modis_chunk, args=(max_ndvi_image, chunk, parent)) for chunk in parent_chunks]
        chunk_results = [chunk.get() for chunk in chunk_processes]
        
        
    
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
          

    def extract_best_dates(self):
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
        print(f"Done with MODIS best date calculation.. - {time.time()-start} sec")
        
        # Download modis tiles at parent resolution
        DATA_DIR = self.data_dir
        MODIS_DIR = f"{self.data_dir}/interim/modis"
        self.modis_dir = MODIS_DIR
        if os.path.exists(MODIS_DIR):
            shutil.rmtree(MODIS_DIR)
        TILE_DIR = f"{self.modis_dir}/tiles" 
        self.tile_dir = TILE_DIR
        Path(TILE_DIR).mkdir(parents=True, exist_ok=True)
        Path(MODIS_DIR).mkdir(parents=True, exist_ok=True)
        
        if not self.bypass:
            self.download_modis(max_ndvi_image)
        

        
        
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

        # Merge downloaded modis tiles into one
        os.system(f'find {TILE_DIR}  -maxdepth 1 -name "*.tif" -print0 | xargs --null -I{"{}"} gdalbuildvrt {MODIS_DIR}/temp.vrt {"{}"} -srcnodata "0"')
        os.system(f'gdal_merge.py -o {MODIS_DIR}/merged.tif {MODIS_DIR}/temp.vrt')
        
        print(f"Merged tiles.. - {time.time()-start} sec")
        
        
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
        
        print(f"Shell GDF created.. - {time.time()-start} sec")        
    
        os.system(f'gdal_polygonize.py {MODIS_DIR}/shell.tif -b 1 -f "GPKG" {MODIS_DIR}/shell.gpkg OUTPUT DateCode')
        print(f"Polygonized shell.. - {time.time()-start} sec")
        
        os.system(f'gdal_polygonize.py {MODIS_DIR}/merged.tif -b 1 -f "GPKG" {MODIS_DIR}/merged.gpkg OUTPUT DateCode')
        print(f"Polygonized merged.. - {time.time()-start} sec")
        
        with rio.open(f"{MODIS_DIR}/merged.tif") as src:
            band1 = src.read(1)
            height = band1.shape[0]
            width = band1.shape[1]
            cols, rows = np.meshgrid(np.arange(width), np.arange(height))
            xs, ys = rio.transform.xy(src.transform, rows, cols)
            lons = np.array(xs)
            lats = np.array(ys)

            points = gpd.GeoSeries(
                list(zip(lons.flatten(), lats.flatten()))).map(Point)

            # use the feature loop in case shp is multipolygon
            geoms = points.values
            features = [i for i in range(len(geoms))]

            out = gpd.GeoDataFrame(
                {'feature': features, 'geometry': geoms}, crs=src.crs)
            out.to_file(f"{MODIS_DIR}/centroids.gpkg", driver="GPKG")
        merged = gpd.read_file(f"{MODIS_DIR}/merged.gpkg")
        centroids = gpd.read_file(f"{MODIS_DIR}/centroids.gpkg")
        centroids = centroids.sjoin(merged, how="inner", predicate='intersects')
        centroids = centroids[['feature', 'geometry', 'DateCode']]
        print(f"Created Centroids.. - {time.time()-start} sec")
        
        child = gpd.read_file(f"{self.data_dir}/interim/child.gpkg")
        child = child.sjoin(centroids,  how="inner", predicate='intersects')
        child = child[['DateCode', 'geometry']]
        child['DateCode'] = child['DateCode'].astype(str)
        child = child.replace({"DateCode": self.date_dict})
        child = child.reset_index()
        child.columns = ["grid_id", "BSD", "geometry"]
        child.to_file(f"{MODIS_DIR}/child.gpkg", driver="GPKG")
        child = gpd.read_file(f"{MODIS_DIR}/child.gpkg")
        child = child[child['BSD'] != "-99"]
        child = child.reset_index()
        child = child[['index', 'BSD', 'geometry']]
        child.columns = ['grid_id', 'BSD', 'geometry']
        child.to_file(f"{self.data_dir}/interim/child.gpkg", driver="GPKG")
        print(f"Saved child GDF. Completed! - {time.time()-start} sec")
    
#         self.alt_joined = child
        
#         shell = gpd.read_file(f"{DATA_DIR}/interim/shell.gpkg")
#         joined = shell.sjoin(centroids,  how="inner", predicate='intersects')
#         child = joined # dev: comment and rename 'joined' to 'child' in line above last
#         child = child[["DateCode_right", "geometry"]]
#         child['DateCode_right'] = child['DateCode_right'].astype(str)
#         child = child.replace({"DateCode_right": self.date_dict})
#         child = child[child['DateCode_right'] != "-99"] # why is this -99?
#         child = child.reset_index()
#         child.columns = ["GRID_ID", "BSD", "geometry"]
#         child.to_file(f"{DATA_DIR}/interim/modis.gpkg", driver="GPKG")
#         child = gpd.read_file(f"{DATA_DIR}/interim/modis.gpkg")
# #         print(child.columns)
#         child = child[child['BSD'] != "-99"]
#         child = child.reset_index()
#         child = child[['index', 'BSD', 'geometry']]
#         child.columns = ['grid_id', 'BSD', 'geometry']
#         child.to_file(f"{DATA_DIR}/interim/modis.gpkg", driver="GPKG")
#         print(f"Saved child GDF. Completed! - {time.time()-start} sec")
        
        
#         self.merged = merged
#         self.centroids = centroids
# #         self.joined = joined
#         self.child = child
        