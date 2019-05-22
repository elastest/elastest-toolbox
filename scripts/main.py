#!/usr/bin/python3
import signal
import sys
import argparse
import shlex
import subprocess
import os
import threading
from functools import partial
from messages import *
from checkETM import *
from run import *
from platformInspect import *
from update import *
from pull import *
from DockerUtils import *

FNULL = open(os.devnull, 'w')


def getArgs():
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('instruction', help='Instruction to execute', type=str, choices=set(
        ('start', 'stop', 'wait', 'inspect', 'update', 'pull-images')))

    # Custom usage message
    usage = parser.format_usage()
    usage = usage.replace(
        "usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform")
    parser.usage = usage

    # If there aren't args, show help and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args([sys.argv[1]])

    # Get options from argv (Hardcoded)
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
    result = runPlatform(['stop'] + params)
    sys.exit(result)


def stopUpdate(expresion, signal, frame):
    print ('')
    print (' Stop updating.')
    sys.exit(0)

def configureDataFolders():
    bindingVolumes = getBindingVolumes().split('|')
    for bindingVolume in bindingVolumes:
        if (not bindingVolume == '' and '/data' == bindingVolume.split(':')[1]):
            os.environ['ET_DATA_IN_HOST'] = bindingVolume.split(':')[0]
            os.environ['ET_DATA_IN_CONTAINER'] = bindingVolume.split(':')[1]
            os.environ['ET_CONFIG_RELATIVE_FOLDER_PATH'] = '/config'
            os.environ['ET_LOGS_RELATIVE_FOLDER_PATH'] = '/etlogs'
            break

def setSignalsTreatment(treatment):
    signal.signal(signal.SIGINT, partial(treatment, expresion))
    signal.signal(signal.SIGTERM, partial(treatment, expresion))

#########################################################################################

# Main
args = getArgs()
argsList = argsToList(args)

expresion = argsList[0:]
params = argsList[1:]

# Config the ElasTest data folder on the host and inside the containers
configureDataFolders()

if(args.instruction == 'start'):
    if (not 'ET_DATA_IN_HOST' in os.environ):
        printMsg('elastest_home_error')
        os._exit(1)
    signal.signal(signal.SIGINT, partial(stop, params))
    signal.signal(signal.SIGTERM, partial(stop, params))

    if(len(params) == 0 or (len(params) > 0 and params[0] != '-h' and params[0] != '--help')):
        # Run in background and wait signal
        run_thread = threading.Thread(target=runPlatform, args=[expresion])
        run_thread.start()

        signal.pause()
    else:
        runPlatform(expresion)

elif(args.instruction == 'stop'):
    print 'Sending stop signal...'
    print ''

    platformImage = getContainerImage()    
    # Space after elastest/platform is necessary
    nProcessCommand = ['docker ps | grep "' + platformImage + ' " | wc -l | cat']
    nproc = int(subprocess.check_output(nProcessCommand, shell=True))    

    signalComannd = 'sh -c \'docker ps -q --filter ancestor="' + platformImage + '" | xargs -r docker kill --signal=SIGTERM\''
    result = subprocess.check_output(shlex.split(signalComannd))
    
    # If Platform container is stopped, run stop just in case there are running containers
    if(result == '' or nproc < 2):  # 2 containers: started container and this container (stop)
        print 'The Plaftorm container not exist. Forcing stop...'
        print ''
        result = runPlatform(['stop'])

elif(args.instruction == 'wait'):
    if (not 'ET_DATA_IN_HOST' in os.environ):
        printMsg('elastest_home_error')
        os._exit(1)
    checkResult = runCheckETM(params)
    exit(checkResult)
elif(args.instruction == 'inspect'):
    inspectPlatform(params)
elif(args.instruction == 'update'):
    setSignalsTreatment(stopUpdate)
    updatePlatform(params)
elif(args.instruction == 'pull-images'):
    setSignalsTreatment(stopUpdate)
    pullETImages(params)
