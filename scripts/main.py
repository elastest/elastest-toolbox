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

def stop(params, signal, frame):
	printMsg('stopping')
	result = subprocess.call(['python', 'run.py', 'stop'] + params)
        sys.exit(result)

if(len(sys.argv) > 1):
	args = sys.argv
	expresion = args[1:]
	params = args[2:]

	if(args[1] == 'start'):
		signal.signal(signal.SIGINT, partial(stop, params))
		signal.signal(signal.SIGTERM, partial(stop, params))
		
		subprocess.Popen(['python', 'run.py'] + expresion, stderr=FNULL)
		printMsg('stop help')
		if(len(params) > 0 and params[0] != '-h' and params[0] != '--help'):
			signal.pause()
	
	elif(args[1] == 'stop'):
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

	elif(args[1] == 'wait'):
		checkResult = runCheckETM()
		exit(checkResult)
	elif(args[1] == 'inspect'):
		subprocess.call(['python', 'inspect.py'] + params)
	elif(args[1] == '-h' or args[1] == '--help'):
		subprocess.call(['python', 'run.py', '-h'])
	else:
		subprocess.call(['python', 'run.py', '-h'])
	
else:
	subprocess.call(['python', 'run.py', '-h'])



