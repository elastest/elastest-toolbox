#!/usr/bin/python3 -u
import sys
import shlex
import subprocess
import argparse
import os
from checkETM import *
from setEnv import *


def getArgs():
	# Define arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('mode', help='Mode to execute: start or stop', type=str, choices=set(('start','stop')))
	parser.add_argument('--lite', '-lt', help='Run in Lite mode', required=False, action='store_true')
	parser.add_argument('--dev', '-d', help='ETM dev mode. Usage: --dev=etm', required=False)
	parser.add_argument('--forcepull', '-fp', help='Force pull of all images. Usage: --forcepull', required=False, action='store_true')
	parser.add_argument('--noports', '-np', help='Unbind all ports. Usage: --noports', required=False, action='store_true')
	parser.add_argument('--logs', '-l', help='Show logs of all containers. Usage: --logs', required=False, action='store_true')
	parser.add_argument('--server-address', '-sa', help='Set server address Env Var. Usage: --server-address', required=False)

	# Custom usage message
	usage = parser.format_usage()
	usage = usage.replace("usage: run.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform")
	parser.usage = usage

	# If there aren't args, show help and exit
	if len(sys.argv) == 1:
        	parser.print_help()
        	sys.exit(1)

	args = parser.parse_args()
	return args


args = getArgs()
dockerCommand = []

mode = args.mode  # start or stop
lite = args.lite

if(args.server_address):
	setServerAddress(args.server_address)

if(args.logs == True):
	FNULL = subprocess.STDOUT
	instruction = ' up'
else:
	FNULL = open(os.devnull, 'w')
	instruction = ' up -d'


# Parameters
etm_dev = False

message = ''

#emp = '-f emp/deploy/docker-compose.yml'
emp = ''
edm = '-f ../edm/deploy/docker-compose.yml'
esm = '-f ../esm/deploy/docker-compose.yml'
eim = '-f ../eim/deploy/docker-compose.yml'
epm = '-f ../epm/deploy/docker-compose.yml'

platform_services = '-f ../platform-services/docker-compose.yml'

etm_complementary = '-f ../etm/deploy/docker-compose-complementary.yml'
etm_main = '-f ../etm/deploy/docker-compose-main.yml'
etm = etm_complementary + ' ' + etm_main

# If -dev=etm run without ETM
if(args.dev == 'etm'):
	etm = etm_complementary
	etm_dev = True

# If is NORMAL mode
if(lite == False):
	dockerCommand = 'docker-compose ' + platform_services + ' ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' ' + emp + ' -p elastest'
	message = 'Starting ElasTest Platform in Normal Mode...'
	submode = 'Normal'

# If is LITE mode
else:
	# etm root path docker-compose files:
	etm_complementary = '-f ../etm/docker/docker-compose-complementary.yml'
	etm_complementary_ports = '-f ../etm/docker/docker-compose-complementary-ports.yml'
	etm_main = '-f ../etm/docker/docker-compose-main.yml'
	etm_main_ports = '-f ../etm/docker/docker-compose-main-ports.yml'
	if(args.noports):
	        print ''
        	print 'No binding ports'
	        etm_complementary_ports = ''
		etm_main_ports = ''

	etm = etm_complementary + ' ' + etm_complementary_ports
	if (not etm_dev):
		etm = etm + ' ' + etm_main + ' ' + etm_main_ports
	dockerCommand = 'docker-compose ' + platform_services + ' ' + etm + ' -p elastest'
	message = 'Starting ElasTest Platform in Lite Mode...'
	submode = 'Lite'

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

	# Run docker-compose up/down
	try:
	    	if(args.logs):
		# If print logs, run in bg
		    subprocess.Popen(shlex.split(dockerCommand), stderr=FNULL)
		else:
		    subprocess.call(shlex.split(dockerCommand), stderr=FNULL)
	except KeyboardInterrupt: # Hide error on SIGINT
		pass
