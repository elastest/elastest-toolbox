#!/usr/bin/python3
import os
import shlex, subprocess
import time
import urllib2
import socket
import sys
import argparse

projectName = 'elastest'
component = 'etm'
containerName = projectName + '_' + component + '_1'
etmPort = '8091'

etprintEnabled=True
args=[]

# Input Arguments
def getArgs(params):
	# Define arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--container', '-c', help='Sets timeout in seconds for wait to the ETM container creation. Usage: --container=240', required=False, action='store_true')
	parser.add_argument('--running', '-r', help='Sets timeout in seconds for wait to ETM is running. Usage: --running=290', required=False)

	# Custom usage message
	usage = parser.format_usage()
	usage = usage.replace("usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait")
	parser.usage = usage

	args = parser.parse_args(params)
	return args


# Custom print function
def etprint(msg):
	if(etprintEnabled):
		print(msg)

def getETMIp():
	command = "docker inspect --format=\"{{.NetworkSettings.Networks." + projectName + "_elastest.IPAddress}}\" "+ containerName
	try:
		ip = subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE)
		# remove /n
		ip = ip.rstrip()
		return ip
	except subprocess.CalledProcessError:	
	        raise Exception('Could not get the ip')

def containerIP():
	ip = ''
	wait = True
	timeout = 240 #seconds
	if(args.container):
		timeout=args.container
	start_time = time.time()
	# your code
	while (wait):
		try:
			ip = getETMIp()
			wait = False
		except subprocess.CalledProcessError:	
			pass
		except KeyboardInterrupt: # Hide error on SIGINT
			exit(0)
		except Exception as error:
			pass

		if((time.time() - start_time) >= timeout):
			etprint('Timeout: container ' + containerName + ' not created')
			exit(1)
	return ip

def getEtmUrl():
	try:
		ip = getETMIp()
		url = 'http://' + ip + ':' + etmPort
		return url
	except subprocess.CalledProcessError:	
		pass
	except KeyboardInterrupt: # Hide error on SIGINT
		pass
	except Exception as error:
	        raise Exception('Could not get the url')
	return ''

def checkWorking(url):
	working = False
	req = urllib2.Request(url)
	try:
	    resp = urllib2.urlopen(req)
	except urllib2.HTTPError as e1:
	    return working
	except urllib2.URLError as e2:
	    return working
	except KeyboardInterrupt: # Hide error on SIGINT
		exit(0)
	else:
	    # 200
	    working = True
	return working


def insertPlatformIntoNetwork():
	try:
		backslashStr = '\\'
		doubleBackslash = backslashStr + backslashStr
		command = 'cat /proc/self/cgroup | grep "docker" | sed s/' + doubleBackslash + '//' + doubleBackslash + 'n/g | tail -1'
		id = subprocess.check_output(command, shell=True, stderr=subprocess.PIPE)
		if(id == ''):
			return ''

		commandTwo = 'docker network connect ' + projectName + '_elastest ' + id
		result = subprocess.call(shlex.split(commandTwo))
		if(result > 0):
			etprint('Error: Unable to register Platform on the network')
			exit (1)
		etprint('Platform inserted into network succesfully')
	except subprocess.CalledProcessError:
		pass
	except KeyboardInterrupt: # Hide error on SIGINT
		exit(0)


# Main function
def runCheckETM(params=[], printEnabled=True):
	global args
	args = getArgs(params)
	global etprintEnabled
	etprintEnabled = printEnabled


        etprint('')
        etprint('Waiting for ETM...')

	# Get ETM container IP
	etmIP = containerIP()

	etprint('')
	etprint('Container created with IP: ' + etmIP)

	# Insert platform into network
	insertPlatformIntoNetwork()

	# Check if service is started and running
	try:
		url = getEtmUrl()
	except Exception as error:
		print(error)
		exit(1)
	wait = True
	working = False
	message_counter=1

	timeout = 290 #seconds
	if(args.running):
		timeout=args.running
	start_time = time.time()
	while (wait):
		working = checkWorking(url)
		if (working):
			wait = False
		else:
			if (message_counter == 1):
				etprint('ETM is not ready. Please wait...')
				message_counter = 0
			if((time.time() - start_time) >= timeout):
				etprint('Timeout: container ' + containerName + ' not started')
				wait = False

	if (working):
		etprint('ETM is ready in ' + url)
		return 0
	else:
		etprint('ERROR: ElasTest ETM not started correctly')
		return 1

