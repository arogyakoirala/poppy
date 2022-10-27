import pandas as pd
import geopandas as gpd
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
import numpy as np
from datetime import datetime
import os


import warnings
warnings.filterwarnings("ignore")

class BestDatesHelper():
    def __init__(self, in_csv, grid, vector_output_dir, out_shp, year, n_neighbors, diagnose=False):
        self._ready(in_csv, grid, year)
        self.out_shp = out_shp
        self.vector_output_dir = vector_output_dir + "/"
        self.diagnose = diagnose
        self.n_neighbors = n_neighbors
        self._make_dir()
        
        
    def _ready(self, csv, grid, year):
        print('------ Readying data..')
        dates = pd.read_csv(csv)
        dates_gdf = gpd.GeoDataFrame(dates,
                                      geometry=gpd.points_from_xy(
                                          dates.Longitude, 
                                          dates.Latitude)).set_crs("epsg:4326")
        self.dates_gdf = dates_gdf # comment in prod
        grid = gpd.read_file(grid).to_crs("epsg:4326")
        self.data = grid.sjoin(dates_gdf, how="left", predicate="intersects")
        
        columns = ['grid_id', 'Latitude', 'Longitude', 'geometry']
        columns.extend(self.data.filter(like=str(year), axis=1).columns.tolist())
        self.data = self.data[columns]
        self.data.columns = ['GRID_ID', 'LAT', 'LNG', 'geometry', 'BSD', 'BED', 'NDVI']
        
    def fill_empty_dates(self):
        copy = self.data.copy()
        copy = copy.to_crs("epsg:32642")
        copy['lat'], copy['lon'] = copy['geometry'].centroid.x, copy['geometry'].centroid.y
        
        
        grid_date_counts = copy.groupby(['GRID_ID']).count().reset_index()
        one_start_date_grid_ids = grid_date_counts[grid_date_counts['BSD'] == 1].reset_index()['GRID_ID'].to_frame()
        one_start_date = copy[copy['GRID_ID'].isin(list(one_start_date_grid_ids['GRID_ID'].values))]
        
        print("------ {} entries with one start date..".format(len(one_start_date)))
        
        not_one_start_date_grid_ids = grid_date_counts[grid_date_counts['BSD'] != 1].reset_index()['GRID_ID'].to_frame()
        not_one_start_date = copy[copy['GRID_ID'].isin(list(not_one_start_date_grid_ids['GRID_ID'].values))]
        not_one_start_date = not_one_start_date[['GRID_ID', 'geometry', 'lat', 'lon']].drop_duplicates()
        
        print("------ {} entries with two or zero start dates..".format(len(not_one_start_date)))
        
        self._fit_predict_knn(one_start_date, not_one_start_date)
        
        
        
    def _fit_predict_knn(self, one_start_date, not_one_start_date):
        print(f'------ Filling missing dates using K-Nearest Neighbour Algorithm at k={self.n_neighbors}')
        self.X, self.y = one_start_date[['GRID_ID', 'lat', 'lon']].set_index('GRID_ID'), one_start_date[['GRID_ID','BSD', 'BED']].set_index('GRID_ID')
        model = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        
        
        model.fit(self.X, self.y)
        print("------ Model fitting complete..")
        
        self.model = model
        if self.diagnose:
            print("------ Performing model diagnostics..")            
            self._diagnose()
        
        dates = pd.DataFrame(model.predict(not_one_start_date[['lat', 'lon']]), columns=['BSD', 'BED'])
        not_one_start_date_rc = pd.concat([not_one_start_date.reset_index(drop=True), dates], axis=1)
        one_start_date_rc = one_start_date[['GRID_ID', 'BSD', 'BED', 'geometry', 'lat', 'lon']]
        
        all_grids = pd.concat([not_one_start_date_rc, one_start_date_rc], axis=0)
        all_grids = all_grids.to_crs("epsg:4326")
        self.data = all_grids


#         print("Saving generated shapefile to disk..")
#         if os.path.isdir(self.vector_output_dir + self.out_shp):
#             directory = self.vector_output_dir + self.out_shp
#             for f in os.listdir(directory):
#                 os.remove(os.path.join(directory, f))
#         else:
#             os.makedirs(self.vector_output_dir + self.out_shp)
#             print("Created new directory: {}{}/".format(self.vector_output_dir, self.out_shp))

        self.data.to_file(self.vector_output_dir + self.out_shp + ".gpkg", driver='GPKG')
        print("------ Successfully saved to disk: {}".format(self.vector_output_dir + self.out_shp + ".gpkg"))

            
        
    def _diagnose(self):        
        kf = KFold(n_splits=10)
        accuracy_scores_bsd = []
        accuracy_scores_bed = []
        iteration = 0
                
        print('------ Diagnosis: Perfoming 10 fold cross validation')
        for train_index, test_index in kf.split(self.X):
            X_train, X_test = self.X.iloc[train_index], self.X.iloc[test_index]
            y_train, y_test = self.y.iloc[train_index], self.y.iloc[test_index]
            
            
            accuracy_score_bsd = accuracy_score(y_test['BSD'], self.model.predict(X_test)[:,0])
            accuracy_score_bed = accuracy_score(y_test['BED'], self.model.predict(X_test)[:,1])

            # Check to ensure that timedelta between predicted BED and BSD is always 15
            # test_diff = pd.DataFrame(self.model.predict(X_test), columns =["BSD", "BED"])
            # print((test_diff.apply(lambda d: datetime.strptime(d['BED'], '%Y-%m-%d'), axis=1) - test_diff.apply(lambda d: datetime.strptime(d['BSD'], '%Y-%m-%d'), axis=1)).dt.days.value_counts())
        
            iteration += 1
            print("--------- Accuracy at iteration {}: {}".format(iteration, accuracy_score_bsd))
            accuracy_scores_bsd.append(accuracy_score_bsd)
            accuracy_scores_bed.append(accuracy_score_bsd)
            

        print("------ Mean accuracy at k=8 is : {}".format(np.mean(accuracy_scores_bsd)))
    
    def _make_dir(self):
        Path(self.vector_output_dir).mkdir(parents=True, exist_ok=True)
    
        
