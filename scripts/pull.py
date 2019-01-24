#!/usr/bin/python3 -u
import sys
import shlex
import subprocess
import argparse
import os
from DockerUtils import *
from ETImages import *

dev_tag = 'dev'
def getArgs(params):
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', '-m', help='Set ElasTest execution mode. Usage: --mode=singlenode',
                        type=str, choices=set(('mini', 'singlenode')), default='mini')

    # Custom usage message
    usage = parser.format_usage()
    usage = usage.replace(
        "usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform pull-images")
    parser.usage = usage

    # If there aren't args, show help and exit
    if len(params) > 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(params)
    return args


def pullETImages(params):
    global args
    args = getArgs(params)
    mode = args.mode

    print ('')
    print ('Pulling ElasTest images...')
    images_list = getElastestImagesByExecMode(mode, False)
    for image in images_list:
        print ('')
        print ('Image to update: ') + image
        print ('')
        if (existsLocalImage(image)):
            pullImage(image)

    deleteOldImages(os.environ['ET_OLD_IMAGES'].split(','), images_list)


def deleteOldImages(oldImages, newImages):
    print (' Removing old images...')
    imagesToRemove = ''
    for oldImage in oldImages:        
        if (oldImage not in newImages):
            print (' Image to remove: ' + oldImage)
            imagesToRemove = imagesToRemove + oldImage + ' '
    deleteImages(imagesToRemove)
    deleteDanglingImages()
