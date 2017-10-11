#!/usr/bin/python3
import subprocess
import shlex
import time
import sys
from ETImages import *

def pullImage(image):
	pull = 'docker pull '
	pull_result = subprocess.call(shlex.split(pull + image))

	if(pull_result > 0):
		print 'Error on pull image ' + image
		exit(1)

def getNightlyTag():
	return time.strftime('%Y%m%d')

def tagImage(image, tag):
	new_tagged = image + ':' + tag
	tag_command = 'docker tag ' + image + ' ' + new_tagged
	tag_result = subprocess.call(shlex.split(tag_command))

	if(tag_result > 0):
		print 'Error on tag image ' + new_tagged
		exit(1)
	return new_tagged

def pushImage(image):
	push = 'docker push '
	push_result = subprocess.call(shlex.split(push + new_tagged))

	if(push_result > 0):
		print 'Error on push image ' + new_tagged
		exit(1)

def createETNightlyImage(image, tag):
	# Pull
	pullImage(image)

	# Tag
	new_image = tagImage(image, tag)

	# Push
	pushImage(new_image)

	print 'Image ' + new_image + ' pushed'
	return tag

#Main functions

def createETNightlyImages():
	images_list = getElastestImages(True)
	tag =  getNightlyTag()


	for image in images_list:
		createETNightlyImage(image, tag)
	print 'All images has been pushed'
	return tag

def updateFilesToNightly():
	tag = createETNightlyImages()
	updateFilesImagesWithTag(tag)
	return tag

