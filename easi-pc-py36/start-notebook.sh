#!/bin/bash

# Drop out on any error
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

# Update path
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  export PATH=$HOME/.local/bin:$PATH
  echo PATH updated. $PATH
else
  echo PATH is fine. $PATH
fi

# Optionally install the Dashboard. Requires postgis
if [ "$1" == "with-dashboard" ]; then
    echo Invoking start-dashboard.sh
    /bin/bash /usr/local/bin/start-dashboard.sh
    shift  # pop "with-dashboard"
fi

# Start Jupyter Notebook
cd $HOME/work

/bin/bash /usr/local/bin/start.sh $HOME/.local/bin/jupyter notebook --NotebookApp.token='secretpassword' $*

