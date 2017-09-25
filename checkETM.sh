#!/bin/bash

containerIp () {
    ip=$(docker inspect --format=\"{{.NetworkSettings.Networks."$COMPOSE_PROJECT_NAME"_elastest.IPAddress}}\" "$COMPOSE_PROJECT_NAME"_$1_1 2> /dev/null)
    error=$?
    echo $( echo $ip | cut -f2 -d'"' )
    exit $error
}

projectName="elastest"

export COMPOSE_PROJECT_NAME=$projectName

# Check if ETM container is created
ET_ETM_API=$(containerIp "etm")

while [ $? -gt 0 ] ; do
	ET_ETM_API=$(containerIp "etm")
done

# wait ETM started
initial=85
counter=$initial
while ! nc -z -v $ET_ETM_API 8091; do
    echo $ET_ETM_API 8091
    if [ $counter = $initial ]; then
	    echo ''
	    echo "ETM is not ready. Wait please..."
    fi
    sleep 2
    # prevent infinite loop
    counter=$(($counter-1))
    if [ $counter = 0 ]; then
	    echo "Timeout"
	    exit 1;
	    break;
    fi
done

response=$(curl --write-out %{http_code} --silent --output /dev/null http://$ET_ETM_API:37006)

if [ $response = '200' ]; then
	echo "ETM is ready in http://$ET_ETM_API:8091"
	exit 0;
else
	echo 'ERROR: ElasTest ETM not started'
	exit 1;
fi 
