FROM 444488357543.dkr.ecr.ap-southeast-2.amazonaws.com/easi-jupyter-singleserver:latest
# For AWS ECR access to easi-jupyter-singleserver obtain the login credentials using this (required valid AWS credentials)
#  $ aws ecr get-login --no-include-email --region ap-southeast-2
#  $ docker build . -t csiroeasi/easi-training-pc:develop
#  $ docker run --rm -it csiroeasi/easi-training-pc:develop /bin/bash
#  $ docker push csiroeasi/easi-training-pc:develop 

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
RUN pip3 install ptvsd    
USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir $HOME/odc && \
    /bin/bash fix-permissions $HOME

WORKDIR $HOME/work
# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

