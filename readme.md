# Poppy Project

This respository contains code that uses unsupervised learning techniques on Google Earth Imagery to predict poppy cultivation in Afghanistan. Using ground truth data from UNODC it then calculates correlations and SSEs between ground truth and predicted values.

# Tutorial

## Data preparation

Create a folder called `inputs` inside your project directory and download and extract the contents of [this zip file](https://www.dropbox.com/s/uhxwmudndulwb0l/poppy.zip?dl=0) into it.

Here's a script that does this automatically.

```
chmod +x *.sh && ./ready.sh
```

This will populate the `inputs` directory with the following:

1. `model_aois`: Folder containing geopackaged shapefiles of candidate regions we would want to model with. Currently contains the sub-folders `r1_r2`, `r1` and `r2`. The subfolder `r1_r2` contains geopackaged shapefiles corresponding to two known poppy producing regions in Nad Ali and Qandahar respectively. `r1` contains a subset of this data (only Nad Ali) and `r2` contains the other subset (only Qandahar)
2. `districts.gpkg`: District level geopackaged shapefile of Afghanistan
3. `mask.tif`: Masking raster (Copernicus Global Landcover Dataset), from 2019, we will use this for all our data, and assume nothing has changed in subsequent years.
4. `poppy_1994-2020.csv`: Ground truth CSV from UNODC. We will use this to compare results.


### Generate individual district level shapefiles using `split.py`

This will explode all the individual polygons in the `districts.gpkg` into their own corresponding shapefiles. We will have to specify the folder where we want to store this. Let's go ahead and store these in `inputs/districts_exploded`

```
python split.py inputs/districts.gpkg inputs/districts_exploded
```

### Tile exploded shapefiles into individual tiled shapefiles at specified resolution using `tile.py`

The next step is to tile individual geopackaged district level shapefiles into tiles of a specified resolution (in meters). We will stored tiled shapefiles in the `inputs/districts_tiled` folder.

> For this tutorial, we only want to focus on districts 2308 and 2416, corresponding to Nad Ali and Qandahar respectively. Let's specify this using the `--subset` optional parameter. Not using the `--subset` parameter will generate tiles for all shapefiles present in the `inputs/district_exploded` folder. The `--subset` parameter can take in the following three inputs for now: `nadali_qandahar` (districts 2308 and 2416), and `hfp` (high frequency poppy districts, i.e. districts 1606, 1607, 1608, 1905, 1906, 2105, 2106, 2111, 2302, 2303, 2304, 2306, 2307, 2308, 2311, 2312, 2407, 2416, 2601, 2605).  

> Similarly, we can also customise the resolution of the tiled shapefile using the optional `--resolution` parameter. For now we will use 10000 meters as our resolution. The default value is 50000 meters. 

```
python tile.py inputs/districts_exploded inputs/districts_tiled --subset nadali_qandahar --resolution 10000
```

## Download data from GEE
We are now ready to download data for the tiled shapefiles in `inputs/districts_tiled` from Google Earth Engine. We will store this data in the `interim/rasters/modal2019` directory.

For this we will use `download.sh`

```
./download.sh year=2019 mode=multi shp=inputs/districts_tiled mask=inputs/mask.tif out=interim/rasters/modal2019 logs=interim/logs cores=2
```

> **Note on `download.sh`**: This script is capable of parallelly downloading rasters from GEE (specied through the `--cores` parameter) and takes in the following parameters.

- `year`: The year for which to download the imagery
- `mode`: Can be one of 'multi' (for parallelized downloading) or 'solo' if we are only working with one shapefile.
- `shp`: Path to directory containing shapefiles if mode='multi' (or) path to shapefile if mode='solo'.

Since we are dealing with multiple shapefiles, we are going to use mode='multi'.
- `mask`: Path to mask.tif
- `out`: Path to where outputs will be stored
- `interim`: Path to interim directory (will store intermediate files)
- `cores`: The number of cores to use. Stick to 1 for now. In _fati_, we can use something like 20.
- `logs`: The directory where we want to store log files


> **Run in background:** This process is going to take time. So it's better to run it in the background and store the logfile somewhere, using: 
> ```
> nohup ./download.sh year=2019 mode=multi shp=data/tiled mask=data/mask.tif out=data/rasters cores=20 logs=data/logs > logs/download_log.log & 
> ```
> You can monitor the status of each individual tile by revieing logfiles present in the `interim/logs/` directory

## Fit model

Time to actually fit the clustering model using `fit.py`

We are going to fit the model on regions defined by shapefiles present in the `inputs/model_aois/` directory, which pertains to two specific regions within Nad Ali and Qandahar where we know poppy is being grown.

We also have to tell the script where the rasters are (that would be `interim/rasters`) and where we want the final model to be stored (let's set this to `outputs/model` directory). Finally let's give the model run a name using the optional `--name` parameter, by default this is set to `""`.

```
python fit.py inputs/model_aois data/rasters outputs/models --name nadali-qandahar
```

### Notes

You can safely ignore the following error for now

```
Traceback (most recent call last):
  File "/Users/arogyak/projects/poppy-dev/fit.py", line 309, in <module>
    save_samples()
  File "/Users/arogyak/projects/poppy-dev/fit.py", line 294, in save_samples
    post = src.read((16,15,14), window=window)
  File "rasterio/_io.pyx", line 496, in rasterio._io.DatasetReaderBase.read
IndexError: band index 16 out of range (not in (1, 2, 3, 4))
```

## Prediction

Let's use the fitted model for making predictions for all shapefiles in `inputs/districts_tiled` folder. This will allow us to generate numbers at a district level.

```
python predict.py inputs/districts_tiled outputs/models/kmeans-3-nadali-qandahar interim/rasters outputs/predictions/nadali-qandahar
```

