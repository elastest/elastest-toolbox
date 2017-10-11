#!/usr/bin/python3
import os
import shlex, subprocess
import time
import urllib2
import socket

projectName = 'elastest'
component = 'etm'
containerName = projectName + '_' + component + '_1'
etmPort = '8091'
etprintEnabled=True

# Custom print function
def etprint(msg):
	if(etprintEnabled):
		print(msg)

def getETMIp():
	command = "docker inspect --format=\"{{.NetworkSettings.Networks." + projectName + "_elastest.IPAddress}}\" "+ containerName
	ip = subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE)
	# remove /n
	ip = ip.rstrip()
	return ip

def containerIP():
	ip = ''
	wait = True
	counterDefault = 120
	counter = counterDefault
	while (wait and counter > 0):
		try:
			ip = getETMIp()
			wait = False
		except subprocess.CalledProcessError:	
			pass
		except KeyboardInterrupt: # Hide error on SIGINT
			exit(0)
		counter-=1
		time.sleep(2)

	if (counter == 0):
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
		exit(0)
	print 'container not created'
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
def runCheckETM(printEnabled=True):
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
	counterDefault = 145
	counter = counterDefault

	url = getEtmUrl()
	wait = True
	working = False

	while (wait and counter > 0):
		working = checkWorking(url)
		if (working):
			wait = False
		else:
			if (counter == counterDefault or counter == (counterDefault / 2)):
				etprint('ETM is not ready. Please wait...')

			counter-=1
			time.sleep(2)


	if (counter == 0):
		etprint('Timeout: container ' + containerName + ' not started')
		return 1
	else:
		if (working):
			etprint('ETM is ready in ' + url)
			return 0
		else:
			etprint('ERROR: ElasTest ETM not started correctly')
			return 1

