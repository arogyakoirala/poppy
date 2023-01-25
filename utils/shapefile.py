import geopandas as gpd
from osgeo import ogr
from math import ceil
import shutil
import os
from shapely.geometry import box
from pathlib import Path

import warnings
warnings.filterwarnings("ignore")


# Shape file helper class
class ShapefileHelper():
    
    def __init__(self, dissolved_aoi_shapefile, vector_output_dir):
        self.raw = dissolved_aoi_shapefile
        self.vector_output_dir = vector_output_dir + "/"
        self._make_dir()
        self._read_file()
    
    def make_grid(self, resolution, name, out_crs="epsg:4326", id_col="grid_id", separate=False, prefix="", data_dir="../data/outputs"):
#         self.gdf.boundary.plot()
        
        gridWidth, gridHeight = resolution, resolution
        xmin, ymin, xmax, ymax = self.gdf.bounds.iloc[0]['minx'],  self.gdf.bounds.iloc[0]['miny'],  self.gdf.bounds.iloc[0]['maxx'],  self.gdf.bounds.iloc[0]['maxy']
        
        outputGridfn = name
        
        # get rows
        rows = ceil((ymax-ymin)/gridHeight)
        # get columns
        cols = ceil((xmax-xmin)/gridWidth)

        # start grid cell envelope
        ringXleftOrigin = xmin
        ringXrightOrigin = xmin + gridWidth
        ringYtopOrigin = ymax
        ringYbottomOrigin = ymax-gridHeight
        
        # create output file
        outDriver = ogr.GetDriverByName('ESRI Shapefile')
#         if os.path.exists(self.vector_output_dir + outputGridfn):
#             print("Deleting pre-existing shapefile: {}{}{}.shp".format(self.vector_output_dir,outputGridfn+"/", outputGridfn))
#             shutil.rmtree(self.vector_output_dir + outputGridfn,  ignore_errors=True)
            
#         if os.path.isdir(self.vector_output_dir):
#             print("Deleting pre-existing folder: {}{}/".format(self.vector_output_dir, outputGridfn))
#             shutil.rmtree(self.vector_output_dir + outputGridfn,  ignore_errors=True)
#         else:
#             os.makedirs(self.vector_output_dir)
#             print("Created new directory: {}{}/".format(self.vector_output_dir, outputGridfn))
            
            
        outDataSource = outDriver.CreateDataSource(self.vector_output_dir + outputGridfn + ".shp")
        outLayer = outDataSource.CreateLayer(outputGridfn,geom_type=ogr.wkbPolygon)
        featureDefn = outLayer.GetLayerDefn()
        
        print(f'--------- Generating grid at {resolution}mx{resolution}m ...')

        # create grid cells
        countcols = 0
        while countcols < cols:
            countcols += 1

            # reset envelope for rows
            ringYtop = ringYtopOrigin
            ringYbottom =ringYbottomOrigin
            countrows = 0

            while countrows < rows:
                countrows += 1
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(ringXleftOrigin, ringYtop)
                ring.AddPoint(ringXrightOrigin, ringYtop)
                ring.AddPoint(ringXrightOrigin, ringYbottom)
                ring.AddPoint(ringXleftOrigin, ringYbottom)
                ring.AddPoint(ringXleftOrigin, ringYtop)
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)

                # add new geom to layer
                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(poly)
                outLayer.CreateFeature(outFeature)
                outFeature.Destroy

                # new envelope for next poly
                ringYtop = ringYtop - gridHeight
                ringYbottom = ringYbottom - gridHeight

            # new envelope for next poly
            ringXleftOrigin = ringXleftOrigin + gridWidth
            ringXrightOrigin = ringXrightOrigin + gridWidth
        # Close DataSources
        outDataSource.Destroy()
        print('--------- Grid generation complete. Saving to disk...')        
        
        
#         # clip to boundary
        output = gpd.read_file(self.vector_output_dir + outputGridfn +".shp")
        # print(f"#################### Output Columns: {output.columns}")
        output = output.set_crs("epsg:32642").to_crs(out_crs).reset_index().rename(columns={"index": id_col}).drop('FID', axis=1)
        output = gpd.sjoin(output, self.gdf.to_crs("epsg:4326")).drop('index_right', axis=1)
        if 'grid_id_left' in output.columns:
            output['grid_id'] = output['grid_id_left']
            output = output.drop(['grid_id_left', 'grid_id_right'], axis=1)
        # print(f"#################### Output Columns: {output.columns}")
        self.output = output
        output = gpd.clip(output, self.gdf.to_crs("epsg:4326"))
        # print(output.columns)
        output = output.drop(id_col, axis=1).reset_index().drop('index', axis=1).reset_index().rename(columns={'index': id_col})
        if not separate:
            output.to_file(self.vector_output_dir + outputGridfn + ".gpkg", driver='GPKG')

        else:
            for i, tile in output.iterrows():
                d = {'geometry': tile['geometry']}
                # d[id_col] = tile[id_col]
                t = gpd.GeoDataFrame([d]).set_crs("epsg:4326")
                t.to_file(self.vector_output_dir + prefix+"_"+ str(tile[id_col]) + ".gpkg", driver='GPKG')
                Path(f"{data_dir}/dnq_outputs/{prefix}_{str(tile[id_col])}").mkdir(parents=True, exist_ok=True)
        print("--------- Successfully saved to disk: {}".format(self.vector_output_dir + outputGridfn+ ".gpkg"))
        self._clean_dir()
        return output

    def subset_grid(self, grid_path, aoi_path):
        aoi = gpd.read_file(aoi_path)
        grid = gpd.read_file(grid_path)
        
        subset = gpd.sjoin(grid, aoi).drop('index_right', axis=1)
        subset.to_file(grid_path, driver='GPKG')
        
    def _read_file(self):
        raw = gpd.read_file(self.raw)
#         geom = box(*raw.total_bounds)
#         gdf = gpd.GeoDataFrame([{"geometry": geom}])
#         gdf = gdf.set_crs("epsg:4326")
        self.gdf = raw.to_crs("epsg:32642")
    
    def _make_dir(self):
        Path(self.vector_output_dir).mkdir(parents=True, exist_ok=True)
    
    def _clean_dir(self):
        test = os.listdir(self.vector_output_dir)
        # print(test)

        for item in test:
            if item.endswith(".shp"):
                os.remove(os.path.join(self.vector_output_dir, item))
            if item.endswith(".shx"):
                os.remove(os.path.join(self.vector_output_dir, item))
            if item.endswith(".dbf"):
                os.remove(os.path.join(self.vector_output_dir, item))
        
