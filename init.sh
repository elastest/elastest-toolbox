#!/bin/sh

if [ -z "$OPTIONS" ]; then
  echo "Starting all components"
  exec python run.py
else
  echo "Starting with" $OPTIONS
  exec python run.py $OPTIONS
fi
