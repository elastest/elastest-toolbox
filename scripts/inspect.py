#!/usr/bin/python3 -u
import sys
import shlex, subprocess
import argparse
import os
from checkETM import *

# Define arguments
parser = argparse.ArgumentParser()
parser.add_argument('--api', '-a', help='Return current status of ElasTest API', required=False, action='store_true')

# Custom usage message
usage = parser.format_usage()
usage = usage.replace("usage: inspect.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform inspect")
parser.usage = usage

# If there aren't args, show help and exit
if len(sys.argv)==1:
	parser.print_help()
	sys.exit(1)

args = parser.parse_args()

if(args.api):
	checkResult = runCheckETM()
	if(checkResult == 0):
		apiUrl = getEtmUrl()
		print ''
		print 'ElasTest API info:'
		print 'Url: ' + apiUrl
		exit(0)
	else:
		exit(1)
