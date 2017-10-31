#!/usr/bin/python3 -u
import sys
sys.path.append('../version-scripts')
from ETImages import *
import shlex
import subprocess
import argparse
import os
import threading
from checkETM import *
from setEnv import *



def getArgs(params):
	# Define arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('mode', help='Mode to execute: start or stop', type=str, choices=set(('start','stop')))
	parser.add_argument('--lite', '-lt', help='Run in Lite mode', required=False, action='store_true')
	parser.add_argument('--dev', '-d', help='ETM dev mode. Usage: --dev=etm', required=False)
	parser.add_argument('--pullall', '-pa', help='Force pull of all images. Usage: --pullall', required=False, action='store_true')
	parser.add_argument('--pullcore', '-pc', help='Force pull of only necessary images. Usage: --pullcore', required=False, action='store_true')
	parser.add_argument('--noports', '-np', help='Unbind all ports. Usage: --noports', required=False, action='store_true')
	parser.add_argument('--logs', '-l', help='Show logs of all containers. Usage: --logs', required=False, action='store_true')
	parser.add_argument('--server-address', '-sa', help='Set server address Env Var. Usage: --server-address=XXXXXX', required=False)
	parser.add_argument('--shared-folder', '-sf', help='Set the folder used to share files between ElasTest Components. Usage: --shared-folder=shared-data/', required=False)
	parser.add_argument('--with-proxy', '-wp', help='Start NGINX proxy for ElasTest services. Usage: --with-proxy=true', required=False)

	# Custom usage message
	usage = parser.format_usage()
	usage = usage.replace("usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start")
	parser.usage = usage

	# If there aren't args, show help and exit
	if len(params) == 0:
        	parser.print_help()
        	sys.exit(1)

	args = parser.parse_args(params)
	return args


def runPlatform(params):
	args = getArgs(params)
	dockerCommand = []

	mode = args.mode  # start or stop
	lite = args.lite

	if(args.server_address):
		#setServerAddress(args.server_address)
		files_list = []
		files_list.append('../etm/deploy/docker-compose-main.yml')
		files_list.append('../etm/docker/docker-compose-main.yml')
		replaceEnvVarValue('ET_PUBLIC_HOST', args.server_address, 'localhost', files_list)
	
	if(args.shared_folder):
		files_list = []
		files_list.append('../etm/deploy/docker-compose-main.yml')
		files_list.append('../etm/docker/docker-compose-main.yml')
		replaceEnvVarValue('ET_SHARED_FOLDER', args.shared_folder, '/shared-data/', files_list)
		
	if(args.logs == True):
		FNULL = subprocess.STDOUT
		instruction = ' up'
	else:
		FNULL = open(os.devnull, 'w')
		instruction = ' up -d'


	# Parameters
	etm_dev = False

	message = ''

	etm_proxy = '-f ../etm/docker/docker-compose-proxy.yml'
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
		dockerCommand = 'docker-compose ' + platform_services + ' ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' ' + emp + ' ' + (etm_proxy if args.with_proxy else '') + ' -p elastest'
		print 'Command: ' + dockerCommand
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
		dockerCommand = 'docker-compose ' + platform_services + ' ' + etm + ' ' + (etm_proxy if args.with_proxy else '') + ' -p elastest'
		print 'Command: ' + dockerCommand
		message = 'Starting ElasTest Platform in Lite Mode...'
		submode = 'Lite'

	# If mode=stop
	if(mode == 'stop'):
		instruction = ' down'
		message = 'Stopping ElasTest Platform (' + submode + ' mode)...'

	if(len(dockerCommand) > 0):
		# If Force pull or pull necessary images, do pull for each image
		if(mode != 'stop'):
			if(args.pullall):
				print 'Forcing pull...'
				print ''
				pullAllImages()
			elif(args.pullcore):
				print 'Pulling necessary images...'
				print ''
				try:
					subprocess.call(shlex.split(dockerCommand + ' pull'))
				except KeyboardInterrupt: # Hide error on SIGINT
					exit(1)

		dockerCommand = dockerCommand + instruction
		print ''
		print message
		if(etm_dev):
			print '(Without ETM)'
		print ''

		# Run docker-compose up/down
		try:
		    	if(args.logs and mode == 'start'):
			# If print logs, run in bg
				subprocess.Popen(shlex.split(dockerCommand), stderr=FNULL)
			else:
				result = subprocess.call(shlex.split(dockerCommand), stderr=FNULL)
				if(result == 0 and mode == 'start'):
					print 'Services has been created'
					if(not etm_dev):
						# Run check ETM in bg
						check_thread = threading.Thread(target=runCheckETM)
						check_thread.daemon = True
						check_thread.start()
			return 0
		except KeyboardInterrupt: # Hide error on SIGINT
			pass
		except subprocess.CalledProcessError:
			return 1
