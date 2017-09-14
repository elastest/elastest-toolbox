# Run
```
docker run --name="toolbox" -e "DOCKER_HOST=172.17.0.1:2375" --rm edujgurjc/elastest-toolbox
```

# Run without ETM
```
docker run --name="toolbox" -e "DOCKER_HOST=172.17.0.1:2375" -e "OPTIONS=noetm" --rm edujgurjc/elastest-toolbox
```

# Stop
```
docker kill --signal=SIGTERM toolbox
```
