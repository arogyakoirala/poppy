import geopandas as gpd
import pandas as pd
import multiprocessing as mp
import numpy as np
import eeconvert as eeconvert
import ee
from datetime import datetime, timedelta
import time
import gc


ee.Initialize()

class BestDatesHelper:
    def __init__(self, grid_shapefile_path, n_cores=1, year=2019):
        self.path = grid_shapefile_path
        self.grid = gpd.read_file(self.path)
        print(f"Starting process for {len(self.grid.index)} tiles")
        self.n_cores = n_cores
        self.year = year
        self.dates = self._get_just_dates()
        
        
    
        
    def _get_just_dates(self):
        dates=[datetime(self.year, 1, 1) + timedelta(i - 1) for i in range(1, 170, 16)]
        date_range=[(x, y) for x, y in zip(dates[:-1], [date-timedelta(1) for date in dates[1:]])]
        just_dates = []
        for start, end in date_range:
            stad=start.date().strftime('%Y-%m-%d')
            endd=end.date().strftime('%Y-%m-%d')
            stadendd = (stad, endd)
            just_dates.append(stadendd)
        return just_dates
    
        
    def add_dates(self):            
        cpus = self.n_cores
        self.total = 0
#         cpus = 6
        grid_chunks = np.array_split(self.grid, cpus)
        pool = mp.Pool(processes=cpus)
        chunk_processes = [pool.apply_async(self._add_dates_for_chunk, args=(chunk, self.grid)) for chunk in grid_chunks]
        chunk_results = [chunk.get() for chunk in chunk_processes]
        final = gpd.GeoDataFrame(data=None, columns=self.grid.columns, index=self.grid.index)
        final = final.iloc[0:0]
        for chunk in chunk_results:
            final = final.append(chunk)
        final.to_file(self.path, driver="GPKG")
        return final

    
    
    def _get_all_dates(self, collection):
        def iter_func(image, newlist):
            date = ee.Number.parse(image.date().format("YYYYMMdd"));
            newlist = ee.List(newlist);
            return ee.List(newlist.add(date).sort())
        ymd = collection.iterate(iter_func, ee.List([]))
        return list(ee.List(ymd).reduce(ee.Reducer.frequencyHistogram()).getInfo().keys())
        
    def _add_dates_for_chunk(self, gdf_chunk, gdf_complete):
        chunk_copy = gpd.GeoDataFrame(data=None, columns=gdf_complete.columns, index=gdf_complete.index)
        chunk_copy = chunk_copy.iloc[0:0]
        for i, row in gdf_chunk.iterrows():
            start = time.time()            
            x,y = row.geometry.exterior.coords.xy
            cords = np.dstack((x,y)).tolist()
            g=ee.Geometry.Polygon(cords)
            feature = ee.Feature(g)
    
            mod_dataset=ee.ImageCollection('MODIS/061/MOD13Q1').filter(ee.Filter.date(self.dates[0][0], self.dates[-1][1])).filter(ee.Filter.bounds(feature.geometry()))
            ndvi = mod_dataset.select(['NDVI']);
            ndvimax = ndvi.max();
            all_dates = self._get_all_dates(mod_dataset)
    
            all_ndvis = ndvi.toArray();
            max_ndvi = all_ndvis.arrayArgmax();
            max_ndvi_tile_image = ee.Image(max_ndvi).arrayProject([0]).arrayFlatten([['maxDate_start', 'band2']]);    
            df = eeconvert.fcToGdf(max_ndvi_tile_image.sample(region=g, factor=1,geometries=True, scale=250)).loc[0]
            date_parsed = all_dates[df['maxDate_start']]
            date_parsed = date_parsed[0:4] + "-" + date_parsed[4:6] + "-" + date_parsed[6:8]
            row['BSD'] = date_parsed
            chunk_copy = chunk_copy.append(row)
            self.total = self.total + 1
            print(f"t={(time.time() - start)} | total = {self.total} | i={i} | {all_dates[df['maxDate_start']]}")
            
            x = None
            y = None
            g = None
            feature = None
            ndvi= None
            ndvimax=None
            all_dates=None
            all_ndvis = None
            max_ndvi=None
            max_ndvi_tile_image=None
            df = None
            gc.collect(generation=2)
            
            
        return chunk_copy
