import sys
import shlex, subprocess

dockerCommand = []
edm = '-f elastest-data-manager/deploy/docker-compose.yml'
etm = '-f elastest-torm/deploy/docker-compose.yml'
esm = '-f elastest-service-manager/deploy/docker-compose.yml'
eim = '-f elastest-instrumentation-manager/deploy/docker-compose.yml'
epm = '-f elastest-platform-manager/deploy/docker-compose.yml'

# If noetm start without ETM
if (len(sys.argv) > 1 and any("noetm" in s for s in sys.argv)):
	etm = '-f elastest-torm/deploy/docker-compose-dev.yml'
# If noesm start without ETM
if (len(sys.argv) > 1 and any("noesm" in s for s in sys.argv)):
	esm = '-f elastest-service-manager/deploy/docker-compose-dev.yml'

dockerCommand = 'docker-compose ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' -p elastest up -d'

if(len(dockerCommand) > 0):
	subprocess.call(shlex.split(dockerCommand))

