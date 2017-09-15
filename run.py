import sys
import shlex, subprocess

dockerCommand = []
edm = '-f edm/deploy/docker-compose.yml'
etm = '-f etm/deploy/docker-compose.yml'
esm = '-f esm/deploy/docker-compose.yml'
eim = '-f eim/deploy/docker-compose.yml'
epm = '-f epm/deploy/docker-compose.yml'

if (len(sys.argv) > 1):
	instruction = sys.argv[1] #up -d or down

	# If noetm start without ETM
	if (any("noetm" in s for s in sys.argv)):
		etm = '-f etm/deploy/docker-compose-dev.yml'
	# If noesm start without ETM
	if (any("noesm" in s for s in sys.argv)):
		esm = '-f esm/deploy/docker-compose-dev.yml'

	dockerCommand = 'docker-compose ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' -p elastest ' + instruction

	if(len(dockerCommand) > 0):
		subprocess.call(shlex.split(dockerCommand))

