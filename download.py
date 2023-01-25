if __name__ == '__main__':
    import argparse
    from pathlib import Path
    import os, shutil
    import multiprocessing
    import time
    import numpy as np
    import rasterio

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", help="Year")
    parser.add_argument("--mask", help="Mask Raster path")

    parser.add_argument("--shp", help="Shapefile path")
    parser.add_argument("--out_dir", help="Directory to store outputs")
    parser.add_argument("--n_cores", help="Number of cores")
    parser.add_argument("--format", help="One of 'R' (raster) or 'Z' (zarr)")
    parser.add_argument("--interim_dir", help="One of 'R' (raster) or 'Z' (zarr)")
    args = parser.parse_args()

    # Inputs
    SHP = None
    SHP_DIR = None

    # Parameters (exposed)
    YEAR = '2019'
    MASK = None
    OUT_DIR = "out_dl"
    FORMAT = 'R'
    N_CORES = multiprocessing.cpu_count() - 2
    INTERIM_DIR = "interim_dl"

    # Parameters (unexposed)
    _RESOLUTION_P = 2500
    _RESOLUTION_C = 250
    _POST_PERIOD_DAYS = [30, 45]

    # Parameters (derived)
    _TILE_OUTPUT_DIR = f'{INTERIM_DIR}/tiles'
    _PATH_TO_PARENT_GRID = f"{INTERIM_DIR}/parent.gpkg"
    _PATH_TO_CHILD_GRID = f"{INTERIM_DIR}/child.gpkg"


    if args.shp:
        SHP = args.shp

    if args.year:
        YEAR = args.year

    if args.mask:
        MASK = args.mask

    if args.out_dir:
        OUT_DIR = args.out_dir

    if args.format:
        FORMAT = args.format

    
    if args.n_cores:
        N_CORES = int(args.n_cores)

    if args.interim_dir:
        INTERIM_DIR = args.interim_dir

    # print(f"### Using {N_CORES} cores..")


    from utils.shapefile import ShapefileHelper
    from utils.bestdates2 import DatesHelper
    from utils.rasters import RasterGenerationHelper, MergeRasterSingleAoi, Masker, Sampler
    from utils.data import DataHelper

    def getBestDatesRaster(shp, interim_dir, out_dir=OUT_DIR, year=YEAR, n_cores=1, res_p=_RESOLUTION_P, res_c=_RESOLUTION_C, post_period_days=_POST_PERIOD_DAYS):
        
        start = time.time()

        if os.path.exists(INTERIM_DIR):
            shutil.rmtree(INTERIM_DIR)
        Path(INTERIM_DIR).mkdir(exist_ok=True, parents=True)
        
        if os.path.exists(OUT_DIR):
            shutil.rmtree(OUT_DIR)
        Path(OUT_DIR).mkdir(exist_ok=True, parents=True)

        # Make grids
        print(f"#### Starting grid generation for {shp}..")
        sh = ShapefileHelper(shp, interim_dir)
        sh.make_grid(resolution=_RESOLUTION_P, name="parent", id_col="pgrid_id")
        sh.make_grid(resolution=_RESOLUTION_C, name="child")
        sh.make_grid(resolution=25000, name="bdg", id_col="pgrid_id")
        print(f"#### Grids generated for {shp}.. | {time.time()-start} sec")

        # Get best dates
        print(f"#### Starting best date calculation for {shp}..")
        bd = DatesHelper(
            interim_dir, 
            shp, 
            [f'{year}-01-01', f'{year}-06-15'], 
            n_cores=n_cores, 
            bypass=False
        ) 
        bd.extract_best_dates(grid_path = f'{interim_dir}/bdg.gpkg')
        print(f"#### Best dates calculation completed for {shp}.. | {time.time()-start} sec")

        
        # Get tiles
        print(f"#### Starting raster download for {shp}..")
        Path(f'{interim_dir}/tiles').mkdir(parents=True, exist_ok=True)
        rgh = RasterGenerationHelper(
            f'{interim_dir}/parent.gpkg', 
            f'{interim_dir}/child.gpkg', 
            f'{interim_dir}/tiles', 
            n_cores, 
            clean = True, 
            post_period_days = post_period_days
        )
        rgh.get_rasters()
        print(f"#### Rasters downloaded for {shp}.. | {time.time()-start} sec")


        # Merge dates with tiles
        print(f"#### Starting merge step for {shp}..")
        mrs = MergeRasterSingleAoi(
            interim_dir, 
            shp, 
            f'{interim_dir}/tiles' 
        )
        mrs.merge(filename=shp.split('/')[-1].split('.gpkg')[0])
        print(f"#### Merge complete for {shp}.. | {time.time()-start} sec")


        # Mask if mask available
        if MASK is not None:
            print(f"#### Starting masking step for {shp}..")
            masker = Masker(
                interim_dir, 
                shp, 
                f"{interim_dir}/{shp.split('/')[-1].split('.gpkg')[0]}.tif",
                MASK
            )
            masker.mask(filename=shp.split('/')[-1].split('.gpkg')[0], gte=60)
            print(f"#### Masking complete for {shp}.. | {time.time()-start} sec")

        Path(f"{out_dir}/{shp.split('.gpkg')[0]}").mkdir(parents=True, exist_ok=True)
        os.system(f"cp -r {interim_dir}/tiles {out_dir}/{shp.split('/')[-1].split('.gpkg')[0]}_tiles")
        os.system(f"cp {interim_dir}/{shp.split('/')[-1].split('.gpkg')[0]}.tif {out_dir}/")


        sampler = Sampler(f"{out_dir}/{shp.split('/')[-1].split('.gpkg')[0]}.tif", interim_dir, out_dir)
        sampler.sample_zarr(1.0)        
        shutil.rmtree(interim_dir)

    getBestDatesRaster(SHP, INTERIM_DIR, out_dir=OUT_DIR, n_cores=N_CORES)
