# ElasTest Toolbox

This repository contains the needed tools to install and execute ElasTest Platform. At the moment, the only way to start the ElasTest Platform is in a single machine with Docker installed. In the near future, ElasTest Platform could be installed and executed in a cluster of machines or in a cloud provider (public or private).

## ElasTest execution modes

ElasTest can be executed in two modes:
* **normal**: In that mode, ElasTest is executed with all core components: EDM, EPM, EMP, ESM, EIM and ETM. In this mode, ElasTest can take long time to start and consume a considerable amount of resources.
* **lite**: This mode is designed to be a bit lighter than `normal` mode. It only starts ETM, EIM, ESM and the MySQL and ElasticSearch services of EDM. 

All other ElasTest components are executed on demand when ElasTest is running.

## System Requirements

To start ElasTest the only needed dependency is to have Docker installed. No additional configuration is necessary. 

ElasTest can be executed in Linux, Windows (with Docker Toolbox or Docker for Windows) and Mac (with Docker Toolbox or Docker for Mac).

## How to start ElasTest

ElasTest is executed in `normal` mode with the following command:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start
```

To execute ElasTest in `lite` mode the command is: 
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
```

## How to stop ElasTest

To stop ElasTest Platform you can execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
```

## Wait for ElasTest is started and running

Once ElasTest Platform start command is launched, you can run the following command to wait for ElasTest is started and running.
This command waits for about ten minutes max for Elastest to start and run; while prints ElasTest status information.
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform wait
```

## How to inspect ElasTest Platform

Once ElasTest Platform is started, you can run the inspect command to know more information:
With --api argument you can get the ElasTest API URL once ElasTest is running.
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform inspect --api
```

## Execution options

If you execute the following command you can see the options that can be used:

```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform -h
```

The output is:

```
usage: docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform [-h] {start,inspect,stop,wait}

positional arguments:
  {start,inspect,stop,wait}
                        Instruction to execute

optional arguments:
  -h, --help            show this help message and exit

```

In addition, you can execute the following commands to see the help of the instructions:

### Start

```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start -h
```

The output is:

```
usage: docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start [-h] [--lite] [--dev DEV] [--pullall] [--pullcore] [--noports]
               [--logs] [--server-address SERVER_ADDRESS]
               {start,stop}

positional arguments:
  {start,stop}          Mode to execute: start or stop

optional arguments:
  -h, --help            show this help message and exit
  --lite, -lt           Run in Lite mode
  --dev DEV, -d DEV     ETM dev mode. Usage: --dev=etm
  --pullall, -pa        Force pull of all images. Usage: --pullall
  --pullcore, -pc       Force pull of only necessary images. Usage: --pullcore
  --noports, -np        Unbind all ports. Usage: --noports
  --logs, -l            Show logs of all containers. Usage: --logs
  --server-address SERVER_ADDRESS, -sa SERVER_ADDRESS
                        Set server address Env Var. Usage: --server-
                        address=XXXXXX
```

### Inspect

```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform inspect -h
```

The output is:

```
usage: docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform inspect [-h] [--api]

optional arguments:
  -h, --help  show this help message and exit
  --api, -a   Return current status of ElasTest API
```

## Development instructions

ElasTest consists of multiple components. Every component has their own GitHub repository. In this repository (ElasTest Toolbox) is implemented the ElasTest Platform container, the docker container that starts the whole platform. 

The ElasTest Platform container is basically a container with the following elements:
* **Docker-compose tool:** To execute the docker-comopose.yml files of the core components.
* **Python runtime:** To execute python scripts.
* **Python scripts:** The python scripts that process the command options and manage the docker-compose files to be executed.

### Development system requirements

To create the ElasTest Platform container the following development tools are needed:
* **git:** To manipulate the git repository
* **docker-compose:** To execute the docker-compose.yml files of the components. 
* **python runtime:** To execute python scripts.

### How to develop the container

Clone elastest-toolbox repository and move into:
```
git clone --recursive https://github.com/elastest/elastest-toolbox
```
```
cd elastest-toolbox/scripts
```
To start ElasTest platform in `normal` mode with the `main.py` script execute:

```
python main.py start
```

To stop platform execute:
```
python main.py stop normal
```

To start ElasTest platform in `lite` mode with the `main.py` script execute:

```
python main.py start --lite
```
To stop platform execute:
```
python main.py stop --lite
```

## Ports
* **37006** ElasTest GUI
* **9200** Elasticsearch API

