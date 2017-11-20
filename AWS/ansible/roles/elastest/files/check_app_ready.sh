#!/bin/bash 

sleep 1m

CONTAINER_ID=$(docker ps --format "table {{.ID}}" | tail -n +2)

while true
do 
  docker logs $CONTAINER_ID | grep "Press Ctrl+C to stop"
  if [ $? == 0 ]; then
    break
  fi
  sleep 1
done

