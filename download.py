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
    parser.add_argument("--interim_dir", help="One of 'R' (raster) or 'Z' (zarr)")
    parser.add_argument("--crop_proba", help="Crop Probability for masking")
    args = parser.parse_args()

    # Inputs
    SHP = None

    # Parameters (exposed)
    YEAR = '2019'
    MASK = None
    OUT_DIR = "out"
    N_CORES = multiprocessing.cpu_count() - 2
    INTERIM_DIR = "../2308_interim"
    CROP_PROBA=60

    # Parameters (unexposed)
    _RESOLUTION_P = 2500
    _RESOLUTION_C = 250
    _POST_PERIOD_DAYS = [25, 40]

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

    # if args.format:
    #     FORMAT = args.format
    
    if args.n_cores:
        N_CORES = int(args.n_cores)
    
    if args.crop_proba:
        CROP_PROBA = int(args.crop_proba)

    if args.interim_dir:
        INTERIM_DIR = args.interim_dir

    # print(f"### Using {N_CORES} cores..")

    print(f"""

        Starting download step...
        
        Run parameters:

            SHP = {SHP}
            INTERIM_DIR = {INTERIM_DIR}
            OUT_DIR = {OUT_DIR}
            N_CORES = {N_CORES}
            YEAR = {YEAR}
            MASK = {MASK} 

    """)


    from utils.shapefile import ShapefileHelper
    from utils.bestdates2 import DatesHelper
    from utils.rasters import RasterGenerationHelper, MergeRasterSingleAoi, Masker, Sampler
    from utils.data import DataHelper

    start = time.time()

    def getBestDatesRaster(shp, interim_dir, out_dir=OUT_DIR, year=YEAR, n_cores=1, res_p=_RESOLUTION_P, res_c=_RESOLUTION_C, post_period_days=_POST_PERIOD_DAYS):
        

        if os.path.exists(f"{OUT_DIR}/COMPLETE"):

            prefix = shp.split("/")[-1].split(".gpkg")[0]
            if os.path.exists(f"{OUT_DIR}/{prefix}.tif"):
                print("Found pre-generated tif file in OUT folder")
                return
            elif os.path.exists(f"{INTERIM_DIR}/{prefix}.tif"):
                print("Found pre-generated tif file in INTERIM folder")

                src = f'{INTERIM_DIR}/{prefix}.tif'
                dest = f'{OUT_DIR}/{prefix}.tif'
                shutil.copy(src, dest)
                os.remove(src)
                print("Copied stuff from INTERIM to OUT")
                return
                # os.path.exists(f"{INTERIM}/{prefix}.tif")
            else: 
                print(f"Skipping tile generation for {shp} because COMPLETE")
                return
            
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
        were_dates_found = bd.extract_best_dates(grid_path = f'{interim_dir}/bdg.gpkg', mask_tif=MASK, crop_proba=CROP_PROBA)
        if were_dates_found:
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

            print("###############",MASK, type(MASK))
            # Mask if mask available
            if type(MASK) == 'None':
                print(f"#### Starting masking step for {shp}..")
                masker = Masker(
                    interim_dir, 
                    shp, 
                    f"{interim_dir}/{shp.split('/')[-1].split('.gpkg')[0]}.tif",
                    MASK
                )
                masker.mask(filename=shp.split('/')[-1].split('.gpkg')[0], gte=CROP_PROBA)
                print(f"#### Masking complete for {shp}.. | {time.time()-start} sec")      
            f = open(f"{out_dir}/COMPLETE", "w")
            f.write(f"Completed raster generation in {(time.time()-start)/60} minutes {(time.time()-start)%60} seconds")
            f.close()
        else:
            print(f"#### Process ended at best dates calculation. No crop land found for  CROP_PROBA = {CROP_PROBA}| {time.time()-start} sec")
            f = open(f"{interim_dir}/NOCROP", "a")
            f.write(f"Completed raster generation for {shp} in {(time.time()-start)/60} minutes {(time.time()-start)%60} seconds")
            f.close()
    
    
    def cleanup(interim_dir, out_dir):
        print(os.listdir(interim_dir))
        if 'NOCROP' in os.listdir(interim_dir):
            print(f"No crop data in: {out_dir}, deleting...")
            os.system(f"rm -rf {out_dir}")


    getBestDatesRaster(SHP, INTERIM_DIR, out_dir=OUT_DIR, n_cores=N_CORES)
    cleanup(interim_dir=INTERIM_DIR, out_dir=OUT_DIR)

