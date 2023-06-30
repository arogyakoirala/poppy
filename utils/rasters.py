
# https://swanlund.space/parallelizing-python
from datetime import date, timedelta
import eeconvert as eeconvert
import ee
import geemap
import multiprocessing as mp
import geopandas as gpd
import os
import shutil
import numpy as np
import pickle
from progress.bar import Bar
from pathlib import Path

import rioxarray as rxr
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon

import pandas as pd
import rasterio
from rasterio import Affine
from rasterio.plot import show
from rasterio.windows import Window
import matplotlib.pyplot as plt
from rasterio.mask import mask
from rasterio import features
import math, time
import os


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import pickle
import json 
import zarr

import matplotlib.pyplot as plt
import seaborn as sns


from osgeo import gdal
from osgeo.gdalconst import GA_Update

ee.Initialize()


# Imagehelpers
CLOUD_FILTER = 50
CLD_PRB_THRESH = 70 # Cloud probability (%); pixel values greater than are considered cloud
NIR_DRK_THRESH = 0.2 # Near-infrared reflectance; values less than are considered potential cloud shadow
CLD_PRJ_DIST = 5 # Maximum distance (km) to search for cloud shadows from cloud edges
BUFFER = 50 # Distance (m) to dilate the edge of cloud-identified objects

def remove_ag(img):
    afg_adm = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_NAME', 'Afghanistan'))
    land2019 = ee.Image("COPERNICUS/Landcover/100m/Proba-V-C3/Global/2019")
    afg_ag = land2019.select('discrete_classification')\
    .updateMask(land2019.select(['discrete_classification']).eq(40)).clip(afg_adm)
    
    return img.updateMask(afg_ag.select('discrete_classification').mask())

def mask_edges(img):
    """
    Mask the edges
    The masks for the 10m bands sometimes do not exclude bad data at
    scene edges, so we apply masks from the 20m and 60m bands as well.
    Example asset that needs this operation:
    COPERNICUS/S2_CLOUD_PROBABILITY/20190301T000239_20190301T000238_T55GDP
    """
    return img.updateMask(
      img.select('B8A').mask().updateMask(img.select('B9').mask()))

def remove_cloud_shadow(img):
    
    """
    Add cld_prb and is_cloud bands to image
    """
    temp = None
    
    # Get s2cloudless image, subset the probability band.    
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

    # Condition s2cloudless by the probability threshold value.    
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    temp = img.addBands(ee.Image([cld_prb, is_cloud]))
    
    
    """
    Add dark_pixels, cld_proj, shadows
    """
    not_water=temp.select('SCL').neq(6)
    
    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = temp.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')
    
    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(ee.Number(temp.get('MEAN_SOLAR_AZIMUTH_ANGLE')));
    
    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (temp.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': temp.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')
    
    temp = temp.addBands(ee.Image([dark_pixels, cld_proj, shadows]))
    
    
    """
    Add is_cld_shdw
    """
    
     # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = temp.select('clouds').add(temp.select('shadows')).gt(0)
    
    
    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(BUFFER*2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))
    
    
    """
    Update image to only include those pixels with no cloud or shadow
    """
    temp = temp.addBands(is_cld_shdw)
    
    not_cld_shdw = temp.select('cloudmask').Not()
    
    return temp.select('B.*').updateMask(not_cld_shdw)
    
    
def add_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi')
    return image.addBands([ndvi])

def mask_ndvi(image, ltOrGt, value):
    ndvi = image.select('ndvi')
    if(ltOrGt == 'gt'):
        return image.updateMask(ndvi.gt(value))
    else: 
        return image.updateMask(ndvi.lt(value))
    
def getSentinelCollection(aoi, start_date, end_date):
    # Import and filter S2 SR.
    s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER)) 
        .map(mask_edges)) # add this 
    

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2_sr_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))


class RasterGenerationHelper:

    def __init__(self, parent_path, child_path,  raster_output_dir, n_cores, clean=False, post_period_days=[30,45]):
        self.parent = gpd.read_file(parent_path)
        self.child = gpd.read_file(child_path)
        self.raster_output_dir = raster_output_dir + "/"
        self.post_period_days = post_period_days

        self.n_cores = n_cores
        self._make_dir()
        if not clean:
            self._ready()
            
    def get_rasters(self): 

        print(f'-------- Downloading {self.parent.shape[0]} tiles..')           
        if not os.path.isdir(self.raster_output_dir):
            os.makedirs(self.raster_output_dir)
            print("-------- Created new directory..".format(self.raster_output_dir))
        cpus = self.n_cores
