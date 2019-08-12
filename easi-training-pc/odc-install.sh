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
    python -m pip install -e .
    # Install remote debugging for Visual Studio Code
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
