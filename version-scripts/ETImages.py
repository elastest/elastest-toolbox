#!/usr/bin/python3
import yaml
import json
import re
from ETFiles import *
from DockerUtils import *

core_list = []
tss_list = []
engines_list = []
et_image_name_prefix = 'elastest/'
preloaded_images = ['']

novnc_image_property = 'novnc.image.id'
socat_image_property = 'et.socat.image'
chrome_browser = 'chrome'
firefox_browser = 'firefox'

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


def getYmlFromETServicesJsonPath(path):
    data = getJson(path)
    return getYmlFromETServicesJsonFile(data)


def getYmlFromETServicesJsonFile(json):
    try:
        return yaml.load(json['manifest']['manifest_content'])
    except KeyError:
        return yaml.load('')

def getPropertiesFromFile(path):    
    separator = "="
    keys = {}    
    with open(path) as f:
        for line in f:
            if separator in line:                
                name, value = line.split(separator, 1)
                keys[name.strip()] = value.strip()        
    return keys;

#*** Images Lists Getters By File Type ***#

def getImagesFromYmlFilesList(files_list):
    files_images = []
    for path in files_list:
        files_images = files_images + getImagesList(getYml(path))
    return files_images

def getImagesFromJsonFilesList(files_list):
    files_images = []
    for path in files_list:
        files_images = files_images + \
            getImagesList(getYmlFromETServicesJsonPath(path))
    return files_images

def getImageFromJsonFile(service_name):
    image = None    
    file_path = getFilePathByImage(service_name)    
    image = getImagesList(getYmlFromETServicesJsonPath(file_path))
    return image


#*** Images Lists Getters By Component Type ***#

def getCoreImages():
    return getImagesFromYmlFilesList(core_list)


def getTSSImages():
    return getImagesFromJsonFilesList(tss_list)


def getEnginesImages():
    return getImagesFromYmlFilesList(engines_list)

def getImageByServiceName(service_name):
    image = None
    image = getImageFromJsonFile(service_name)
    return image

def getBrowserImage(browser):
    properties = {}    
    properties = getPropertiesFromFile(getFilePathByImage('eusBrowsers'))
    latest_version = 0
    browser_image = None    
    
    for key, value in properties.iteritems():        
        if browser in key:
            if re.findall('\d+', key)[0] > latest_version:
                latest_version = re.findall('\d+', key)[0]
                browser_image = value                
    
    return browser_image


def getBrowsersImages():    
    browser_images = []    
    browser_images.append(getBrowserImage(chrome_browser))
    browser_images.append(getBrowserImage(firefox_browser))    
    return browser_images
    
def getImageFromFileProperties(image_key, properties_type):
    image = None
    properties = {}    
    properties = getPropertiesFromFile(getFilePathByImage(properties_type))
    image = properties.get(image_key, None)
    
    return image
    

##################################    Updaters    ##################################

def modifyImageTag(image, tag):
    new_image = image.split(':')[0]
    new_image = new_image + ':' + tag
    return new_image


def updateImagesTagOfReadYml(d, tag):
    key = 'image'
    if key in d:
        # If is ElasTest Image, set image tag
        if(d[key].startswith(et_image_name_prefix)):
            d[key] = modifyImageTag(d[key], tag)
        return d
    for k in d:
        if isinstance(d[k], dict):
            d[k] = updateImagesTagOfReadYml(d[k], tag)
    return d


def updateImagesTagOfYmlFile(path, tag):
    yml_file = getYml(path)
    new_yml = updateImagesTagOfReadYml(yml_file, tag)
    # Save new yml file with images tag updated
    saveYml(path, new_yml)


def updateImagesTagOfJsonFile(path, tag):
    json_file = getJson(path)
    yml = getYmlFromETServicesJsonFile(json_file)
    new_yml = updateImagesTagOfReadYml(yml, tag)
    json_file['manifest']['manifest_content'] = yaml.dump(new_yml, encoding=('utf-8'), default_flow_style=False)    

    # Save new json file with images tag updated
    saveJson(path, json_file)


#*** Images Lists Updaters By File Type ***#

def updateImagesTagOfYmlFiles(files_list, tag):
    for path in files_list:
        updateImagesTagOfYmlFile(path, tag)


def updateImagesTagOfJsonFilesList(files_list, tag):
    files_images = []
    for path in files_list:
        updateImagesTagOfJsonFile(path, tag)


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


def getAllImages():
    loadETLists()
    images_list = []
    images_list = images_list + getCoreImages()
    images_list = images_list + getTSSImages()
    images_list = images_list + getEnginesImages()
    return images_list

def getAllImagesByExecMode(mode):
    images_list = []
    global core_list
    core_list = getCoreListByExecMode(mode)
    images_list = images_list + list(set(getCoreImages()))
    if (mode == 'experimental' or mode == 'experimental-lite'):
        global tss_list
        tss_list = getTSSList()
        global engines_list
        engines_list = getEnginesList()        
        #images_list = images_list + getTSSImages()
        #images_list = images_list + getEnginesImages()
    else:
        images_list = images_list + getPreloadedImages()
    
    images_list.append(getContainerImage())
    
    return images_list

def getElastestImages(without_tag):
    images_list = getAllImages()

    elastest_images = []
    for image in images_list:
        if(image.startswith(et_image_name_prefix)):
            if(without_tag):
                image_splited = image.split(':')
                elastest_images.append(image_splited[0])
            else:
                elastest_images.append(image)
    return elastest_images

def getElastestImagesByExecMode(mode, without_tag):
    images_list = getAllImagesByExecMode(mode)

    elastest_images = []
    for image in images_list:
        if(image.startswith(et_image_name_prefix)):
            if(without_tag):
                image_splited = image.split(':')
                elastest_images.append(image_splited[0])
            else:
                elastest_images.append(image)
    return elastest_images

def getElasTestImagesAsString(mode):
    images_list = getElastestImagesByExecMode(mode, False)    
    return ",".join(map(str,images_list))


def getPreloadedImages():    
    images_list = []
    images_list = images_list + getBrowsersImages()
    
    images_list = images_list + getImageByServiceName('eus')

    image_aux = getImageFromFileProperties(novnc_image_property,'eusNovnc')    
    if image_aux:
        images_list.append(image_aux)
        image_aux = None

    image_aux = getImageFromFileProperties(socat_image_property,'etmSocat')
    if image_aux:
        images_list.append(image_aux)
        image_aux = None

    return images_list

def updateFilesImagesWithTag(tag):
    loadETLists()
    updateCoreImagesTag(tag)
    updateTSSImagesTag(tag)
    updateEnginesImagesTag(tag)


def pullAllImages():
    images_list = getAllImages()
    for image in images_list:
        pullImage(image)

def pullPreloadImages():
    images_list = getPreloadedImages()
    for image in images_list:       
        pullImage(image)
