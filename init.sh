#!/bin/sh

stop() {
  if [ -z "$RUN_PID" ]; then
    echo 'Not stopped'
    exit 1
  else
     pkill -TERM -P $RUN_PID # Kill run.py process and childs
     echo ''
     echo '*************************'
     echo '*  Stopping components  *'
     echo '*************************'
     echo ''
     if [ -z "$SUBMODE" ]; then
       python run.py 'stop' $MODE
     else
       python run.py 'stop' $MODE $SUBMODE
     fi
     exit 0
  fi
}

#if there aren't arguments or first arg is start, then up docker compose
if [ $1 = 'start' ] || [ $1 = 'start-lite' ]; then
	# Trap SIGTERM to stop execution
	trap stop TERM
	export MODE=$1

	# Run run.py script to start components
	if [ -z "$2" ]; then
	  echo "Starting..."
	  export SUBMODE=$2
	  python run.py $1 & export RUN_PID=$!
	else
	  echo "Starting with" $2
	  python run.py $1 $2 & export RUN_PID=$!
	fi

	echo ''
	echo '*****************************************************************************************'
	echo '*  To stop open new terminal and type:                                                  *'
	echo '*  docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop  *'
	echo '*****************************************************************************************'
	echo ''

	# Wait for stop signal
	while true; do
	  sleep 20 &
	  wait $!
	done

# docker run stop
elif [ $1 = 'stop' ]; then
	echo 'Sending stop signal...'
	echo ''
	sh -c 'docker ps -q --filter ancestor="elastest/platform" | xargs -r docker kill --signal=SIGTERM'
	# If container is stopped, run stop just in case there are running containers
	if [ $? -gt 0 ]; then
		echo ''
		echo 'trying again...'
		echo ''
	       python run.py 'stop'
	fi
fi
