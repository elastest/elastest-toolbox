#!/bin/bash

function containerIp () {
    ip=$(docker inspect --format=\"{{.NetworkSettings.Networks."$COMPOSE_PROJECT_NAME"_elastest.IPAddress}}\" "$COMPOSE_PROJECT_NAME"_$1_1)
    echo $( echo $ip | cut -f2 -d'"' )
}

ET_ETM_API=$(containerIp "etm")

docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start-lite -forcepull -noports

sleep 180;
response=$(curl --write-out %{http_code} --silent --output /dev/null http://${ET_ETM_API}:8091)

docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop

if [ $response = '200' ]; then
	echo 'ElasTest ETM started'
	exit 0;
else
	echo 'ElasTest ETM not started'
	exit 1;
fi 
