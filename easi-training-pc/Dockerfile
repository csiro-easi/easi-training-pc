FROM jupyter/scipy-notebook

LABEL maintainer="CSIRO EASI Data Cube Training on PC <Robert.Woodcock@csiro.au>"

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:nextgis/ppa && \
    apt-get update && \
    apt-get upgrade --yes

# Install core requirements for ODC development and jupyter notebooks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Core requirements
    libhdf4-dev \
    gdal-bin gdal-data libgdal-dev libgdal20 libudunits2-0 \
    libudunits2-dev \
    # Additional utilities useful for ODC dev
	postgresql-client \
	curl \
    wget \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
    ffmpeg \
    cifs-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-setuptools python3-dev python3-pip python3-wheel libdpkg-perl
    
USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir $HOME/odc && \
    /bin/bash fix-permissions $HOME && \
# Install psycopg2 as a special case, to quiet the warning message 
    python -m pip install --no-cache --no-binary :all: psycopg2 && \
# Install jupyter notebook and additional python packages for interactive odc use
    python -m pip install folium ffmpeg shapely scikit-image fiona
RUN conda install -c conda-forge gdal
RUN conda install -c conda-forge netcdf4
RUN conda install rasterio

COPY odc-install.sh /usr/local/bin/start-notebook.d/

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

