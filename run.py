import sys
import shlex, subprocess

dockerCommand = []

"""
if (len(sys.argv) > 1 and sys.argv[1] == 'nomonitoring'):
	dockerCommand = 'docker-compose -f ./elastest-data-manager/deploy/docker-compose.yml -f ./elastest-torm/deploy/docker-compose.yml -f ./elastest-service-manager/deploy/docker-compose.yml -f ./elastest-instrumentation-manager/deploy/docker-compose.yml -f ./elastest-platform-manager/deploy/docker-compose.yml -p elastest up -d'
else:	
	dockerCommand = 'docker-compose -f ./elastest-data-manager/deploy/docker-compose.yml -f ./elastest-torm/deploy/docker-compose.yml -f ./elastest-service-manager/deploy/docker-compose.yml -f ./elastest-instrumentation-manager/deploy/docker-compose.yml -f ./elastest-platform-manager/deploy/docker-compose.yml -f ./elastest-monitoring-platform/deploy/docker-compose.yml -p elastest up -d'
"""

#Temporally dockerCommand:
if (len(sys.argv) > 1 and sys.argv[1] == 'noetm'):
	dockerCommand = 'docker-compose -f elastest-data-manager/deploy/docker-compose.yml -f elastest-service-manager/deploy/docker-compose.yml -p elastest up'

else:
	dockerCommand = 'docker-compose -f elastest-data-manager/deploy/docker-compose.yml -f elastest-torm/deploy/docker-compose.yml -f elastest-service-manager/deploy/docker-compose.yml -p elastest up'

if(len(dockerCommand) > 0):
	subprocess.call(shlex.split(dockerCommand))

