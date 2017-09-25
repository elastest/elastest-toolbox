#!/bin/bash

containerIp () {
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

# Check if ETM container is created
ERROR=$(containerIp "etm" "check")

while [ $ERROR -gt 0 ] ; do
	ERROR=$(containerIp "etm" "check")
done

ET_ETM_API=$(containerIp "etm")

# wait ETM started
initial=85
counter=$initial
while ! nc -z -v $ET_ETM_API 8091 2> /dev/null; do
    if [ $counter = $initial ]; then
	    echo ''
	    echo "ETM is not ready. Please wait..."
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

response=$(curl --write-out %{http_code} --silent --output /dev/null http://$ET_ETM_API:8091)

if [ $response = '200' ]; then
	echo "ETM is ready in http://$ET_ETM_API:8091"
	exit 0;
else
	echo 'ERROR: ElasTest ETM not started'
	exit 1;
fi 
