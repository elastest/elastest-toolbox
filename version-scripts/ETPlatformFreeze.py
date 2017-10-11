#!/usr/bin/python3
import subprocess
import shlex
import sys
from ETDockerNightly import *

def buildImageFromToolbox(tag, image):
	command = 'sh -c "cd ..; docker build -t ' + image + ' . -f platform-services/Dockerfile"' #Note: cd only in this call
	build_result = subprocess.call(shlex.split(command))

	if(build_result > 0):
		print 'Error on build image: ' + image
		exit(1)

def buildPlatformServices(tag):
	image = 'elastest/platform-services:' + tag
	buildImageFromToolbox(tag, image)
	return image

def buildPlatform(tag):
	image = 'elastest/platform:' + tag
	buildImageFromToolbox(tag, image)
	return image


print('Reading ET components files to modify images tags...')
tag = updateFilesToNightly()

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
