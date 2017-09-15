# Run
```
docker run --name="toolbox" -v /var/run/docker.sock:/var/run/docker.sock --rm edujgurjc/elastest-toolbox
```

# Stop
```
docker kill --signal=SIGTERM toolbox
```
