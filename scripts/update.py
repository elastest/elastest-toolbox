#!/usr/bin/python3 -u
import sys
import shlex
import subprocess
import argparse
import os
from DockerUtils import *

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

    print ('')
    print (' Preparing the environment...')    
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

    #Download/update the images of the ElasTest components
    executePlatformCommand(image, pull_command)
    print ('')
    print ('Update finished successfully.')    


def updateImage(image):    
    print (' Updating ' + image)
    if (dev_tag not in image):
        image_parts = image.split(':')
        image = image_parts[0]
    pullImage(image)
