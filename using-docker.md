# Docker quick-help for CSIRO datacube training environment

1. [Introduction](#introduction)
2. [List images, with their names and IDs](#list-images-with-their-names-and-ids)
3. [List containers, with their names and IDs](#list-containers-with-their-names-and-ids)
4. [Connect to the database](#connect-to-the-database)
5. [Up, Down, Start and Stop](#up-down-start-and-stop)
6. [Volumes](#volumes)
7. [Connect into a container](#connect-into-a-container)
8. [Make changes and build your own images](#make-changes-and-build-your-own-images)
9. [Check container logs to check progress or track down any errors](#check-container-logs-to-check-progress-or-track-down-any-errors)
10. [Windows 10 environment](#windows-10-environment)
11. [Linux environments](#linux-environments)
12. [MacOS environments](#macos-environments)

## Introduction
Docker is a software environment that provides pre-built machine images and customisation of these images. Its role is to make it easy to package, share and deploy pre-configured images of an operating system plus the necessary software for a specific purpose.

http://www.docker.com

In many ways docker is akin to virtual machines (e.g., VirtualBox and VMWare) but offers a managed, repeatable and scalable way to create and share images that include an operating system plus pre-configured software.

Docker images are publicly shared through [Docker Hub](https://hub.docker.com). You can use this to search for many kinds of pre-built images to use.

For example, the [Open Data Cube partnership (ODC)](https://www.opendatacube.org) provides [docker images](https://hub.docker.com/u/opendatacube) for many of its [github repositories](https://github.com/opendatacube). The [CSIRO datacube training environment](https://hub.docker.com/r/csiroeasi/easi-training-pc) also provides a public docker image.

```Dockerfile``` and ```docker-compose.yml``` scripts allow us to build-on and adapt an existing docker image.

The CSIRO datacube training environment uses ```Dockerfile``` and ```docker-compose.yml``` scripts adapted from those provided by ODC and create a datacube environment suited to the "power-user" needs of CSIRO science teams.

## List images, with their names and IDs
```
$ docker images
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
csiroeasi/easi-training-pc   latest              af0f9050058d        3 weeks ago         1.59GB
postgres                     alpine              9ca7fdaec623        4 weeks ago         70.8MB
```

Remove or delete an image
```
$ docker image rm REPOSITORY[:TAG]
```
Remove all images
```
$ docker image rm $(docker images -a -q)
```

## List containers, with their names and IDs
```
$ docker ps -a
CONTAINER ID   IMAGE                               COMMAND                  CREATED          STATUS         PORTS                                            NAMES
11c215be8d9b   csiroeasi/easi-training-pc:latest   "/usr/local/bin/tini…"   10 seconds ago   Up 8 seconds   0.0.0.0:5678->5678/tcp, 0.0.0.0:8888->8888/tcp   easi-pc-py36_opendatacube_1
993c76da5286   postgres:alpine                     "docker-entrypoint.s…"   11 seconds ago   Up 9 seconds   0.0.0.0:5432->5432/tcp                           easi-pc-py36_postgres_1
```

Remove or delete a container
```
$ docker rm REPOSITORY[:TAG]
```
Remove all containers
```
$ docker rm $(docker ps -a -q)
```

The CSIRO datacube training containers open (map) a set of ports that allow connections into the containers from software outside of the containers:
* 5678 - enable debugging with Visual Studio Code
* 8888 - enable a browser to connect to the notebooks via http://localhost:8888
* 5432 - enable connections to the postgres server and the datacube database

## Connect to the database
The password is given in ```docker-compose.yml```
```
$ psql -h localhost -p 5432 -U odc
Password for user odc:
```

## Up, Down, Start and Stop
Up and Down are used with ```docker-compose``` to create and remove containers, respectively. The associated images will be created if they do not exist locally already.<br>
Start and Stop are used with ```docker``` to (re)start and pause containers. The container state is retained between start and stop cycles.<br>
The general workflow is:
```
$ docker-compose up -d                 # create containers; reads docker-compose.yml
$ docker exec -t -i [NAME] /bin/bash   # access a container
$ docker stop [NAME]                   # pause a container
$ docker start [NAME]                  # restart a container
$ docker-compose down                  # remove containers but retain images; reads docker-compose.yml
```

## Volumes
The datacube database is created in a persistent volume, which is persistent through Up, Down, Start, Stop cycles.
```
$ docker volume ls                # list volumes
DRIVER              VOLUME NAME
local               easi-training-pc-postgres-data
```

Remove or delete a volume
```
$ docker volume rm [VOLUME NAME]  # remove a volume
$ docker volume prune             # remove all orphaned volumes
```
Remove all volumes
```
$ docker volume rm $(docker volume ls -q)
```

## Connect into a container
The CSIRO datacube training containers will connect you in as user "root", which will let you mount network drives and install additional software
```
$ docker exec -t -i [NAME] /bin/bash

root@[hash]: exit  # logout of the container
```

## Make changes and build your own images
1. Edit ```DockerFile``` or the associated scripts
2. Create a new image with ```docker build```. You will need to fix any errors
3. Edit ```docker-compose.yml``` to use the new image. You will need to fix any errors
```
$ export DOCKER_BUILDKIT=1     # smarter caching and output, for docker>=18.06
$ docker build -t NAME:TAG .   # reads DockerFile; NAME:TAG can be anything you like
# Edit docker-compose.yml to use the NAME:TAG image
$ docker-compose up -d
```

## Check container logs to check progress or track down any errors
Often easiest to use in a separate shell with the ```-f|--follow``` option
```
$ docker logs -f [CONTAINER NAME]
```

## Windows 10 environment
There are a few combinations of software that you can use, depending on your preferences. Full details are not provided here. If you require trouble-shooting help then your first option is the internet as its quite likely someone has already tried what you are trying (much of what we know has been found this way). If you're still stuck then contact us and we will provide what guidance we can. 

#### Docker CE for Windows
Create an account and download the software from www.docker.com.
For most commands and operations you will need to use one of, for example, PowerShell or Command Prompt, Windows Subsystem for Linux, or Visual Studio Code (includes a shell).

Enable Hyper-V
1. Add or remove programs
2. Programs and features (right hand side)
3. Turn Windows features on or off
4. Scroll down to Hyper-V
5. Turn everything on

#### PowerShell or Command Prompt
The docker commands above should work as described.

#### Windows Subsystem for Linux
1. Get Ubuntu from the Microsoft Store
2. Follow https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly to connect to Docker CE for Windows.
   - Note that its necessary to make the change such that C: mounts to /c (not the default /mnt/c); otherwise ```docker-compose up -d``` will fail.
3. Mount other mapped drives. Mounts other than 'C:' will need to be reset at the start of each session.
   * (manual) At command line ```sudo mount -t drvfs  X:  /x```
   * (automatic) In ```/etc/fstab``` add a line like ```H: /h   drvfs   defaults 0 0```

#### Visual Studio Code
1. Get Python for Windows, from https://www.python.org
2. Get the Docker extension

The docker commands above should work as described.

## Linux environments
Ubuntu example given here only.
1. Follow https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly to connect to docker's apt repository

The docker commands above should work as described.

## MacOS environments
TBC.
