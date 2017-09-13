# Run
```
docker run --name="toolbox" -e "DOCKER_HOST=172.17.0.1:2375" edujgurjc/elastest-toolbox
```

# Run without ETM
```
docker run --name="toolbox" -e "DOCKER_HOST=172.17.0.1:2375" -e "OPTIONS=noetm" edujgurjc/elastest-toolbox
```
