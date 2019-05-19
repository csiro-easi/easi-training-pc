#!/bin/bash
set -e
# Install ODC dev environment - only once
if [ ! $(pip3 freeze 2> /dev/null | grep datacube==) ]; then
    # Now use the setup.py file to identify dependencies
    cd $HOME/odc
    export CPLUS_INCLUDE_PATH=/usr/include/gdal
    export C_INCLUDE_PATH=/usr/include/gdal
    
    rm -rf $HOME/.cache/pip
    # Install ODC in develop mode with all dependencies
    # Source rebuild of rasterio to include HDF4 support
    python -m pip install --no-binary rasterio -e .
    # Install remote debugging for Visual Studio Code
    python -m pip install ptvsd
fi
# Update path
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  export PATH=$HOME/.local/bin:$PATH
  echo PATH updated. $PATH
else
  echo PATH is fine. $PATH
fi
# Start Jupyter Notebook
cd $HOME/work

#/usr/local/bin/start.sh ~/.local/bin/jupyter notebook --NotebookApp.token='secretpassword' $*