#         cpus = 6
        parent_chunks = np.array_split(self.parent, cpus)
        pool = mp.Pool(processes=cpus)
        chunk_processes = [pool.apply_async(self._get_rasters_for_chunk, args=(chunk, self.parent)) for chunk in parent_chunks]
        chunk_results = [chunk.get() for chunk in chunk_processes]

    def _get_rasters_for_chunk(self, gdf_chunk, gdf_complete):
        
        for i, tile in gdf_chunk.iterrows():
            temp = self.child.sjoin(self.parent[self.parent['pgrid_id']==tile['pgrid_id']], how="inner", predicate="intersects")
#             temp = self.child.sjoin(self.parent)
            
            
            datewise_counts = temp.groupby(['BSD']).count()['grid_id'].sort_values(ascending=False)
            datewise_counts = datewise_counts.reset_index()
            datewise_counts = datewise_counts.reset_index().rename(columns={'index': 'Date Combo Code', 'grid_id': 'count'})
#             print("## TILE PGRID_ID present?", tile['pgrid_id'] in set(list(np.unique(self.parent['pgrid_id']))))
#             print("## PARENT PGRID_IDs", self.parent['pgrid_id'])
            images = []
            for index, row in datewise_counts.iterrows():
                
                bsd = row['BSD']
                
#                 bed = row['BED']
#                 print("###DATE", date.fromisoformat(bsd).isoformat())
                preStart = (date.fromisoformat(bsd) + timedelta(days = -7)).isoformat()
                preEnd = (date.fromisoformat(bsd) + timedelta(days = +7)).isoformat()
                postStart = (date.fromisoformat(bsd) + timedelta(days = +self.post_period_days[0])).isoformat()
                postEnd = (date.fromisoformat(bsd) + timedelta(days = +self.post_period_days[1])).isoformat()
                
                
                tileIDS = temp[(temp['BSD'] == bsd)]['grid_id'].to_list()
                
                aoiInput = eeconvert.gdfToFc(self.child[self.child['grid_id'].isin(tileIDS)])
                
                # Get pre
                preImage = getSentinelCollection(aoiInput, preStart, preEnd)
                pre_w_ndvi = (preImage.map(remove_cloud_shadow).map(add_ndvi).reduce(ee.Reducer.median()))

                # Get Post
                postImage = getSentinelCollection(aoiInput, postStart, postEnd)
                post_w_ndvi = (postImage.map(remove_cloud_shadow).map(add_ndvi).reduce(ee.Reducer.median()))
#                 postImage = getSentinelCollection(aoiInput, postStart, postEnd).first()
#                 postImage = ee.ImageCollection.fromImages([postImage]);

                combined = pre_w_ndvi.addBands([post_w_ndvi])   
    
                if len(combined.bandNames().getInfo()) > 13:
                
                    tmpNDVI = combined.select(['ndvi_median']).multiply(5000).rename('ndvi')
                    tmpNDVI_1 = combined.select(['ndvi_median_1']).multiply(5000).rename('ndvi1')
                    combined = combined.select('B.*', 'ndvi.*')

                    # Clip to AOI
                    combined_clip = combined.clip(aoiInput)
                    images.append(combined_clip)
            
            bounds = self.parent[self.parent['pgrid_id'] == tile['pgrid_id']].bounds
            minx, miny, maxx, maxy = np.max(bounds['minx']), np.max(bounds['miny']),np.max(bounds['maxx']),np.max(bounds['maxy'])
            aoi = ee.Geometry.Rectangle([minx, miny, maxx, maxy])

            mosaicked = ee.ImageCollection([*images]).mosaic()
