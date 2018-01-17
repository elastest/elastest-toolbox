#!/usr/bin/python3 -u
import sys
import shlex
import subprocess
import argparse
import os
import time
from DockerUtils import *
from ETImages import *

dev_tag = 'dev'
eps_volume = 'elastest_platform-services'
eps_image = 'elastest/platform-services'
pull_command = 'pull-images'


def getArgs(params):
    # Define arguments
    parser = argparse.ArgumentParser()

    # Custom usage message
    usage = parser.format_usage()
    usage = usage.replace(
        "usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform update")
    parser.usage = usage

    # If there aren't args, show help and exit
    if len(params) > 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(params)
    return args


def updatePlatform(params, mode):    
    global args
    args = getArgs(params)
    continueUpdate = True

    confirmMessage1 = 'You are going to update the ElasTest version ' + getVersionFromHostContainer() + '. Continue?'
    #Confirm that you want to update this ElasTest version    
    if(yes_or_no(confirmMessage1)):
        elasTestRunning = elasTestIsRunning()
        if(elasTestRunning):            
            confirmMessage2 = 'The version of ElasTest that you want to update is already running and it is necessary to stop it. Continue?'            
            if(not yes_or_no(confirmMessage2)):
                continueUpdate = False
            
        if(continueUpdate):
            print ('')
            print (' Preparing the environment...')    
            if(elasTestRunning):
                sys.stdout.write (' Stopping ElasTest...')
                stopRunningElasTest()
                while (elasTestIsRunning()):
                    time.sleep(1)
                    sys.stdout.write('.')
                print ('')
            deleteVolume(eps_volume)
            print ('')
            print (' Upating ElasTest...')
            print ('')
            #Update platform image    
            image = getContainerImage()
            updateImage(image)

            print ('')
            #Update platform-services image
            updateImage(eps_image)

            #Get images list to update            
            dockeArgs = '-e ET_OLD_IMAGES="%s"'%(getElasTestImagesAsString(mode))

            #Download/update the images of the ElasTest components
            executePlatformCommand(image, pull_command, dockeArgs)
            print ('')
            print ('Update finished successfully.')
        else:
            exit(0)
    else:
        exit(0)



def updateImage(image):    
    print (' Updating ' + image)
    if (dev_tag not in image):
        image_parts = image.split(':')
        image = image_parts[0]
    pullImage(image)


def elasTestIsRunning():    
    platformImage = getContainerImage()    
    nProcessCommandStr =  "docker ps | grep %s | wc -l | cat"%(platformImage)
    nProcessCommand = [nProcessCommandStr]    
    nproc = int(subprocess.check_output(nProcessCommand, shell=True))
    if(nproc > 1):        
        return True
    else:        
        return False


def stopRunningElasTest():    
    platformImage = getContainerImage()
    getContainersCommand = ['docker ps -q --filter ancestor=' + platformImage]
    platformContainers = str(subprocess.check_output(getContainersCommand, shell=True)).split()
    platformContainers.remove(getContainerId())
    for containerId in platformContainers:        
        killContainer(containerId, 'SIGTERM')
    

def yes_or_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        #sys.stdout.write(question + prompt)
        choice = raw_input(question + prompt).lower().strip()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
                            

    
