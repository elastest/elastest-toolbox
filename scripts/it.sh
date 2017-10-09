#!/bin/bash

projectName="elastest"

export COMPOSE_PROJECT_NAME=$projectName

# Start

echo 'Running Platform...'
docker run -d -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start --lite --forcepull --noports

# Check if is started
echo 'Checking if ETM is working...'
responseCheck=$('docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait')

echo 'Stopping ET Platform...'
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
echo ''

if [ $responseCheck -eq 0 ]; then
	echo 'ElasTest ETM started'
	exit 0;
else
	echo 'ElasTest ETM not started'
	exit 1;
fi 