#             print("BandsBrah", mosaicked.bandNames().getInfo())
            geemap.ee_export_image(
                mosaicked, 
                filename=self.raster_output_dir + str(tile['pgrid_id'])+".tif", 
                scale=10, 
                region=aoi, 
                file_per_band=False
            )
            
            
    def _filename_to_ids(self, filename):
        return int(filename.split(".tif")[0])
    
    def _ready(self):
        # print(list(filter(lambda x: x.endswith(".tif"), os.listdir(self.raster_output_dir))))
        
        files = list(map(self._filename_to_ids, list(filter(lambda x: x.endswith(".tif"), os.listdir(self.raster_output_dir)))))
        old_size = self.parent.shape[0]
        self.parent = self.parent[~self.parent['pgrid_id'].isin(files)]
        new_size = self.parent.shape[0]
        
        print("-------- Ignoring {} tiles as rasters for them are already generated; will only generate rasters for remaining {} tiles".format(old_size - new_size, new_size))
        
        
    def _make_dir(self):
        Path(self.raster_output_dir).mkdir(parents=True, exist_ok=True)



"""
MergeRasterSingleAoi(data_dir, shp_path, tiles_path)

Create a merged raster from independent
tiles, for a given shapefile.



Assumption: All tiles for the area of 
interest have been already downloaded
"""
class MergeRasterSingleAoi:
    
    def __init__(self, data_dir, shp_path, tiles_path):
        self.shp_path = shp_path
        self.tiles_path = tiles_path
        self.data_dir = data_dir
        
    def merge(self, filename="merged"):
        aoi = gpd.read_file(self.shp_path)
        parent = gpd.read_file(f"{self.data_dir}/parent.gpkg")
        
        df = gpd.sjoin(parent, aoi)
        rasters = list(self.tiles_path +'/' + (df['pgrid_id']).astype('str') + ".tif")
        
        temp_dir = f"{self.data_dir}/temp"
        
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        for file in rasters:
            if os.path.exists(file):
                shutil.copy(file, temp_dir + "/")
        
        if os.path.exists(f"{self.data_dir}/{filename}.vrt"):
            os.remove(f"{self.data_dir}/{filename}.vrt")
            
        if os.path.exists(f"{self.data_dir}/{filename}.tif"):
            os.remove(f"{self.data_dir}/{filename}.tif")

        raw = [f"{temp_dir}/{f}" for f in os.listdir(temp_dir) if ".tif" in f]
        vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True, srcNodata=None)
        gdal.BuildVRT(f'{self.data_dir}/{filename}.vrt', raw, options=vrt_options)
            
        # os.system(f'gdalbuildvrt {self.data_dir}/{filename}.vrt {temp_dir}/*.tif -srcnodata None')
        os.system(f'gdal_merge.py -o {self.data_dir}/{filename}.tif {self.data_dir}/{filename}.vrt')


        f = f'{self.data_dir}/{filename}.tif'
        nodata = 0
        # open the file for editing
        ras = gdal.Open(f, GA_Update)
        # loop through the image bands
        for i in range(1, ras.RasterCount + 1):
            # set the nodata value of the band
            ras.GetRasterBand(i).SetNoDataValue(nodata)
        # unlink the file object and save the results
        ras = None

        # os.system(f"gdal_translate -of GTiff -a_nodata 0 {self.data_dir}/{filename}_interim.tif {self.data_dir}/{filename}.tif")
        # os.remove(f"{self.data_dir}/{filename}_interim.tif")
        

        raster = rxr.open_rasterio(f'{self.data_dir}/{filename}.tif').squeeze()
        raster = raster.rio.clip(aoi.geometry.apply(mapping), aoi.crs)
        raster.rio.to_raster(f'{self.data_dir}/{filename}.tif')
        
        # shutil.rmtree(temp_dir)
        
