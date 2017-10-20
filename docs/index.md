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

ElasTest can be executed in the developer machine with linux, windows or mac operating system. But it also can be installed in a server to be used remotely using its public IP or FQDN. In the current version, ElasTest doesn't have a user management system. It has only one admin user. It is planned to include a powerful user management system with fine grained autorization in future releases. 

## How to execute ElasTest in the developer machine

When ElasTest is started the first time it is downloaded. There is no "installation" step. 

ElasTest is executed in `full` mode with the following command:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start
```

To execute ElasTest in `lite` mode the command is: 
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
```

The `start` command outputs an informative message when ElasTest is ready to be used. That is ideal for users to know when open the ElasTest URL in the browser. 

That command will block the shell until ElasTest is stopped using `Ctrl+C` (see bellow other ways to stop it).

> **NOTE**: To execute ElasTest in Windows or Mac with "Docker Toolbox" it is necessary to obtain the docker virtual machine IP with the command `docker-machine ip default` and specify it in the parameter `server-address` of the start command. For example, if IP is 192.168.99.100, then the command will look like:

`docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite --server-address=192.168.99.100`

## How to execute ElasTest in a server

To execute ElasTest in a server for remote usage, it is necessary to include the parameter `--server-adress` with the public IP or the FQDN of the server. It is necessary to configure it because ElasTest needs to know how to create public URLs to their own services:

The command will be the following one:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --server-address=<public_ip_or_host>`
```
ElasTest main GUI and REST API is accessible in localhost on port 37006. Other ports are needed during execution because new services can be started in new ports. We plan to implement a way to control the port range, but at the moment, any port in range [32768 to 61000] can be used and thus should be open to public in the firewall or proxy.

## How to stop ElasTest

ElasTest can be stopped using `Ctrl+C` in the shell where `start` command has been executed. Another way to stop the platform is opening a new shell and execute the `stop` command:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform stop
```

## ElasTest versions

ElasTest is in active development. There is no stable version yet. For the moment, the `start` command will execute the last development version available. That is, the version generated from latest commit of the master branch. It is idel for development, but latest development version can be broken from time to time. 

>> **NOTE**: New images are not downloaded automatically when updated in the server. To update your local ElasTest images to the latest ones first update the `elastest/platform` with `docker pull elastest/platform` and then execute ElasTest with `--pullcore` option. 

Every day the current version is tagged as the nightly version of that day. In that way, you can execute the code available in a specifc day. This is specially useful when latest version is broken. Te command to execute a nightly version is:

```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform:<date> start
```
Where `date` has the format `YYYYMMDD`. Not all dates are available. Take a look to [elastest/platform in DockerHub](https://hub.docker.com/r/elastest/platform/tags/) to see what tags can be used. 

## Tips for troubleshooting development issues

ElasTest is composed by several components. Some components are started on startup, the core components. Other components can be executed on demand or associated to the execution of TJobs. That components are Test Engines and Test Support Services. ElasTest components are executed as one or several docker containers. Some containers are started on startup and others on demand. 

Sometimes during development it is necessary to look to some component log. As every component is one or several containers, executing `docker run logs <container_name>` you can see the logs of that container. You can list all running containers with `docker ps`. The number and name of containers is evolving as ElasTest is being developed. But, for example, the main container is called `elastest_etm_1`. Then, you can inspect its logs with:

```
docker logs elastest_etm_1
```

## Start ElasTest from a script

ElasTest `start` command by default blocks the shell until ElasTest is stopped. This is generally desirable when a developer uses the shell to start ElasTest, but it is not very convenient if ElasTest has to be started within a script, for example in a CI system.

When `start` command is executed with `-d` docker option (detached), the command shows the container id just created and returns immediatelly. ElasTest is executed in background:
```
docker run -d --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
```

To wait wait until ElasTest is ready the command `wait` can be used:
```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform wait
```
In the case ElasTest is not started for some error or timeout is reached, the command will print an informative message and will exit with non zero result.

Once ElasTest is started, it is important to know what is the URL to reach it. The command `inspect` will return information about ElasTest. At the moment, the only information returned is the graphical user interface URL obtained with `--api` parameter:

```
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform inspect --api
```
If ElasTest is not started, the command will return 1 as exit code. It is planned that `inspect` command can return more information about running ElasTest.

In summary, to start and manage ElasTest in a bash script, the following commands can be used:

```
docker run -d --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform start --lite
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform wait
ELASTEST_GUI_URL=$(sudo docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform inspect --api)
echo "ElasTest GUI URL: $ELASTEST_GUI_URL"
```

In CI systems is usual to execute tests in containers to facilitiate developers to bring their own environment with the tests. If you plan to access ElasTest from inside a container it is important to remember that it is necessary that test container and ElasTest main container belongs to the same docker network. If they belong to different networks, network connection will fail. ElasTest containers are associated to the network `elastest_elastest`. Execute the following commands inside a container, just after ElasTest has been executed, to connect the "current" container to `elastest_elastest` network:

```
containerId=$(cat /proc/self/cgroup | grep "docker" | sed s/\\//\\n/g | tail -1)
echo "containerId = ${containerId}"
docker network connect elastest_elastest ${containerId}
```

## ElasTest management commands

As you can see, ElasTest can be managed executing the `elastest/platform` container. That container can be run with different commands and each command has different parameters. To know what are the available commands you can executed:

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

### Wait command

```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait -h
```

The output is:

```
usage: docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait [-h] [--container CONTAINER] [--running RUNNING]

optional arguments:
  -h, --help            show this help message and exit
  --container CONTAINER, -c CONTAINER
                        Sets timeout in seconds for wait to the ETM container
                        creation. Usage: --container=240
  --running RUNNING, -r RUNNING
                        Sets timeout in seconds for wait to ETM is running.
                        Usage: --running=290
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
To start ElasTest platform in `full` mode with the `main.py` script execute:

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

# Troubleshooting
In case of you have problems starting, try running platform with --logs (or -l) parameter to view more information of process
