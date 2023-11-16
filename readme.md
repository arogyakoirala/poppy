# Poppy Project

This respository contains code that uses unsupervised learning techniques on Google Earth Imagery to predict poppy cultivation in Afghanistan. Using ground truth data from UNODC it then calculates correlations and SSEs between ground truth and predicted values.

## Table of Contents
- [Project outputs](#project-outputs)
- [Installation](#installation)
- [Tutorial](#tutorial)
   * [1. Data preparation](#1-data-preparation)
      + [1.1 Generate individual district level shapefiles using `split.py`](#11-generate-individual-district-level-shapefiles-using-splitpy)
      + [1.2 Tile exploded shapefiles into individual tiled shapefiles at specified resolution using `tile.py`](#12-tile-exploded-shapefiles-into-individual-tiled-shapefiles-at-specified-resolution-using-tilepy)
   * [2. Download data from GEE](#2-download-data-from-gee)
   * [3. Fit model](#3-fit-model)
   * [4. Generate predictions using model](#4-generate-predictions-using-model)
- [Troubleshooting](#troubleshooting)


# Project outputs 

Raster files for estimated areas of poppy cultivation in have been uploaded as assets on Google Earth Engine:

1. [2019 Rasters](https://code.earthengine.google.com/?asset=projects/ee-xhtai/assets/6-2-23poppyRaster_2019)
2. [2020 Rasters](https://code.earthengine.google.com/?asset=projects/ee-xhtai/assets/6-2-23poppyRaster_2020)
3. [2021 Rasters](https://code.earthengine.google.com/?asset=projects/ee-xhtai/assets/6-2-23poppyRaster_2021)

GEE scripts for socioeconomic analysis can be found here:
1. [Healthcare accessiblity analysis](https://code.earthengine.google.com/6a1bee76116ef8bd0d38695461d8a209?noload=true)
2. [Education analysis](https://code.earthengine.google.com/d3abae4e8797f80c32d0ed9b7022f81f?noload=true)

# Installation

Follow these steps to setup your environment. 

1. Clone this repository: `git clone https://github.com/arogyakoirala/poppy.git`
2. Navigate to project directory: `cd poppy`
3. Create virtual environment: `python3 -m venv poppy-env`
4. Activate virtual environment: `source poppy-env/bin/activate`
5. Install requirements using pip: `pip install -r requirements.txt`


# Tutorial

## 1. Data preparation

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


### 1.1 Generate individual district level shapefiles using `split.py`

This will explode all the individual polygons in the `districts.gpkg` into their own corresponding shapefiles. We will have to specify the folder where we want to store this. Let's go ahead and store these in `inputs/districts_exploded`

```
python split.py inputs/districts.gpkg inputs/districts_exploded
```

#### Arguments for `split.py`

```
  positional arguments:
  shp         SHP  Path to district shapefile in GPKG format
  out_dir     Out  Directory where individual shapefiles for each polygon within the district shapefile are to be stored
  
  optional arguments:
  -h, --help  show this help message and exit
```

### 1.2 Tile exploded shapefiles into individual tiled shapefiles at specified resolution using `tile.py`

The next step is to tile individual geopackaged district level shapefiles into tiles of a specified resolution (in meters). We will stored tiled shapefiles in the `inputs/districts_tiled` folder.

> For this tutorial, we only want to focus on districts 2308 and 2416, corresponding to Nad Ali and Qandahar respectively. Let's specify this using the `--subset` optional parameter. Not using the `--subset` parameter will generate tiles for all shapefiles present in the `inputs/district_exploded` folder. The `--subset` parameter can take in the following three inputs for now: `nadali_qandahar` (districts 2308 and 2416), and `hfp` (high frequency poppy districts, i.e. districts 1606, 1607, 1608, 1905, 1906, 2105, 2106, 2111, 2302, 2303, 2304, 2306, 2307, 2308, 2311, 2312, 2407, 2416, 2601, 2605).  

> Similarly, we can also customise the resolution of the tiled shapefile using the optional `--resolution` parameter. For now we will use 10000 meters squared as our resolution. The default value is 50000 meters squared. 

```
python tile.py inputs/districts_exploded inputs/districts_tiled --subset nadali_qandahar --resolution 10000
```

#### Arguments for `tile.py`

```
positional arguments:
  shp                   SHP Path to folder containing candidate shapefiles for which to generate tiles
  out_dir               Out Directory where tiled shapefiles are to be stored

optional arguments:
  -h, --help            show this help message and exit
  --resolution RESOLUTION
                        Resolution (in meters squared; defaults to 50000
  --subset SUBSET       Subset Specify subset to be used 
```


## 2. Download data from GEE
We are now ready to download data for the tiled shapefiles in `inputs/districts_tiled` from Google Earth Engine. We will store this data in the `interim/rasters/modal2019` directory.

For this we will use `download.sh`

```
./download.sh year=2019 mode=multi shp=inputs/districts_tiled mask=inputs/mask.tif out=interim/rasters/modal2019 logs=interim/logs cores=2
```

#### Arguments for `download.sh`
This script is capable of parallelly downloading rasters from GEE (specied through the `--cores` parameter) and takes in the following arguments.

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
> nohup ./download.sh year=2019 mode=multi shp=inputs/districts_tiled mask=inputs/mask.tif out=interim/rasters/modal2019 logs=interim/logs cores=20 > logs/download_log.log & 
> ```
> You can monitor the status of each individual tile by revieing logfiles present in the `interim/logs/` directory

## 3. Fit model

Time to actually fit the clustering model using `fit.py`

We are going to fit the model on regions defined by shapefiles present in the `inputs/model_aois/r1_r2` directory, which pertains to two specific regions within Nad Ali and Qandahar where we know poppy is being grown.

We also have to tell the script where the rasters are (that would be `interim/rasters`) and where we want the final model to be stored (let's set this to `outputs/model` directory). Finally let's give the model run a name using the optional `--name` parameter, by default this is set to `""`.

```
python fit.py inputs/model_aois interim/rasters/modal2019 outputs/models --name nadali-qandahar
```

#### Arguments for `fit.py`

```
positional arguments:
  shp          Directory containing shapefiles for regions of interest from which to use data for model fitting
  rasters_dir  Directory where rasters have been downloaded from the download step 
  out_dir      Directory where the output model and its metrics will be stored

optional arguments:
  -h, --help   show this help message and exit
  --name  An optional name given to the model
```

#### Notes

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

## 4. Generate predictions using model

Let's use the fitted model for making predictions for all shapefiles in `inputs/districts_tiled` folder. This will allow us to generate numbers at a district level.

```
python predict.py inputs/districts_tiled outputs/models/kmeans-3-nadali-qandahar interim/rasters/modal2019 outputs/predictions/nadali-qandahar
```

#### Arguments for `predict.py`

```
positional arguments:
  shp          Directory containing shapefiles for which predictions are to be generated (note that rasters for these shapefiles must have been downloaded in the download step)
  model_dir    Directory where the model to be used for fitting data is stored
  rasters_dir  Directory where rasters have been downloaded from the download step 
  out_dir      Directory where model predictions will be stored

optional arguments:
  -h, --help   show this help message and exit
```

# Troubleshooting

## The library gdal fails to install
This was because the version specified in requirements.txt did not match the bindings of those found in ubuntu native gdal. This is fixed after we change the version info for gdal in requirements.txt to match the version we gent when running the following command.

```
gdal-config --version
```
