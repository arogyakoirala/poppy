# Poppy Project

This respository contains code that uses unsupervised learning techniques on Google Earth Imagery to predict poppy cultivation in Afghanistan. Using ground truth data from UNODC it then calculates correlations and SSEs between ground truth and predicted values.


### Clone this repository:
git clone https://github.com/arogyakoirala/poppy-latest.git

### Environment setup
This code requires certain libraries, and we need to make sure these are installed. This section describes how you can do that.


Step 0: Create a virtual environment (one-time only)
```
venv poppy -r poppy-latest/requirements.txt
```

Step 1: Activate the virtual environment:

```
source poppy/bin/activate
cd poppy-latest
```

IMPORTANT: All of the python code must be run from inside the `poppy-latest` folder. This is true for all examples shown from here on. I will assume that you're in the `poppy-latest` directory and skip all the cd statements going forward.


### Preprocessing Step
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




