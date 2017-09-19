#!/usr/bin/python3 -u
import sys
import shlex, subprocess

dockerCommand = []

if (len(sys.argv) > 1):
	mode = sys.argv[1] #start, start-lite or stop
	submode = ''
	instruction = ' up -d'
	
	#Parameters
	etm_dev = False
	force_pull = False
	bind_ports = True	
 
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

	# If there is second param
	if(len(sys.argv) > 2):
		# If valid submodule
		if(sys.argv[2] == 'start' or sys.argv[2] == 'start-lite' or sys.argv[2] == 'normal' or sys.argv[2] == 'lite'):
			submode = sys.argv[2] #start, start-lite, normal or lite on stop

		### Init Parameters ###
		# If -dev option is passed and -dev=etm
		if(any('-dev=etm' in s for s in sys.argv)):
			etm = etm_complementary
			etm_dev = True

		# If -forcepull option is passed (only on start/start-lite)
		if(mode != 'stop' and any('-forcepull' in s for s in sys.argv)):
			force_pull = True

		# If -dev option is passed 
		if(any('-noports' in s for s in sys.argv)):
			bind_ports = False


	# If mode=start or mode=stop with submode: start, normal or nothing
	if(mode == 'start' or (mode == 'stop' and (submode == 'start' or submode == 'normal' or submode == ''))):
		dockerCommand = 'docker-compose ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + ' ' + epm + ' ' + emp + ' -p elastest'
		message = 'Starting ElasTest Platform in Normal Mode...'

	# If mode=start-lite or mode=stop with submode: start-lite or lite
	elif(mode == 'start-lite' or (mode == 'stop' and (submode == 'start-lite' or submode == 'lite'))):
		# etm root path docker-compose files:
		etm_complementary = '-f etm/docker-compose-complementary.yml'
		etm_complementary_ports = '-f etm/docker-compose-complementary-ports.yml'
		etm_main = '-f etm/docker-compose-main.yml'
		etm_main_ports = '-f etm/docker-compose-main-ports.yml'
		etm_lite = '-f etm/docker-compose-lite.yml'
		if(not bind_ports):
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
		message = 'Stopping ElasTest Platform...'
			

	if(len(dockerCommand) > 0):
		# If Force pull, do pull for each image
		if(force_pull):
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
		subprocess.call(shlex.split(dockerCommand))

