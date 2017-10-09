#!/bin/bash

# Start
echo 'Running Platform...'
docker run -d -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start --lite --forcepull --noports

# Check if is started
echo 'Checking if ETM is working...'
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait
responseCheck=$?

echo 'Stopping ET Platform...'
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
echo ''

if [ $responseCheck -gt 0 ] ; then
	echo 'ElasTest ETM not started'
	exit 1;
else
	echo 'ElasTest ETM started'
	exit 0;
fi 
