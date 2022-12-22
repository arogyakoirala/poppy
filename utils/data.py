import pickle
import pandas as pd
import numpy as np
import rasterio
import rioxarray as rxr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from pathlib import Path

class DataHelper:
    def __init__(self, data_dir, raw):
        self.data_dir = data_dir
        self.raw = pd.read_pickle(raw)
        
    def pre_only(self):
        return self.raw[[*range(1,13),'ndvi_pre', 'dayofyear']]
    
    def post_only(self):
        return self.raw[[*range(12,25),'ndvi_pre','ndvi_post', 'dayofyear']]
    
    def diff_bands(self):
        copy = self.raw.copy()
        for col in range(1,13):
            copy[col] = copy[col+12] - copy[col]
        return copy[[*range(1,13), 'ndvi_pre','dayofyear']]
    
    def diff_all(self):
        copy = self.raw.copy()
        for col in range(1,13):
            copy[col] = copy[col+12] - copy[col]
        copy['diff_ndvi'] = copy['ndvi_post'] - copy['ndvi_pre']
        return copy[[*range(1,13), 'ndvi_pre', 'diff_ndvi', 'dayofyear']]
    
    def ndvi_and_day(self):
        return self.raw[['ndvi_pre', 'dayofyear']]
    
    def save(self, df, label, filename=None):
        print(f"------ Saved {label}; Columns: {df.columns}")
        if filename != None:
            df.to_pickle(filename)
        else:
            df.to_pickle(f'{self.data_dir}/interim/data_{label}.tgz')
        
class ModelingHelper:
    def __init__(self, data_dir, raw, run_name):
        self.raw = pd.read_pickle(raw)
        self.data_dir = data_dir
        self.run_name = run_name
        with rasterio.open(f"{self.data_dir}/interim/temp.tif") as src:
            self.profile = src.profile
    
    def ready_data(self, data):
        dataset = data[data['ndvi_pre'] > 0.3]
        dataset = dataset.loc[~(dataset==0).all(axis=1)]
        dataset.columns = dataset.columns.astype('str')
        return dataset
        
    def fit(self, data, model_type, n, save=True, drop_ndvi=False):
        clean = self.ready_data(data)
        scaler = StandardScaler()
        scaler.fit(clean)
        normalised_data = scaler.transform(clean)
        
        if model_type=='kmeans':
            model = KMeans(n_clusters=n)
            model.fit(normalised_data)

        if model_type=='gmm':
            model = GaussianMixture(n, covariance_type='full', random_state=0)
            model.fit(normalised_data)
        
        self.model = model
        
        MODEL_DIR = f'{self.data_dir}/outputs/models/{self.run_name}'
        Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

        with open(f'{MODEL_DIR}/model.pickle', 'wb') as f:
            pickle.dump(model, f)
        
        with open(f'{MODEL_DIR}/scaler.pickle', 'wb') as f:
            pickle.dump(scaler, f)
            
        return model
    
    def load_model(self, path):
        with open(path, 'rb') as f:
            model = pickle.load(f)
    
        return model
    
    def load_scaler(self, path):
        with open(path, 'rb') as f:
            scaler = pickle.load(f)
    
        return scaler
    
    def predict(self, data, model, scaler):
        dataset = self.ready_data(data)
        cluster_assignments =  model.predict(scaler.transform(dataset))
        result = dataset.copy()
        result['clust'] = cluster_assignments
        result = result[['clust']]
        result = pd.merge(data.reset_index(), result.reset_index(), how="left").set_index(['y','x'])
        return result
        
    def save_raster(self, results, filename):
        crs = self.profile['crs']
        transform = self.profile['transform']
        
        clust_assignments = pd.DataFrame(results['clust'])
        clust_assignments = pd.melt(clust_assignments, value_vars=['clust'], value_name='value', ignore_index=False)   
        clust_assignments = clust_assignments.drop('variable', axis=1) 
        clust_assignments[np.isnan(clust_assignments['value'])] = -99
        clust_assignments = clust_assignments.reset_index().drop_duplicates(subset=['y', 'x']).set_index(['y', 'x']).to_xarray()
        clust_assignments.rio.to_raster(f"{filename}.tif")
        
        with rasterio.open(f"{filename}.tif", "r+") as src:
            src.crs = crs
            src.nodata=-99
            src.transform=transform
    
    def save_ndvi_plot(self, results, model_type, n, filename):
        fig, ax = plt.subplots(n, 1, dpi=70, figsize=(9,9))
        ax=ax.flatten()
            
        for i in range(0,n):
            data = results[results['clust']==i]['ndvi_pre']
            ax[i].hist(data, bins=100)
            ax[i].set_title(f"{model_type} with k={n}; cluster={i}")
        plt.tight_layout()
        plt.savefig(f"{filename}.png")
        plt.close('all')
        
    def get_poppy_pixels(self, dist_id, year):
        poppyPixels = pd.read_csv(self.data_dir + "/inputs/poppy_1994-2020.csv")
        poppyPixels = poppyPixels[poppyPixels['distid'] == dist_id]

        return poppyPixels[f'X{year}'].iloc[0] 

    def save_comparison_results(self, results, dist, year, filename):
        results = pd.DataFrame(results.groupby('clust').count()['ndvi_pre']).rename(columns={'ndvi_pre': 'pixels_from_clustering'})
        results['clustering_ha'] = results['pixels_from_clustering']/100
#         results['unodc_ha'] = self.get_poppy_pixels(dist, year)
        results.to_csv(f"{filename}.csv")
        print(f"--------- Comparison saved to {filename}.csv")
        
class PredictionHelper:
    def _init_():
        print("Init")
    def prep_raster():
        print("Prep raster")
    def load_models():
        print("Load raster")
    def predict():
        print("Predict")
    def save():
        print("Save")
                    