class MergeRaster:
    """
    Makes analysis ready rasters for a 
    given shapefile. Assumes vectors and 
    rasters are already generated for 
    all of Afghanistan and they are stored 
    in self.out_dir.
    
    Asssumes the following files are present:
        * district shapefiles in self.aoi_path
        * vectors/parent.gpkg
        * rasters/bestdates_tiles/*.tif (2500mx2500m GeoTIFFs)
    """
    
    
    def __init__(self, aoi_path, out_dir, n_cores):
        self.aoi_path = aoi_path
        self.out_dir = out_dir
        self.start_time = time.time()
        self.n_cores = n_cores

    
            
    def _handle_chunk(self, aoi_chunk, aoi_complete):
        parent = gpd.read_file(self.out_dir + "/vectors/parent.gpkg")
        RASTER_OUTPUT_DIR = self.out_dir + "/rasters/bestdates_tiles"

        for file in aoi_chunk:
            poly = gpd.read_file(file)
            df = gpd.sjoin(parent, poly)
            rasters = list(RASTER_OUTPUT_DIR+'/' + (df['pgrid_id']).astype('str') + ".tif")
            dist_id = file.split("/districts/")[1].split(".gpkg")[0]
            temp_dir = self.out_path + "/temp_"+  dist_id
            Path(temp_dir).mkdir(parents=True, exist_ok=True)
            
            for file in rasters:
                shutil.copy(file, temp_dir+"/")

            
            print(f"--- Making VRT for District {dist_id}: {time.time() - self.start_time} seconds ---")
            os.system(f'gdalbuildvrt {temp_dir}/temp_{dist_id}.vrt {temp_dir}/*.tif -srcnodata "0"')
            print(f"--- Merging for District {dist_id}: {time.time() - self.start_time} seconds ---")
            os.system(f'gdal_merge.py -o {self.out_path}/merged_{dist_id}.tif {temp_dir}/temp_{dist_id}.vrt')
            
            print(f"--- Clipping for District {dist_id}: {time.time() - self.start_time} seconds ---")
            raster = rxr.open_rasterio(f'{self.out_path}/merged_{dist_id}.tif').squeeze()
            raster = raster.rio.clip(poly.geometry.apply(mapping), poly.crs)
            raster.rio.to_raster(f'{self.out_path}/merged_{dist_id}.tif')

    
    def merge_rasters(self, out_path): 
        self.out_path = out_path
        aois = list(map(lambda x: self.aoi_path + "/" + x, os.listdir(self.aoi_path)))
        print(aois)
        cpus = self.n_cores
        aoi_chunks = np.array_split(aois, cpus)
        pool = mp.Pool(processes=cpus)
        chunk_processes = [pool.apply_async(self._handle_chunk, args=(chunk, aois)) for chunk in aoi_chunks]
        chunk_results = [chunk.get() for chunk in chunk_processes]



class Masker:
    def __init__(self, data_dir, input_shp, input_raster, mask_raster):
        self.input_raster = rasterio.open(input_raster)
        self.input_shp = gpd.read_file(input_shp)
        self.mask_raster = rasterio.open(mask_raster)
        self.data_dir = data_dir
        
    def mask(self, filename="masked", gte=80):
        out_img, out_transform = mask(self.mask_raster, shapes=self.input_shp.geometry, crop=True)
        out_img[out_img < gte] = 255
        is_valid = (out_img != 255.0).astype(np.uint8)
        cropland = []
        for coords, value in features.shapes(is_valid, transform=out_transform):
#             print(value)
#             if value != 0:
            geom = shape(coords)
            cropland.append({"geometry": geom, "value" : value})
                
        cropland = gpd.GeoDataFrame(cropland).set_crs("epsg:4326")
        cropland = cropland[cropland['value']==1] # only get a shapefile of cropland
        out_img, out_transform = mask(self.input_raster, cropland.geometry, crop=True)
        out_img[np.isnan(out_img)] = -99
        out_img = out_img[0:24]
        with rasterio.open(
            f'{self.data_dir}/{filename}.tif',
            'w',
            driver='GTiff',
            height=out_img.shape[1],
            width=out_img.shape[2],
            count=out_img.shape[0],
            dtype='float32',
            crs=self.input_raster.crs,
            transform=out_transform,
        ) as dst:
            dst.nodata = -99
            dst.write(out_img[0:24])

