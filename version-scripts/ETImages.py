#!/usr/bin/python3
import yaml
import json
from ETFiles import *

core_list = []
tss_list = []
engines_list = []

def getValuesListOfKey(d, key):
	values_list = []
	if key in d:
        	return [d[key]]
	for k in d:
        	if isinstance(d[k], dict):
			values_list = values_list + getValuesListOfKey(d[k], key)
	return values_list

def getImagesListOfKey(d):
	return getValuesListOfKey(d, 'image')

def getJson(path):
	with open(path, 'r') as stream:
		data = json.load(stream)
		return data
	return json.load('')

def getYmlFromJson(path):
	data = getJson(path)
	try:
		return yaml.load(data['manifest']['manifest_content'])
	except KeyError:
		return yaml.load('')

def getYml(path):
	with open(path, 'r') as stream:
	    try:
		return yaml.load(stream)		
	    except yaml.YAMLError as exc:
		return yaml.load('')

def getImagesFromYmlFilesList(files_list):
	files_images = []
	for path in files_list:
		files_images = files_images + getImagesListOfKey(getYml(path))
	return files_images

def getImagesFromJsonFilesList(files_list):
	files_images = []
	for path in files_list:
		files_images = files_images + getImagesListOfKey(getYmlFromJson(path))
	return files_images

def getCoreImages():
	return getImagesFromYmlFilesList(core_list)

def getTSSImages():
	return getImagesFromJsonFilesList(tss_list)

def getEnginesImages():
	return getImagesFromYmlFilesList(engines_list)

def loadETLists():
	global core_list 
	core_list = getCoreList()
	global tss_list 
	tss_list = getTSSList()
	global engines_list
	engines_list = getEnginesList()	

# Main
def getElastestImages(without_tag):
	loadETLists()
	et_image_name_prefix = 'elastest/'
	images_list = []
	images_list = images_list + getCoreImages()
	images_list = images_list + getTSSImages()
	images_list = images_list + getEnginesImages()
	
	elastest_images = []
	for image in images_list:
		if(image.startswith(et_image_name_prefix)):
			if(without_tag):
				image_splited = image.split(':')
				elastest_images.append(image_splited[0])
			else:
				elastest_images.append(image)
	return elastest_images

