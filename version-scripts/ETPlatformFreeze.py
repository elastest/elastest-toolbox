#!/usr/bin/python3
import subprocess
import shlex
import sys
from ETDockerNightly import *
from DockerUtils import *



def buildImageFromToolbox(tag, image, dockerfile):
    if(not dockerfile):
        dockerfile = ''
    docker_command = 'docker build --build-arg GIT_COMMIT=$(git rev-parse HEAD) --build-arg COMMIT_DATE=$(git log -1 --format=%cd --date=format:%Y-%m-%dT%H:%M:%S) --build-arg VERSION=' + \
        tag + ' -t ' + image + ' . ' + dockerfile
    command = 'sh -c "cd ..; ' + docker_command + '"'  # Note: cd only in this call
    build_result = subprocess.call(shlex.split(command))

    if(build_result > 0):
        print('Error on build image: ' + image)
        exit(1)


def buildPlatformServices(tag):
    image = 'elastest/platform-services:' + tag
    dockerfile = '-f platform-services/Dockerfile'
    buildImageFromToolbox(tag, image, dockerfile)
    return image


def buildPlatform(tag):
    image = 'elastest/platform:' + tag
    buildImageFromToolbox(tag, image, '')
    return image


buildingNightly = False
if (len(sys.argv) > 1 and not sys.argv[1] == 'bytime'):
    print('Freezing release')
    tag = sys.argv[1]    
else:
    print('Freezing nightly')
    tag = 'bytime'

if(tag == 'bytime'):
    buildingNightly = True

only_modify_files = False

if (len(sys.argv) > 2 and sys.argv[2] == 'True'):
    # If True, only modify files without build and push images
    only_modify_files = True

print('Reading ET components files to modify images tags...')
tag = updateFilesToNightly(tag, only_modify_files)

# Build and push Platform Services Image
print('Building Platform Services Image')
services_image = buildPlatformServices(tag)
print('Pushing Platform Services Image')
pushImage(services_image)

# Build and push Platform Image
print('Building Platform Image')
platform_image = buildPlatform(tag)
print('Pushing Platform Image')
pushImage(platform_image)

if (buildingNightly):
    print('Pushing nightly images')
    # Publish nightly images
    pushImage(tagImage(platform_image, "nightly"))
    pushImage(tagImage(services_image, "nightly"))