class Sampler:
    def __init__(self, input_raster, interim_dir, out_dir):
        self.input_raster = input_raster
        self.out_dir = out_dir
        self.interim_dir = interim_dir
        
    def sample_zarr(self, sample_size, sample_filename="sample", full_filename="full", save_full = True):
        df, profile = self._generate_df_from_raster()
        sample_length = int(len(df) * sample_size)
        sample = df.sample(sample_length, random_state=7)

        copy = sample.copy()
        # # Get only relevant columns: lat/lng, differences, ndvi_pre, dayofyear

        full = copy[[*range(1,25), 'ndvi_pre', 'dayofyear', 'ndvi_post']]
        for col in range(1,13):
            copy[col] = copy[col+12] - copy[col]
        sample = copy.reset_index()[['y', 'x', *range(1,13), 'ndvi_pre',  'dayofyear', 'ndvi_post']]
        
        # Save pre and post NDVI plots
        _dir = self.input_raster.split("/")[-1].split(".tif")[0]
        Path(f"{self.out_dir}/plots").mkdir(exist_ok=True, parents=True)
        
        fig, ax = plt.subplots(1,1,figsize=(10,4), dpi=200)
        sns.histplot(copy['ndvi_pre'], ax = ax)
        sns.histplot(copy['ndvi_post'], ax = ax)
        plt.title("NDVI: Pre (blue) and Post (orange)")
        plt.tight_layout()
        ax.set(xlabel='NDVI', ylabel='Density')
        plt.savefig(f'{self.out_dir}/plots/ndvi.png')
        
        # Save pre and post raster plots  
        self.save_images()

        # Save to ZARR
        if sample_size < 1:
            if os.path.exists(f'{self.out_dir}/full.zarr'):
                z = zarr.open(f'{self.out_dir}/full.zarr', mode='a')
                z.append(full.to_numpy())
            else:
                zarr.save(f'{self.out_dir}/full.zarr', full.to_numpy()) 

        if os.path.exists(f'{self.out_dir}/{sample_filename}.zarr'):
            z = zarr.open(f'{self.out_dir}/{sample_filename}.zarr', mode='a')
            z.append(sample.to_numpy())
        else:
            zarr.save(f'{self.out_dir}/{sample_filename}.zarr', sample.to_numpy()) 


    def _generate_df_from_raster(self):
        with rasterio.open(self.input_raster) as src:
            profile = src.profile                
            
        image = rxr.open_rasterio(self.input_raster)
        df = image.to_dataframe(name="value")
        df = df.reset_index()
        df.columns = ['band', 'y', 'x', 'spatial_ref', 'value']
        df = pd.pivot(df, index = ['y', 'x'], columns=['band'], values=['value']).reset_index()
        print(df.columns)
        cols = [*df.columns.get_level_values(0)[0:2], *df.columns.get_level_values(1)[2:]]
        df.columns = df.columns.to_flat_index()
        df.columns = cols
        
        
        df = df.set_index(['y', 'x'])
        df = self._add_ndvi(df, 8, 4, "ndvi_pre")
        df = self._add_ndvi(df, 20, 16, "ndvi_post")
        df = self._add_dates(df)
        
        return df, profile

    def _add_ndvi(self, df, b8, b4, label):
        df[label] = (df[b8] - df[b4]) / (df[b8] + df[b4]) 
        return df

    def _add_dates(self, df):
        child_gdf = gpd.read_file(f"{self.interim_dir}/child.gpkg")
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.reset_index().x, df.reset_index().y))
        gdf = gdf.set_crs("epsg:4326").sjoin(child_gdf)
        gdf = gdf.drop(['grid_id', 'geometry'], axis=1)
        gdf['dayofyear'] = pd.to_datetime(gdf['BSD']).dt.dayofyear
        gdf = gdf.drop('BSD', axis=1)
        gdf = gdf.drop(['index_right'], axis=1)
        return gdf

    def save_images(self):
        s = rasterio.open(self.input_raster)
        x_lb = (s.width//2) - (s.width//4)
        x_ub = (s.width//2) + (s.width//4)
        y_lb = (s.height//2) - (s.height//4)
        y_ub = (s.height//2) + (s.height//4)

        n_images = 5
        fig, ax = plt.subplots(2,n_images,figsize=(5*n_images,10), dpi=500)
        ax=ax.flatten()

        _dir = self.input_raster.split("/")[-1].split(".tif")[0]
        locs = open(f"{self.out_dir}/locs.txt", "a")
        np.random.seed(seed=42)
        for i in range(0, n_images):
            with rasterio.open(self.input_raster) as src:
                random_x = np.random.randint(x_lb, x_ub)
                random_y = np.random.randint(y_lb, y_ub)
                
                locs.write(f"{random_x},{random_y}\n")

                window = Window(random_x, random_y, 100, 100)
                pre = src.read((4,3,2), window=window)
                post = src.read((16,15,14), window=window)

                show(pre, ax=ax[i], adjust=True)
                show(post, ax=ax[n_images+i],  adjust=True)

                    
        locs.close()   
        _dir = self.input_raster.split("/")[-1].split(".tif")[0]
        plt.savefig(f'{self.out_dir}/plots/prepost.png')

