# Prepare your data folder

Create a folder called data in the project home directory.


```
mkdir data
```

Download and copy the following files in the `data` directory: [sample.gpkg](https://drive.google.com/file/d/1jhFYw5HF0avgVqRGQL-05dvq_aYGfZXQ/view?usp=share_link), [mask.tif](https://drive.google.com/file/d/1wJVfKi8ZV8WhVFoNTQ87YWFYrCfVzWgH/view?usp=sharing)


# Tiling shapefile

Working with rasters that have extremely large geospatial bounds requires a lot of memory, so for the first step, we are going to split the shapefile into smaller shapefiles of 5km by 5km. 

For doing this, we will use `tile.py`.

This takes in the following parameters:

- `shp`: Path to the shapefile that we want to tile
- `out_dir`: Where doe we want to store these tiled shapefiles?
- `resolution`: What resolution(in meters) do we want to generate the tiles in?

```
python tile.py data/sample.gpkg data/tiled --resolution 5000
```

This will create a new folder called `tiled` inside the `data` folder, containing 11 different shapefiles named 0.gpkg, 1.gpkg, ..., 11.gpkg


# Downloading imagery from GEE

We will now download Sentinel-2 imagery for Afghanistan corresponding for regions defined by the tiled shapefiles. For this we will use `download.sh`

This script takes in the following parameters.

- `year`: The year for which to download the shapefiles
- `mode`: Can be one of 'multi' (for parallelized downloading) or 'solo' if we are only working with one shapefile.
- `shp`: Path to directory containing shapefiles if mode='multi' (or) path to shapefile if mode='solo'.

    Since we are dealing with multiple shapefiles, we are going to use mode='multi'.
- `mask`: Path to mask.tif
- `out`: Path to where outputs will be stored
- `interim`: Path to interim directory (will store intermediate files)
- `cores`: The number of cores to use. Stick to 1 for now. In _fati_, we can use something like 20.
- `logs`: The directory where we want to store log files.


```
./download.sh year=2019 mode=multi shp=data/tiled mask=data/mask.tif out=data/rasters cores=1 logs=data/logs
```

# Accumulating missing tiles

This is important to ensure all tiles are downloaded. It simply checks the `data/rasters/out` folder to see if every "*.tif" is generated. If missing, it re-runs the download step one more time for the missing district.



