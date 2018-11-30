#!/bin/bash

# Drop out on any error
set -e

# Install Dashboard deploy environment - only once
if [ ! $(pip3 freeze 2> /dev/null | grep dashboard) ]; then
    # Now use the setup.py file to identify dependencies
    cd $HOME/work/dea-dashboard
#    export CPLUS_INCLUDE_PATH=/usr/include/gdal
#    export C_INCLUDE_PATH=/usr/include/gdal

#    apt-get update && apt-get install -y \
#        python3-fiona python3-shapely \
#        && rm -rf /var/lib/apt/lists/*
        
    pip3 install gunicorn flask pyorbital colorama

    pip3 install -e .[deployment]

    # To be updated after the dashboard install
    pip3 install -U  cligj \
        && rm -rf $HOME/.cache/pip
fi

cd $HOME
if [ -d "product-summaries" ]; then
    rm -rf "product-summaries"
fi
mkdir "product-summaries"

cubedash-gen --all | tee -a $HOME/summary-gen.log

gunicorn -b '0.0.0.0:8998' -w 1 '--worker-class=egg:meinheld#gunicorn_worker'  --timeout 60 cubedash:app &
