# Poppy Project

## Data preparation

Create a folder called inputs inside your project directory and download and extract the contents of [this zip file](link) into it.

```
chmod +x *.sh && ./ready.sh
```

This will populate the data directory with the following:

1. `model_aois`: Folder containing geopackaged shapefiles of candidate regions we would want to model with. Currently contains the folders `r1_r2`, `r1` and `r2`. `r1_r2` contains geopackaged shapefiles corresponding to two known poppy producing regions in Nad Ali and Qandahar respectively. `r1` contains a subset of this data (only Nad Ali) and `r2` contains the other subset (only Qandahar)
2. `districts.gpkg`: District level geopackaged shapefile of Afghanistan
3. `mask.tif`: Masking raster (Copernicus Global Landcover Dataset), from 2019, we will use this for all our data, and assume nothing has changed in subsequent years.
4. `poppy_1994-2020.csv`: Ground truth CSV from UNODC


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

## Download data for GEE.
We are now ready to download data for the tiled shapefiles in `inputs/districts_tiled` from Google Earth Engine. We will store this data in the `interim/rasters/modal2019` directory.

For this we will use `download.sh`

```
./download.sh year=2019 mode=multi shp=inputs/districts_tiled mask=inputs/mask.tif out=interim/rasters/modal2019 logs=interim/logs cores=2
```

Notes on `download.sh`: This script is capable of parallelly downloading rasters from GEE (specied through the `--cores` parameter) and takes in the following parameters.

- `year`: The year for which to download the imagery
- `mode`: Can be one of 'multi' (for parallelized downloading) or 'solo' if we are only working with one shapefile.
- `shp`: Path to directory containing shapefiles if mode='multi' (or) path to shapefile if mode='solo'.

Since we are dealing with multiple shapefiles, we are going to use mode='multi'.
- `mask`: Path to mask.tif
- `out`: Path to where outputs will be stored
- `interim`: Path to interim directory (will store intermediate files)
- `cores`: The number of cores to use. Stick to 1 for now. In _fati_, we can use something like 20.
- `logs`: The directory where we want to store log files


> **Note:** This process is going to take time. So it's better to run it in the background and store the logfile somewhere, using: 
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

## Prediction Step

Let's use the fitted model for making predictions for all shapefiles in `inputs/districts_tiled` folder. This will allow us to generate numbers at a district level.

```
python predict.py inputs/districts_tiled outputs/models/kmeans-3-nadali-qandahar interim/rasters outputs/predictions/nadali-qandahar
```

1. Prepare district level shapefiles.

We want district level shapefiles for making future predictions. 



2. Tile district level shapefiles.
3. Download imagery from GEE for region of analysis.
3. Ready shapefiles for modeling.
4. Fit model.
5. Ready shapefiles for which we want to make predictions.
6. Predict using candidate model.

<!-- # Poppy Project

This respository contains code that uses unsupervised learning techniques on Google Earth Imagery to predict poppy cultivation in Afghanistan. Using ground truth data from UNODC it then calculates correlations and SSEs between ground truth and predicted values.


### Clone this repository:
```
git clone https://github.com/arogyakoirala/poppy-latest.git
```
### Environment setup
This code requires certain libraries, and we need to make sure these are installed. This section describes how you can do that.


Step 0: Create a virtual environment (one-time only)
```
python -u venv poppy -r poppy-latest/requirements.txt
```

Step 1: Activate the virtual environment:

```
source poppy/bin/activate
cd poppy
```

IMPORTANT: All of the python code must be run from inside the `poppy-latest` folder. This is true for all examples shown from here on. I will assume that you're in the `poppy-latest` directory and skip all the cd statements going forward.


# One shot fit and predict step

The `fit_predict.sh` file allows:
* fitting a user specified unsupervised learning model (model=kmeans or model=gmm), 
* with the specified number of clusters or components (n=3) 
* on GEE data for an area corresponding to an input AOI shapefile (mode_in=solo) or multiple AOI shapefiles (mode_in=multi),
* and the uses the model to predict clusters for an area corresponding to an input AOI shapefile (mode_out=solo) or a directory containing multiple AOI shapefiles (mode_out=multi).

**Usage example**

```
./fit_predict.sh \
    model=kmeans \
    n=3 \
    mode_in=solo \
    shp_in=/data/tmp/arogya/inputs/2306.gpkg \ 
    mask=/data/tmp/arogya/inputs/mask.tif \
    year=2020 \
    cores=20 \
    out=../2308_2020 \
    shp_out=/data/tmp/arogya/inputs/grids_50km \
    mode_out=multi
```

Run in background:
```
nohup ./fit_predict.sh model=kmeans n=3 mode_in=solo shp_in=/data/tmp/arogya/inputs/2306.gpkg mask=/data/tmp/arogya/inputs/mask.tif year=2020 cores=20 out=/data/tmp/arogya/results/2308_2020 shp_out=/data/tmp/arogya/inputs/grids_50km mode_out=multi > logs/2308_2020.out &
```

<!-- ### Preprocessing Step
In this step, we download all the necessary data tpo perform the clustering exercise on.

```
./download.sh -p multi -s /path/to/gpkgs -m path/to/mask.tif -c 3
```

Sample code:
```
/download.sh -p multi -s ../poppydata/inputs/sample_tiles_small -m ../poppydata/inputs/mask.tif -c 3
```

Parameters:
- p: *process* can be 'multi' or 'solo'. If solo, the -s argument will expect a path to a single shapefile. If multi, the -s argument will expect a path to a folder containing multiple shapefiles.
- s: *shapefile path* the region (or regions) for which we want to perform the clustering exercise. If -p is multi, the -s argument will expect a path to a folder containing multiple shapefiles, else it will expect the path to a single shapefile. All shapefiles must be available in .gpkg format
- m: *mask file path* Specify a raster mask if possible 
- c: *cores* Number of cores.

Results of this step will be present in the "out" directory, and will contain, for each shapefile:
* A merged raster file with 24 bands
* A numpy file stored in the ZARR file format, which we will be using for the modeling step
* A plot of pre and post images (in PNG format)

### (Optional) Accumulate Step
In case of "multi" mode, we will need to carry out an additional step where we accumulate all the ZARR files into a single ZARR file for use in our modeling step.


```
python -u accumulate.py out    
```




By default the path/to/out/directory is "out"

### Modeling step
In this step, we run the modeling exercise and store the model as a pickle object. We will need to tell the command which ZARR file to use for modeling.

```
python -u model.py /path/to/sample/zarr model n 
```

Sample code:
```
python -u model.py ./out/acc_sample.zarr kmeans 3 
```

Parameters:
- */path/to/sample/zarr*: Location of the sample ZARR file containing pixel level values.
- *model*: Type of model, one of 'kmeans' or 'gmm' 
- *n*: Number of clusters for kmeans or number of components for GMM.



 --> -->
