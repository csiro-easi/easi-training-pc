# Standalone Docker for CSIRO DC Training environment
# Python 3.6 development environment

## Installation



## Usage
TODO Write usage instructions


## Basic architecture

This environment comprises 2 containers:
- postgres DB with a local persistent docker volume (cdclte-postgres-data)
- opendatacube with jupyter notebook dev container with docker bind volumes to host directories containing datacube-core and training notebooks (git submodules linked to respective repos)

These containers are linked by a docker bridged network, whereby they can see each other under their respective service names.
