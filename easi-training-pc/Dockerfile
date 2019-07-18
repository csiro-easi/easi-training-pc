FROM 444488357543.dkr.ecr.ap-southeast-2.amazonaws.com/easi-jupyter-singleserver:latest

LABEL maintainer="CSIRO EASI Data Cube Training on PC <Robert.Woodcock@csiro.au>"

USER root

# Install additional tools for training PC
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Core requirements
    sudo \
    cifs-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir $HOME/odc && \
    /bin/bash fix-permissions $HOME

# ODC is install but on training PC the option exists to do dataucbe-core deveopment using a user development install
# this script will install that component
COPY odc-install.sh /usr/local/bin/start-notebook.d/

WORKDIR $HOME/work

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

