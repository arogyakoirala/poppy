import geopandas as gpd
from pathlib import Path
import shutil
import argparse




def get_corresponding_tiles(shapefile_path, grid_folder_path, out_dir):
    shp = gpd.read_file(shapefile_path)
    grid = gpd.read_file(f'{grid_folder_path}/grid.gpkg')

    joined = gpd.sjoin(grid, shp)
    overlapping_tiles = joined['grid_id'].to_list()
    overlapping_tiles = [f'{f}.gpkg' for f in overlapping_tiles]
    print(overlapping_tiles)

    Path(out_dir).mkdir(exist_ok=False, parents=True)
    for tile in overlapping_tiles:
        source = f"{grid_folder_path}/{tile}"
        destination = f"{out_dir}/{tile}"
        shutil.copy(source, destination)


    

    joined.to_file("join.gpkg", driver="GPKG")


get_corresponding_tiles("../data/poppydata/inputs/aoi.gpkg", "../data/poppydata/afghanistan_tiles_10km", "out")