#!/usr/bin/python3 -u
import sys
import shlex, subprocess
import argparse

# Define arguments
parser = argparse.ArgumentParser(description='Starts up ElasTest Platform.')

parser.add_argument('command', help='Command mode to execute: start, start-lite or stop')
parser.add_argument('submode', help='(Only for stop command) Submode equivalent to command mode executed: normal or lite', nargs='?', default='normal')
parser.add_argument('-dev', help='ETM dev mode. Usage: -dev=etm', required=False)
parser.add_argument('-forcepull', help='Force pull of all images. Usage: -forcepull', required=False, action='store_true')
parser.add_argument('-noports', help='Unbind all ports. Usage: -noports', required=False, action='store_true')
parser.add_argument('-verbose', help='Show logs of all containers. Usage: -verbose', required=False, action='store_true')

args = parser.parse_args()

dockerCommand = []


mode = args.command #start, start-lite or stop
submode = args.submode

if(args.verbose == True):
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

	# Run docker-compose up/down''
	subprocess.call(shlex.split(dockerCommand))

