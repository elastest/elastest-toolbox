# ElasTest Toolbox

This repository contains the needed tools to install and execute ElasTest Platform. At the moment, the only way to start the ElasTest Platform is in a single machine with Docker installed. In the near future, ElasTest Platform could be installed and executed in a cluster of machines or in a cloud provider (public or private).

## System Requirements

To install and execute ElasTest you can use any mayor operating systema (linux, windows or mac) with Docker installed. No additional configuration is necessary.

To install Docker CE (Community Edition), please follow the [official installation instructions](https://docs.docker.com/engine/installation/).

## ElasTest execution modes

ElasTest can be executed in two modes:
* **full**: ElasTest is executed with all components. It is ideal to execute in a server with high computing resources. It can take several minutes to start all services included.
* **lite**: This mode is designed to be lighter than `full` mode. It executes a basic persistence (no redundancy) and doesn't execute the monitoring platform. It is ideal to execute ElasTest in the development laptop as it consume less resources and starts in less time.

Test Support Services and Engines are started on demand by the user when needed to improve startup time and save some resources if that components are not used.

## How to start ElasTest

ElasTest is executed in `full` mode with the following command:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start
```

To execute ElasTest in `lite` mode the command is: 
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
```

> **NOTE**: To execute ElasTest in Windows or Mac with Docker Toolbox it is necessary to obtain the virtual machine IP with the command `docker-machine ip default` and specify it in the parameter `server-address`. For example, if IP is 192.168.99.100, then the command will look like:

`docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite --server-address=192.168.99.100`

The `start` command will block the shell until ElasTest is stopped (see bellow how to stop it). But if the docker option `-d` (detached) is used, then the commands returns immediatelly and ElasTest is executed in background. This command is very useful to start ElasTest within a script if more actions needs to be done:
```
docker run -d --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
```

## How to stop ElasTest

ElasTest can be stopped using `Ctrl+C` in the shell where `start` command has been executed. Another way to stop the platform is opening a new shell and executing the `stop` command:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
```

## Wait for ElasTest is ready to be used

The `start` command outputs an informative message when ElasTest is ready to be used. That is ideal for users to know when open the ElasTest URL in the browser. When ElasTest is started within a script, is better to start it with the docker option `-d` that start ElasTest in background. In that cases, the `wait` command can be used. These command will be running until the platform is available. The `wait` command ends when ElasTest platform is ready to be used. The `wait` command is executed:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform wait
```
Is possible that ElasTest can not be started (for some error) or that the timeout is reached. In that cases, the command will end in ten minutes with 1 as exit code.

## ElasTest URL and other information

Once ElasTest is started, it is important to know what is the URL to reach it. By default, the URL is `http://localhost:37006`. But it can change in the future, so is better to query the URL executing the `inspect` command with `--api` parameter: 

```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform inspect --api
```
It ElasTest is not started, the command will return 1 as exit code. It is planned that `inspect` command can return more information about running ElasTest.

## Command help

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

### Start command

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

### Inspect command

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

### How to develop the platform container

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
