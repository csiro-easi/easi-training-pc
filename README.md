# CSIRO EASI training environment for PC (Win,Mac,Linux) 

# Quickly get up and running

## Clone the repository, noting the submodule(s)
*Windows host notes:*
* __Do not use Docker Desktop 2.0.0.2__ (current release at 16/1/2018), please use Docker Desktop 2.0.0.0. There is a known issue that causes intermitment file not found errors in datacube.load() when it uses rasterio to read the host files.
* __CRLF handling in GIT and Editor__ As described below many of the text files used by the Docker container are mounted from the Docker host. Since Windows uses CRLF line endings by default and Linux (running in the Containers) uses only LF it is important to ensure that GIT and your chosen editors use LF by default. You will need to determine how to do this in your editor (eg. Visual Studio Code shows the current LF ending in the lower right of the window and has a default you can change in its settings). In Git auto conversion can be disabled prior to cloning by adjusting the global config:
    ```
    $ git config --global core.autocrlf false
    ```

To clone the repository and submodules:
```
git clone --recursive https://github.com/csiro-easi/easi-training-pc.git
```

If you have cloned it and the submodules didn't load
```
$ cd easi-training-pc/
$ git submodule update --init --recursive
```

## Download and run the docker images for the first time 
```
$ cd easi-training-pc/easi-pc-py36/
$ docker-compose up -d
```
## Connect via your web browser to the jupyter notebooks
1. Go to a browser and enter "`localhost:8888`". This should connect to the docker's jupyter notebooks. Jupyter password is "`secretpassword`".
2. Navigate to the "`easi-pc-notebooks`" and open "`01 - PC Getting Started`" and work your way through initialising the database and indexing some sample data.
3. Other notebooks show how to ingest data and the ODC API

## Connect to a bash shell inside the container
```
$ docker exec -t -i easi-pc-py36_opendatacube_1 /bin/bash
$ cd ~ # to get to the home directory
```
_Note: The container above will change if you have a container of the same name still around. You can list current containers and get the names using:_
```
docker container ls
```
## Files: Notebooks, data and your own python files
Changes that are user would make, be it python library installs, database index, etc can occur in two places:
1. On the host system
2. Inside the container(s)

All notebooks, data and python code are stored on the host system as paths relative to the git root ("`$ cd easi-training-pc`"). The list below shows the relative path on the host and the path that is mounted in the opendatacube container:
```
      - ../datacube-core:/home/jovyan/odc
      - ../../sample_data:/data
      - ../output:/home/jovyan/output
      - ../work:/home/jovyan/work
      - ./config/datacube.conf:/home/jovyan/.datacube.conf
      - ./config/datacube_integration.conf:/home/jovyan/.datacube_integration.conf
```
Placing a user related data, notebooks and files into any of the directories, or modifying files will immediately be reflected in the container. 


## To shutdown with and without removing the ODC and database containers
Docker has two ways to shutdown containers:
* down - will stop and REMOVE the container. This will delete the ODC database and any changes made to the ODC container (e.g. if you added python libraries in the container these will be removed).
* stop - will stop the containers but their state will remain. The ODC database and all changes will persist when next started.

The normal workflow is to use `up` to create the containers, start/stop to do your work, keeping any changes you make and down to remove the containers and start over.

Here's all the commands:
```
$ cd easi-training-pc/easi-pc-py36/
$ docker-compose up -d # creative
$ docker-compose stop 
$ docker-compose start
$ docker-compose down  # destructive
```

# Additional details
See [easi-pc-py36/readme.md](easi-pc-py36/readme.md) for detailed instructions.
