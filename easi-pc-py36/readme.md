# Standalone Docker for CSIRO DC Training environment
# Python 3.6 development environment

## Installation
Clone the repository, noting the submodule(s).
```
git clone --recursive https://github.com/csiro-easi/easi-training-pc.git
```

If you have cloned it and the submodules didn't load
```
$ cd easi-training-pc/
$ git submodule update --init --recursive
```

Download and run the docker images
```
$ cd easi-training-pc/easi-pc-py36/
$ docker-compose up

real	6m35.203s
user	0m1.355s
sys	0m0.245s
```

Go to a browser and enter "`localhost:8888`". This should connect to the docker's jupyter notebooks. Jupyter password is "`secretpassword`".

Get the container name and connect to a bash shell inside the container
```
$ docker ps -a
$ docker exec -t -i [CONTAINER ID or NAME] /bin/bash
```


## Usage
TODO Write usage instructions

```
$ docker images
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
csiroeasi/easi-training-pc   latest              3117169adcdd        5 days ago          3.77GB
postgres                     alpine              daa3d8ceab8f        2 weeks ago         71.7MB
```

```
$ docker ps -a
CONTAINER ID        IMAGE                               COMMAND                  CREATED             STATUS                     PORTS               NAMES
e458777744b1        csiroeasi/easi-training-pc:latest   "/usr/local/bin/tini…"   3 minutes ago       Exited (1) 3 minutes ago                       easi-pc-py36_opendatacube_1_ac43351ac544
258fddc6eaba        postgres:alpine                     "docker-entrypoint.s…"   3 minutes ago       Up 3 minutes               5432/tcp            easi-pc-py36_postgres_1_f9d66f7ef79b
```

```
$ docker-compose down
Stopping easi-pc-py36_postgres_1_f9d66f7ef79b ... done
Removing easi-pc-py36_opendatacube_1_ac43351ac544 ... done
Removing easi-pc-py36_postgres_1_f9d66f7ef79b     ... done
Removing network easi-pc-py36_default
$ docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
```

```
$ time docker-compose up
Creating network "easi-pc-py36_default" with the default driver
Creating easi-pc-py36_postgres_1_63b38f66fe3a ... done
Creating easi-pc-py36_opendatacube_1_126caea7fcef ... done

real	0m2.099s
user	0m0.423s
sys	0m0.130s
```

If you need to build the docker image locally because something changed in the image build process then use `docker build`. Eventually you will have a local version. `docker-compose` will then use that image.
```
$ docker build -t [CONTAINER ID or NAME] .
 ```


## Guides

- Overview of Docker: https://docs.docker.com/engine/docker-overview/
- Docker cheat sheet: https://www.linode.com/docs/applications/containers/docker-commands-quick-reference-cheat-sheet/
- Docker-compose: https://www.linode.com/docs/applications/containers/how-to-use-docker-compose/
- Containers:
    - A container is a runnable instance of an image. You can create, start, stop, move, or delete a container. You can connect a container to one or more networks, attach storage to it, or even create a new image based on its current state.
    - A container is defined by its image as well as any configuration options you provide to it when you create or start it. When a container is removed, any changes to its state that are not stored in persistent storage disappear.

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