#!/bin/sh

if [ -z "$OPTIONS" ]; then
  echo "Start all components"
  exec python run.py
else
  echo "Start with " $OPTIONS
  exec python run.py $OPTIONS
fi
