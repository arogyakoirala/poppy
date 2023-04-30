#!/bin/bash
conda activate poppy-linux

# process='solo'
# mask=""
# cores="1"
# out="out"
# # interim="../2308_interim"
# year="2019"

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done


# echo "shp = $shp"
# echo "out = $out"
# echo "cores = $cores"
# echo "mask = $mask"
# echo "year = $year"

# echo "interim = $interim"




out_dir=$out/out
interim_dir=$out/interim
mkdir -p $logs



if [[ $process == 'solo' ]]
then
        python -u download.py --shp $shp --mask $mask --out_dir $out_dir --n_cores $cores --year $year --interim_dir $interim_dir
else
    N=$cores
    # for ((i=0; i <= ${#shps[@]}-1; i++));
    for entry in `ls $shp`;
    do
        
        ((j=j%N)); ((j++==0)) && wait
        # Define $idir and $odir
        base=${entry##*/}
        base=${base%.*}
        idir="${interim_dir}/${base}"
        odir="${out_dir}/${base}"
        logfile="${logs}/download-${base}.txt"
        
        # Download
        echo Started process for $base.gpkg. Writing logfile to: $logfile
        python -u download.py --shp $shp/$base.gpkg --mask $mask --out_dir $odir --interim_dir $idir --n_cores 1  --year $year > $logfile &

    done

            
    # BUG: Unnecessary folders generated
    # FIX: Find name of root folder by splitting $shp by "/" 
    # and delete it from outdir/base
    for entry in `ls $shp`;
    do
        ((j=j%N)); ((j++==0)) && wait
        IFS='/' read -r -a array <<< "$shp"
        base=${entry##*/}
        base=${base%.*}
        root_folder="${array[0]}"
        odir="${out_dir}/${base}"
        delete_folder="${odir}"/"${root_folder}"
        rm -rf "$delete_folder"
    done

    # Move tiles and important files from interim to out
    for entry in `ls $shp`;
    do
        ((j=j%N)); ((j++==0)) && wait
        IFS='/' read -r -a array <<< "$shp"
        base=${entry##*/}
        base=${base%.*}
        source="${interim_dir}/${base}/tiles"
        dest="${out_dir}/${base}/"
        mkdir -p "$dest"
        cp -r "$source" "$dest"

        source="${interim_dir}/${base}/${base}.tif"
        dest="${out_dir}/${base}/"
        cp -r "$source" "$dest"

        source="${interim_dir}/${base}/${base}.tif"
        dest="${out_dir}/all"
        mkdir -p "$dest"
        cp -r "$source" "$dest"
    done

    for entry in `ls $shp`;
    do
        
        ((j=j%N)); ((j++==0)) && wait
        # Define $idir and $odir
        base=${entry##*/}
        base=${base%.*}
        idir="${interim_dir}/${base}"
        odir="${out_dir}/${base}"
        logfile="${logs}/download-${base}.txt"
        
        # Download
        echo STARTED RECHECK AND CLEAN for $base.gpkg. Writing logfile to: $logfile
        python download.py --shp $shp/$base.gpkg --mask $mask --out_dir $odir --interim_dir $idir --n_cores 1  --year $year > $logfile &

    done
fi

wait 

# rm -rf "$interim_dir"
# mv "$out_dir"/* "$out"
# rm -rf "$out_dir"
