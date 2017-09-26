#!/usr/bin/python3
import os
import shlex, subprocess
import time
import urllib2

projectName = 'elastest'
component = 'etm'
containerName = projectName + '_' + component + '_1'
etmPort = '8091'

def containerIP():
	ip = ''
	wait = True
	counter = 70
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
	print ''
	print 'Container created with IP: ' + ip
	return ip

def checkWorking(url):
	working = False
	req = urllib2.Request(url)
	try:
	    resp = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
	    print e.output
	except urllib2.URLError as e:
	    print e.output
	else:
	    # 200
	    working = True
	return working


# First, get ETM container IP
etmIP = containerIP();

# Check if service is started
counterDefault = 90
counter = counterDefault
checkCommand = 'nc -z -v ' + etmIP + ' 8091'
wait = True
while (wait and counter > 0):
	try:
		subprocess.check_call(shlex.split(checkCommand), stderr=subprocess.PIPE)
		wait = False
	except subprocess.CalledProcessError:	
		if (counter == counterDefault or counter == (counterDefault / 2)):
			print 'ETM is not ready. Please wait...'

	counter-=1
	time.sleep(2)

if (counter == 0):
	print 'Timeout: container ' + containerName + ' not started'
	exit(1)
print ''
print 'ETM is started'

# Check if service is working
workingCommand = 'curl --write-out %{http_code} http://' + etmIP + ':' + etmPort
url = 'http://' + etmIP + ':' + etmPort
print 'Checking if ETM is working correctly...'
working = checkWorking(url)

if (working):
	print 'ETM is ready in ' + url
	exit(0)
else:
	print 'ERROR: ElasTest ETM not started'
	exit(1)



