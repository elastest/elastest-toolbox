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
       python down.py
     else
       python down.py $OPTIONS
     fi
     exit 0
  fi
}

# Trap SIGTERM to stop execution
trap stop TERM

# Run run.py script to start components
if [ -z "$OPTIONS" ]; then
  echo "Starting all components"
  python run.py & export RUN_PID=$!
else
  echo "Starting with" $OPTIONS
  python run.py $OPTIONS & export RUN_PID=$!
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
