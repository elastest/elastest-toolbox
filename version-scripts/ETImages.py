#!/usr/bin/python3
import yaml
import json
from ETFiles import *

core_list = []
tss_list = []
engines_list = []
et_image_name_prefix = 'elastest/'

##################################    Getters    ##################################


#*** Getters By Object ***#

def getValuesListOfKey(d, key):
	values_list = []
	if key in d:
        	return [d[key]]
	for k in d:
        	if isinstance(d[k], dict):
			values_list = values_list + getValuesListOfKey(d[k], key)
	return values_list

def getImagesList(d):
	return getValuesListOfKey(d, 'image')


def getYmlFromETServicesJson(path):
	data = getJson(path)
	try:
		return yaml.load(data['manifest']['manifest_content'])
	except KeyError:
		return yaml.load('')

#*** Images Lists Getters By File Type ***#

def getImagesFromYmlFilesList(files_list):
	files_images = []
	for path in files_list:
		files_images = files_images + getImagesList(getYml(path))
	return files_images

def getImagesFromJsonFilesList(files_list):
	files_images = []
	for path in files_list:
		files_images = files_images + getImagesList(getYmlFromETServicesJson(path))
	return files_images


#*** Images Lists Getters By Component Type ***#

def getCoreImages():
	return getImagesFromYmlFilesList(core_list)

def getTSSImages():
	return getImagesFromJsonFilesList(tss_list)

def getEnginesImages():
	return getImagesFromYmlFilesList(engines_list)


##################################    Updaters    ##################################

def modifyImageTag(image, tag):
	new_image = image.split(':')[0]
	new_image = new_image + ':' + tag
	return new_image

def updateImagesTagOfReadYml(d, tag):
	key = 'image'
	if key in d:
		d[key] = modifyImageTag(d[key], tag)
        	return d
	for k in d:
        	if isinstance(d[k], dict):
			d[k] = updateImagesTagOfReadYml(d[k], tag)
	return d

def updateImagesTagOfYmlFile(path, tag):
	yml_file = getYml(path)
	new_yml = updateImagesTagOfReadYml(yml_file, tag)


#*** Images Lists Updaters By File Type ***#

def updateImagesTagOfYmlFiles(files_list, tag):
	for path in files_list:
		updateImagesTagOfYmlFile(path, tag)

def updateImagesTagOfJsonFilesList(files_list, tag):
	files_images = []
	for path in files_list:
		files_images = files_images + getImagesList(getYmlFromETServicesJson(path))


#*** Images Lists Updaters By Component Type ***#

def updateCoreImagesTag(tag):
	updateImagesTagOfYmlFiles(core_list, tag)

def updateTSSImagesTag(tag):
	updateImagesTagOfJsonFilesList(tss_list, tag)

def updateEnginesImagesTag(tag):
	updateImagesTagOfYmlFiles(engines_list, tag)


##################################    Main functions    ##################################


# Loads lists of files
def loadETLists():
	global core_list 
	core_list = getCoreList()
	global tss_list 
	tss_list = getTSSList()
	global engines_list
	engines_list = getEnginesList()	


def getElastestImages(without_tag):
	loadETLists()
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


def updateFilesImagesWithTag(tag):
	loadETLists()
	updateCoreImagesTag(tag)
	updateTSSImagesTag(tag)
	updateEnginesImagesTag(tag)


#print(getElastestImages(True))

