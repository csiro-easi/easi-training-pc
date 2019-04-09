## Basic architecture

This environment comprises 2 containers:
- postgres DB with a local persistent docker volume (cdclte-postgres-data)
- opendatacube with jupyter notebook dev container with docker bind volumes to host directories containing datacube-core and training notebooks (git submodules linked to respective repos)

These containers are linked by a docker bridged network, whereby they can see each other under their respective service names.

`docker-compose.yml`
- Top level Docker environment recipe
- Defines postgres and datacube images, ports, persistent volumes and local mounts

`Dockerfile`
- Defines a Ubuntu-based image with user/group, open data cube and dependencies
- Create "jovyan" user, with appropriate group and permissions
- Adds `99parallel`, `fix-permissions`
- Copy `start.sh`, `start-notebook.sh`, `start-singleuser.sh` into /usr/local/bin/
- Copy `jupyter_notebook_config.py` into /etc/jupyter/
- Launch `start-notebook.sh` by default (CMD) 

`99parallel`
- Apt config options

`fix-permissions`
- Make everything in the directory owned by the group $NB_GID and writable by that group

`start.sh`
- start a notebooks container, adapted from the Jupyter team

`start-notebook.sh`
- Install datacube-core
- If $JUPYTERHUB_API_TOKEN exec `/usr/local/bin/start-singleuser.sh`
- Else start Jupyter with `start.sh`

`start-singleuser.sh`
- Set notebook arguments
- Start Jupyter + arguments with `start.sh`
