#!/bin/bash

function containerIp () {
	ip=$(docker inspect --format=\"{{.NetworkSettings.Networks."$COMPOSE_PROJECT_NAME"_elastest.IPAddress}}\" "$COMPOSE_PROJECT_NAME"_$1_1 2> /dev/null)
	error=$?
	if [ -z "$2" ]; then
		echo $( echo $ip | cut -f2 -d'"' )
	elif [ "$2" = 'check' ]; then
		echo $error
	fi
}

projectName="elastest"

export COMPOSE_PROJECT_NAME=$projectName

# Start

echo 'Running Platform...'
docker run -d -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start --lite --forcepull --noports --nocheck


# Check if ETM container is created
ERROR=$(containerIp "etm" "check")

while [ $ERROR -gt 0 ] ; do
	ERROR=$(containerIp "etm" "check")
done

ET_ETM_API=$(containerIp "etm")

docker logs -f "$COMPOSE_PROJECT_NAME"_etm_1 &

# Connect test container to docker-compose network

containerId=$(cat /proc/self/cgroup | grep "docker" | sed s/\\//\\n/g | tail -1)

echo "containerId = ${containerId}"

docker network connect ${projectName}_elastest ${containerId}

# wait ETM started
initial=90
counter=$initial
while ! nc -z -v $ET_ETM_API 8091 2> /dev/null; do
    if [ $counter = $initial ]; then
	    echo "ETM is not ready in address $ET_ETM_API and port 8091"
    fi
    echo 'Wait while ETM is starting up'
    sleep 2
    # prevent infinite loop
    counter=$(($counter-1))
    if [ $counter = 0 ]; then
	    echo "Timeout"
	    exit 1;
	    break;
    fi
done

echo ''
echo "ETM is ready in address $ET_ETM_API and port 8091"

echo 'Check if ETM is working...'
responseCheck=$(curl --write-out %{http_code} --silent --output /dev/null http://$ET_ETM_API:8091)

echo 'Stopping ET Platform...'
docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop
echo ''

if [ $responseCheck = '200' ]; then
	echo 'ElasTest ETM started'
	exit 0;
else
	echo 'ElasTest ETM not started'
	exit 1;
fi 
