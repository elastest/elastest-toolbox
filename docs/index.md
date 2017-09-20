# ElasTest Platform
ElasTest Platform starts ElasTest on docker containers. Can run in two modes:

## Run in normal mode
The normal mode in ElasTest Platform starts up all core components: EDM, EPM, EDM, EMP, EIM and ETM. To start up platform in normal mode execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start
```

## Run in lite mode
The lite mode in ElasTest Platform starts up only ESM and ETM with necesary services: Logstash, Elasticsearch, MySQL, Dockbeat and RabbitMQ. To start up platform in lite mode execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start-lite
```

## Stop in both modes
To stop ElasTest Platform in both modes execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
```

## Parameters
ElasTest platform allows to pass configuration parameters at the end of the run commands:
* Not bind ports: `-noports`
* Force pull of all docker images: `-forcepull`
* Start in ETM development mode: `-dev=etm`
>For example: `docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start-lite -noports`


# Development
To run ElasTest platform you need to have docker-compose and python installed.
Once installed clone elastest-toolbox repository and move into:
```
git clone --recursive https://github.com/elastest/elastest-toolbox
```
```
cd elastest-toolbox
```

## Run in normal mode
To run in normal mode execute:
```
python run.py start
```
To stop platform execute:
```
python run.py stop normal
```

## Run in lite mode
To run in lite mode execute:
```
python run.py start-lite
```
To stop platform execute:
```
python run.py stop lite
```

> You can pass parameters of Parameters section
