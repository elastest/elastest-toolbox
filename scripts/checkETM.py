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

def containerIP():
	ip = ''
	wait = True
	counter = 120
	while (wait and counter > 0):
		try:
			command = "docker inspect --format=\"{{.NetworkSettings.Networks." + projectName + "_elastest.IPAddress}}\" "+ containerName
			ip = subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE)
			wait = False
			# remove /n
			ip = ip.rstrip()
		except subprocess.CalledProcessError:	
			pass
		counter-=1

	if (counter == 0):
		print 'Timeout: container ' + containerName + ' not created'
		exit(1)
	return ip

def getEtmUrl():
	ip = containerIP()
	url = 'http://' + ip + ':' + etmPort
	return url

def checkWorking(url):
	working = False
	req = urllib2.Request(url)
	try:
	    resp = urllib2.urlopen(req)
	except urllib2.HTTPError as e1:
	    return working
	except urllib2.URLError as e2:
	    return working
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
			print 'Error: Unable to register Platform on the network'
			exit (1)
		print 'Platform inserted into network succesfully'
	except subprocess.CalledProcessError:
		pass


# Main function
def runCheckETM():

	# Insert platform into network
	insertPlatformIntoNetwork()

	# Get ETM container IP
	etmIP = containerIP()
	print ''
	print 'Container created with IP: ' + etmIP


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
				print 'ETM is not ready. Please wait...'

			counter-=1
			time.sleep(2)


	if (counter == 0):
		print 'Timeout: container ' + containerName + ' not started'
		exit(1)
	else:
		if (working):
			print 'ETM is ready in ' + url
			exit(0)
		else:
			print 'ERROR: ElasTest ETM not started correctly'
			exit(1)

