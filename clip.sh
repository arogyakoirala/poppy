#!/bin/bash

source poppy-env/bin/activate


python -u clip.py outputs/predictions/nadali-qandahar-r1-r2-2019-30day/predictions  outputs/clipped/2019-30day inputs/afgmask60.gpkg   
python -u clip.py outputs/predictions/nadali-qandahar-r1-r2-2020-30day/predictions  outputs/clipped/2020-30day inputs/afgmask60.gpkg   
python -u clip.py outputs/predictions/nadali-qandahar-r1-r2-2021-30day/predictions  outputs/clipped/2021-30day inputs/afgmask60.gpkg   
python -u clip.py outputs/predictions/nadali-qandahar-r1-r2-2019_2-30day/predictions  outputs/clipped/2019_2-30day inputs/afgmask60.gpkg   
