# Short description
ElasTest Platform can run in two modes:
## Normal
The normal mode in ElasTest Platform starts up all core components: EDM, EPM, EDM, EMP, EIM and ETM

## Lite
The lite mode in ElasTest Platform starts up only EUS and ETM with necesary services: Logstash, Elasticsearch, MySQL, Dockbeat and RabbitMQ

# Run from repo
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
python run.py down normal
```

## Run in lite mode
To run in lite mode execute:
```
python run.py start-lite
```
To stop platform execute:
```
python run.py down lite
```

# Run from docker image
First, Pull ElasTest Platform image:
```
docker pull elastest/platform
```

## Run in normal mode
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start
```

## Run in lite mode
To start up platform in lite mode execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start-lite
```
## Stop in both modes
To stop ElasTest Platform in both modes execute:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
```
