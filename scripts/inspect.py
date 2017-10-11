#!/usr/bin/python3 -u
import sys
import shlex, subprocess
import argparse
import os
from checkETM import *

def getArgs(params):
	# Define arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('--api', '-a', help='Return current status of ElasTest API', required=False, action='store_true')

	# Custom usage message
	usage = parser.format_usage()
	usage = usage.replace("usage: inspect.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform inspect")
	parser.usage = usage

	# If there aren't args, show help and exit
	if len(params)==0:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args(params)
	return args

def inspectPlatform(params):
	args = getArgs(params)
	if(args.api):
		try:
			ip = getETMIp()
			apiUrl = getEtmUrl()
			checkWorking(apiUrl)
		except subprocess.CalledProcessError:
			exit(1)
		except KeyboardInterrupt:
			exit(1)
