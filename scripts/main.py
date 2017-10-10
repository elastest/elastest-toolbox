#!/usr/bin/python3
import signal
import sys
import argparse
import shlex, subprocess
import os
from functools import partial
from messages import *
from checkETM import *

FNULL = open(os.devnull, 'w')

def getArgs():
	# Define arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('instruction', help='Instruction to execute', type=str, choices=set(('start','stop', 'wait', 'inspect')))

	# Custom usage message
	usage = parser.format_usage()
	usage = usage.replace("usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform")
	parser.usage = usage

	# If there aren't args, show help and exit
	if len(sys.argv) == 1:
        	parser.print_help()
        	sys.exit(1)

	args = parser.parse_args([sys.argv[1]])

	#Get options from argv (Hardcoded)
	if(len(sys.argv) > 1):
		args.options = sys.argv[2:]
	else:
		args.options = []
	return args

def argsToList(args):
	argsList = []
	for arg in vars(args):
		value = getattr(args, arg)
		if(value != None and value != [] and value != 'dummy'):
			if(isinstance(value, list)):
				argsList = argsList + value
			else:
				argsList.append(value)
	return argsList


def stop(params, signal, frame):
	printMsg('stopping')
	result = subprocess.call(['python', 'run.py', 'stop'] + params)
        sys.exit(result)


#########################################################################################

# Main
args = getArgs()
argsList = argsToList(args)

expresion = argsList[0:]
params = argsList[1:]

if(args.instruction == 'start'):
	signal.signal(signal.SIGINT, partial(stop, params))
	signal.signal(signal.SIGTERM, partial(stop, params))
	
	if(len(params) == 0 or (len(params) > 0 and params[0] != '-h' and params[0] != '--help')):
		proc = subprocess.Popen(['python', 'run.py'] + expresion)
		printMsg('stop help')
		signal.pause()
		
	else:
		subprocess.call(['python', 'run.py'] + expresion)

elif(args.instruction == 'stop'):
	print 'Sending stop signal...'
	print ''

	nProcessCommand = 'echo $(docker ps | grep elastest/platform | wc -l)'
	nproc = subprocess.check_output(shlex.split(nProcessCommand))

	signalComannd = 'sh -c \'docker ps -q --filter ancestor="elastest/platform" | xargs -r docker kill --signal=SIGTERM\''
	result = subprocess.call(shlex.split(signalComannd))

	# If container is stopped, run stop just in case there are running containers
	if(result > 0 or nproc < 2): # 2 containers: started container and this container (stop)
		print ''
		print 'trying again...'
		print ''
		result = subprocess.call(['python', 'run.py', 'stop'])

elif(args.instruction == 'wait'):
	checkResult = runCheckETM()
	exit(checkResult)
elif(args.instruction == 'inspect'):
	subprocess.call(['python', 'inspect.py'] + params)


