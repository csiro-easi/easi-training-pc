# CSIRO EASI training environment for PC (Win,Mac,Linux) 

# Table of Contents
1. [Quickly get up and running](#quickly-get-up-and-running)
2. [Using Jupyter Notebooks](#using-jupyter-notebooks)
3. [Debugging my own python with Visual Studio Code](#debugging-my-own-python-with-visual-studio-code)

# Quickly get up and running
## Prerequisites
* Install git - https://git-scm.com/downloads
* Install Docker - https://docs.docker.com/install/
* (Optional) - a python code editor. This is only needed if you intend on writing python code directly, not just use the jupyter notebooks. Several options exist though many folks use Visual Studio Code https://code.visualstudio.com/download

All commands listed here should be entered into a terminal. On Windows Powershell works just fine.

***Windows host notes:***
* __CRLF handling in GIT and Editor__ As described below many of the text files used by the Docker container are mounted from the Docker host. Since Windows uses CRLF line endings by default and Linux (running in the Containers) uses only LF it is important to ensure that GIT and your chosen editors use LF by default. You will need to determine how to do this in your editor (eg. Visual Studio Code shows the current LF ending in the lower right of the window and has a default you can change in its settings). In Git auto conversion can be disabled prior to cloning by adjusting the global config:
    ```
    $ git config --global core.autocrlf false
    ```

## Clone the repository, noting the submodule(s)
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
* down - will stop and REMOVE the container. This will delete any changes made to the ODC container (e.g. if you added python libraries in the container these will be removed).
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
The database that contains your index of data has a independent lifecycle. It is stored in a separate persistent volume:
```
$ docker volume ls
DRIVER              VOLUME NAME
local               easi-training-pc-postgres-data
```
This means you can change the postgres and odc containers as much as you like and delete them, and the database content will still persist. If you want to start again you can remove it using:
```
$ docker volume rm easi-training-pc-postgres-data
```

# Using Jupyter Notebooks
## Connect via your web browser to the jupyter notebooks
1. Go to a browser and enter "`localhost:8888`". This should connect to the docker's jupyter notebooks. Jupyter password is "`secretpassword`".
2. Navigate to the "`easi-pc-notebooks`" and open "`01 - PC Getting Started`" and work your way through initialising the database and indexing some sample data.
3. Other notebooks show how to ingest data and the ODC API

# Debugging my own python with Visual Studio Code
1. Put your python source in the hosts "`work`" directory
1. Configure Visual Studio Code by adding a Configuration with the following:
    ```
            {
                "name": "Attach ODC Container (Remote Debug)",
                "type": "python",
                "request": "attach",
                "localRoot": "${workspaceRoot}/work",
                "remoteRoot": "/home/jovyan/work",
                "port": 5678,
                "host": "localhost"
            },
    ```
1. Connect to a bash shell inside the container (you can use the Visual Studio Code build in terminal to do this, or the Docker extension you can just right click Attach Shell)
    ```
    $ docker exec -t -i easi-pc-py36_opendatacube_1 /bin/bash
    ```
    _Note: The container above will change if you have a container of the same name still around. You can list current containers and get the names using:_
    ```
    docker container ls
    ```
1. In the container bash shall use pip3 to install any additional packages you require (you will need to do this whenever your create a new container (using up/down). Using start/stop will preserve container between uses)
1. In the bash execute change to the "`~/work`" directory and execute "`yourCode.py`" with using ptvsd
    ```
    $ cd ~/work
    $ python3 -m ptvsd --host 0.0.0.0 --port 5678 --wait yourCode.py
    ```
    The code will block and wait for the debugger to attach.
1. In Visual Studio Code debugger set breakpoints in your code and then start debugging using the Attach ODC Container (Remote Debug) configuration you setup earlier




# Additional details
See [easi-pc-py36/readme.md](easi-pc-py36/readme.md) for detailed instructions.
