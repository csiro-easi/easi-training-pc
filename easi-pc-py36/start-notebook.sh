#!/bin/bash
set -e
# Install ODC dev environment - only once
if [ ! $(pip3 freeze 2> /dev/null | grep datacube==) ]; then
    # Now use the setup.py file to identify dependencies
    cd $HOME/odc
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal
        
    rm -rf $HOME/.cache/pip
    # Install ODC in develop mode
    pip3 install -e .
    pip3 install --requirement requirements-test.txt
    # # Fix an issue with the pandas pinned version in requirements-test.txt not being appropriate (ImportError: cannot import name 'AbstractMethodError').
    # # TODO: This should be fixed in datacube-core on the CSIRO branch or fork as will be determined in future.
    # Add missing python packages that are required for things like data inges
    pip3 install pandas geopandas
fi
# Start Jupyter Notebook
cd $HOME/work

/usr/local/bin/start.sh ~/.local/bin/jupyter notebook --NotebookApp.token='secretpassword' $*
