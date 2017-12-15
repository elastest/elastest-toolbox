#!/usr/bin/python3
import subprocess
import shlex
import time
import sys
import os

pull_command = 'pull-images'

def pullImage(image):
    pull = 'docker pull '
    pull_result = subprocess.call(shlex.split(pull + image))

    if(pull_result > 0):
        print('Error on pull image ' + image)
        exit(1)


def tagImage(image, tag):
    new_tagged = image + ':' + tag
    tag_command = 'docker tag ' + image + ' ' + new_tagged
    tag_result = subprocess.call(shlex.split(tag_command))

    if(tag_result > 0):
        print('Error on tag image ' + new_tagged)
        exit(1)
    return new_tagged


def pushImage(image):
    push = 'docker push '
    push_result = subprocess.call(shlex.split(push + image))

    if(push_result > 0):
        print('Error on push image ' + image)
        exit(1)


def getContainerImage():
    command = 'docker inspect --format "{{ index .Config.Image }}" ' + \
        os.environ['HOSTNAME']
    image = subprocess.check_output(shlex.split(command))
    return image


def deleteVolume(name):
    print ('')
    print (' Deleting some volumes....')
    command = 'docker volume rm ' + name
    subprocess.call(shlex.split(command))        

    
def executePlatformCommand(image, command):
    if (command == pull_command):
        print ('')
        print (' Updating ElasTest components....')
        print ('')
        command_line = 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ' + \
        image + ' ' + command        
    
    subprocess.check_output(shlex.split(command_line))
