#!/usr/bin/python3 -u
import sys
import shlex, subprocess
import argparse

# Define arguments
parser = argparse.ArgumentParser()

parser.add_argument('mode', help='Mode to execute: start, start-lite or stop')
parser.add_argument('submode', help='(Only for stop command) Submode equivalent to mode executed: normal or lite', nargs='?', default='normal')
parser.add_argument('--dev', '-d', help='ETM dev mode. Usage: --dev=etm', required=False)
parser.add_argument('--forcepull', '-fp', help='Force pull of all images. Usage: --forcepull', required=False, action='store_true')
parser.add_argument('--noports', '-np',help='Unbind all ports. Usage: --noports', required=False, action='store_true')
parser.add_argument('--logs', '-l', help='Show logs of all containers. Usage: --logs', required=False, action='store_true')

# Custom usage message
usage = parser.format_usage()
usage = usage.replace("usage: run.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform")
parser.usage=usage

# If there aren't args, show help and exit
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

dockerCommand = []

mode = args.mode #start, start-lite or stop
submode = args.submode

if(args.logs == True):
	instruction = ' up'
else:
	instruction = ' up -d'


#Parameters
etm_dev = False

message = ''

#emp = '-f emp/deploy/docker-compose.yml'
emp = ''
edm = '-f edm/deploy/docker-compose.yml'
esm = '-f esm/deploy/docker-compose.yml'
eim = '-f eim/deploy/docker-compose.yml'
epm = '-f epm/deploy/docker-compose.yml'

etm_complementary = '-f etm/deploy/docker-compose-complementary.yml'
etm_main = '-f etm/deploy/docker-compose-main.yml'
etm_lite = '-f etm/deploy/docker-compose-lite.yml'
etm = etm_complementary + ' ' + etm_main

# If -dev=etm run without ETM
if(args.dev == 'etm'):
	etm = etm_complementary
	etm_dev = True

# If mode=start or mode=stop with submode: start, normal or nothing
if(mode == 'start' or (mode == 'stop' and (submode == 'start' or submode == 'normal' or submode == ''))):
	dockerCommand = 'docker-compose ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' ' + emp + ' -p elastest'
	message = 'Starting ElasTest Platform in Normal Mode...'

# If mode=start-lite or mode=stop with submode: start-lite or lite
elif(mode == 'start-lite' or (mode == 'stop' and (submode == 'start-lite' or submode == 'lite'))):
	# etm root path docker-compose files:
	etm_complementary = '-f etm/docker/docker-compose-complementary.yml'
	etm_complementary_ports = '-f etm/docker/docker-compose-complementary-ports.yml'
	etm_main = '-f etm/docker/docker-compose-main.yml'
	etm_main_ports = '-f etm/docker/docker-compose-main-ports.yml'
	etm_lite = '-f etm/docker/docker-compose-lite.yml'
	if(args.noports):
		print ''
		print 'No binding ports'
		etm_complementary_ports = ''
		etm_main_ports = ''

	etm = etm_complementary + ' ' + etm_complementary_ports
	if (not etm_dev):
		etm = etm + ' ' + etm_main + ' ' + etm_main_ports + ' ' + etm_lite
	dockerCommand = 'docker-compose ' + etm + ' -p elastest'
	message = 'Starting ElasTest Platform in Lite Mode...'

# If mode=stop
if(mode == 'stop'):
	instruction = ' down'
	message = 'Stopping ElasTest Platform (' + submode + ' mode)...'
		

if(len(dockerCommand) > 0):
	# If Force pull, do pull for each image
	if(mode != 'stop' and args.forcepull == True):
		print 'Forcing pull...'
		print ''
		subprocess.call(shlex.split(dockerCommand + ' pull'))

	dockerCommand = dockerCommand + instruction
	print ''
	print message
	if(etm_dev):
		print '(Without ETM)'
	print ''

	#Check if ETM is started
	if(mode != 'stop' and not etm_dev):
		subprocess.Popen(shlex.split('./checkETM.sh'))

	# Run docker-compose up/down''
	subprocess.call(shlex.split(dockerCommand))

