import sys
import shlex, subprocess

dockerCommand = []

#Temporally dockerCommand:
dockerCommand = 'docker-compose -f elastest-data-manager/deploy/docker-compose.yml -f elastest-torm/deploy/docker-compose.yml -f elastest-service-manager/deploy/docker-compose.yml -p elastest down'

if(len(dockerCommand) > 0):
	subprocess.call(shlex.split(dockerCommand))

