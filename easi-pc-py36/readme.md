# Standalone Docker for CSIRO DC Training environment

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

Download and run the docker images. 
```
$ cd easi-training-pc/easi-pc-py36/
$ docker-compose up -d

real	6m35.203s
user	0m1.355s
sys	0m0.245s
```

`docker-compose up -d` will download (or use previously downloaded) base images and create containers for each of postgres and datacube with notebooks. When the container for datacube is created it will run `start-notebook.sh`, which will download the python requirements for datacube. This may take some time.

List the containers names and IDs
```
$ docker ps -a
```

Follow the download and install progress. (Crtl-c to exit).
```
$ docker logs -f [CONTAINER ID or NAME]
```

Go to a browser and enter "`localhost:8888`". This should connect to the docker's jupyter notebooks. Jupyter password is "`secretpassword`".

Connect to a bash shell inside the container
```
$ docker exec -t -i [CONTAINER ID or NAME] /bin/bash
```


## Usage
List images, with their names and IDs
```
$ docker images
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
csiroeasi/easi-training-pc   latest              3117169adcdd        5 days ago          3.77GB
postgres                     alpine              daa3d8ceab8f        2 weeks ago         71.7MB
```

List containers, with their names and IDs
```
$ docker ps -a
CONTAINER ID        IMAGE                               COMMAND                  CREATED             STATUS                     PORTS               NAMES
e458777744b1        csiroeasi/easi-training-pc:latest   "/usr/local/bin/tini…"   3 minutes ago       Exited (1) 3 minutes ago                       easi-pc-py36_opendatacube_1_ac43351ac544
258fddc6eaba        postgres:alpine                     "docker-entrypoint.s…"   3 minutes ago       Up 3 minutes               5432/tcp            easi-pc-py36_postgres_1_f9d66f7ef79b
```

Create new or updated containers, using docker-compose.yaml
```
$ docker-compose up -d
Creating network "easi-pc-py36_default" with the default driver
Creating easi-pc-py36_postgres_1_63b38f66fe3a ... done
Creating easi-pc-py36_opendatacube_1_126caea7fcef ... done
```

Close and remove the containers, using docker-compose.yaml
```
$ docker-compose down
Stopping easi-pc-py36_postgres_1_f9d66f7ef79b ... done
Removing easi-pc-py36_opendatacube_1_ac43351ac544 ... done
Removing easi-pc-py36_postgres_1_f9d66f7ef79b     ... done
Removing network easi-pc-py36_default
$ docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
```

If you need to build the docker image locally because something changed in the image build process then use `docker build`. If there are errors then you will need to fix them. When it completes you will have your custom image, from which to create containers. Edit `docker-compose.yaml` to use the new image.
```
$ export DOCKER_BUILDKIT=1  # Smarter caching and output, for docker>=18.06
$ docker build -t NAME:TAG .
# Edit docker-compose.yaml to use the new image
$ docker-compose down
$ docker-compose up -d
 ```

Also worth checking and cleaning the volumes
```
$ docker volume ls
DRIVER              VOLUME NAME
local               d3742d97fc21b9d9ae31a0e45a43c0c3ae35c332a86438863ac04c7d8135413f
local               easi-training-pc-postgres-data
local               f7c06db474fb69c90d364f7f5b150c4085f75aa2194248aceeb74adf97a17e85
local               f2391ace277e83f5cb6994c4a711793896ac256106c200d24ff6f4635eede0f3
local               f96331cf43ed46e331f7ced0e8c2c368ac599bbf57a3f72913381e7a804a07f3

$ docker volume prune

$ docker volume ls
DRIVER              VOLUME NAME
local               easi-training-pc-postgres-data
```

To remove the database and start fresh, also remove the persistent volume
```
$ docker volume rm [volume]
```

To access the database from inside the datacube container
```
$ docker exec -it [CONTAINER ID or NAME] bash

jovyan@[ID]:/$ psql -h postgres -p 5432 -U odc
Password for user odc:
psql (10.6 (Ubuntu 10.6-0ubuntu0.18.04.1), server 11.1)
WARNING: psql major version 10, server major version 11.
         Some psql features might not work.
Type "help" for help.

odc=#
```

To expose your data cube database to applications outside of docker.
```
$ docker stop [CONTAINER ID or NAME]
$ docker rm [CONTAINER ID or NAME]

# Update docker-compose.yaml to ensure there is a key/value in the postgres section like,
    - ports:
        5432:5432

$ docker-compose up -d
Creating network "easi-pc-py36_default" with the default driver
Creating easi-pc-py36_postgres_1_83ff9eebd620 ... done
Creating easi-pc-py36_opendatacube_1_63043048f161 ... done

$ docker ps -a
CONTAINER ID        IMAGE                               COMMAND                  CREATED             STATUS              PORTS                    NAMES
36ce31051b72        csiroeasi/easi-training-pc:latest   "/usr/local/bin/tini…"   10 minutes ago      Up 10 minutes       0.0.0.0:8888->8888/tcp   easi-pc-py36_opendatacube_1_6c1be926266a
bcb9cc9e7996        postgres:alpine                     "docker-entrypoint.s…"   10 minutes ago      Up 10 minutes       0.0.0.0:5432->5432/tcp   easi-pc-py36_postgres_1_22c416f1bf2e

# Ensure that you do not have another another postgres server running that may also be listening on port 5432
# From outside docker

$ psql -h localhost -p 5432 -U odc
Password for user odc:
psql (10.5, server 11.1)
WARNING: psql major version 10, server major version 11.
         Some psql features might not work.
Type "help" for help.

odc=# \q
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
