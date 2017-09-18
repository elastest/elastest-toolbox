# Run from repo
To run ElasTest platform you need to have docker-compose and python installed.
Once installed performs the following steps:
1. Clone elastest-toolbox repository and move into:
```
git clone --recursive https://github.com/elastest/elastest-toolbox
```
```
cd elastest-toolbox
```
2. Start up platform:
```
python run.py up
```
>Note: to hide logs run: ```python run-py up -d```
3. Shutdown platform:
```
python run.py down
```

# Run from docker image
1. Pull platform image:
```
docker pull elastest/platform
```
2. Start up platform:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform
```
3. Shutdown platform:
```
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
```
