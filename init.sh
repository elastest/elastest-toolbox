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

     if [ -z "$OPTIONS" ]; then
       python run.py 'down'
     else
       python run.py 'down' $OPTIONS
     fi
     exit 0
  fi
}

#if there aren't arguments or first arg is start, then up docker compose
if [ $# -eq 0 ] || [ $1 = 'start' ]; then
	# Trap SIGTERM to stop execution
	trap stop TERM

	# Run run.py script to start components
	if [ -z "$OPTIONS" ]; then
	  echo "Starting all components"
	  python run.py 'up -d' & export RUN_PID=$!
	else
	  echo "Starting with" $OPTIONS
	  python run.py 'up -d' $OPTIONS & export RUN_PID=$!
	fi

	echo ''
	echo '*******************************************************************************************'
	echo '*  To stop open new terminal and type docker kill --signal=SIGTERM <this_container_name>  *'
	echo '*******************************************************************************************'
	echo ''

	# Wait for stop signal
	while true; do
	  sleep 20 &
	  wait $!
	done

# docker compose down
elif [ $1 = 'stop' ]; then
	echo 'Send stop signal'
	sh -c 'docker kill --signal=SIGTERM toolbox'
fi
