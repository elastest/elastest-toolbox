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
et_docker_image_name_prefix = 'ET_DOCKER_IMG'
preloaded_images = ['']

novnc_image_property = 'novnc.image.id'
socat_image_property = 'et.socat.image'
chrome_browser = 'chrome'
firefox_browser = 'firefox'

images_to_pre_pulling = ['elastest/eus-novnc', 'elastest/etm-socat', 'elastest/eus', 'elastest/etm-dockbeat']
tss_images_in_normal_mode = ['eus']

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("ASCII") # <- or any other encoding of your choice
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

##################################    Getters    ##################################


#*** Getters By Object ***#

def getValuesListOfKey(d, key):
    values_list = []
    if key in d:
        try:
            return [d[key]]
        except TypeError:
            print ('dict modified: ' + yaml.dump(d, stream=None, default_flow_style=True))
            dm = yaml.dump(d, stream=None, default_flow_style=True)
            return [dm[key]]
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

def getETDockerImagesFromYml(yml):
    dynamic_images = []
    environment = 'environment'
    if environment in yml:
        for var in yml[environment]:
            try:
                if(var.startswith(et_docker_image_name_prefix)):
                    dynamic_images.append(var.split('=')[1])                    
            except TypeError:
                print ('Error getting ET_DOCKER_IMAGES')
        return dynamic_images
    for k in yml:
        if isinstance(yml[k], dict):
            dynamic_images = dynamic_images + getETDockerImagesFromYml(yml[k])
    return dynamic_images

#*** Images Lists Getters By File Type ***#

def getImagesFromYmlFilesList(files_list):
    files_images = []
    for path in files_list:
        files_images = files_images + getImagesList(getYml(path))
        files_images = files_images + getETDockerImagesFromYml(getYml(path))
    return files_images

def getImagesFromJsonFilesList(files_list):
    files_images = []
    for path in files_list:        
        files_images = files_images + \
            getImagesList(getYmlFromETServicesJsonPath(path))
        files_images = files_images + \
            getETDockerImagesFromETServiceJsonFile(path)
    return files_images

def getImageFromJsonFile(service_name):
    image = None    
    file_path = getFilePathByImage(service_name)    
    image = getImagesList(getYmlFromETServicesJsonPath(file_path))
    return image

def getETDockerImagesFromETServiceJsonFile(path):
    json_file = getJson(path)
    yml = getYmlFromETServicesJsonFile(json_file)
    return getETDockerImagesFromYml(yml)

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
    #print ('dict: ' + str(d))
    if key in d:
        # If is ElasTest Image, set image tag
        try:
            if(d[key].startswith(et_image_name_prefix)):
                d[key] = modifyImageTag(d[key], tag)
                return d
        except TypeError:
            print ('dict modified: ' + yaml.dump(d, default_flow_style=False))
            dm = yaml.dump(d, stream=None, default_flow_style=True)
            if(dm[key].startswith(et_image_name_prefix)):
                dm[key] = modifyImageTag(dm[key], tag)
                return dm
            return dm
    for k in d:
        if isinstance(d[k], dict):
            d[k] = updateImagesTagOfReadYml(d[k], tag)
    return d


def updateETDockerImagesTagYml(yml, tag):    
    environment = 'environment'
    if environment in yml:
        for i, var in enumerate(yml[environment]):
            try:
                if(var.startswith(et_docker_image_name_prefix)):
                    yml[environment][i] = modifyImageTag(var, tag)                    
            except TypeError:
                print ('Error updating ET_DOCKER_IMAGES')                
        return yml
    for k in yml:
        if isinstance(yml[k], dict):
            yml[k] = updateETDockerImagesTagYml(yml[k], tag)
    return yml


def updateImagesTagOfYmlFile(path, tag):
    yml_file = getYml(path)
    new_yml = updateImagesTagOfReadYml(yml_file, tag)
    new_yml = updateETDockerImagesTagYml(new_yml, tag)
    # Save new yml file with images tag updated
    saveYml(path, new_yml)


def updateImagesTagOfJsonFile(path, tag):
    json_file = getJson(path)    

    # Update images version in the docker-compose files
    yml = getYmlFromETServicesJsonFile(json_file)
    new_yml = updateImagesTagOfReadYml(yml, tag)    
    new_yml = updateETDockerImagesTagYml(new_yml, tag)
    json_file['manifest']['manifest_content'] = json.loads(json.dumps(yaml.dump(new_yml, encoding=('utf-8'), default_flow_style=False), cls=MyEncoder))    
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


def getTSSImagesByServices(tss_list):
    image_list = []
    image_file_list = []
    for tss in tss_list:
        image_file_list.append(getTSSFile(tss))
    image_list = getImagesFromJsonFilesList(image_file_list)
    return image_list


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
        images_list = images_list + getTSSImages()
        images_list = images_list + getEnginesImages()
    else:
        images_list = images_list + getTSSImagesByServices(tss_images_in_normal_mode)
    
    images_list.append(getContainerImage())
    
    return images_list


def getAllCoreImagesByExecMode(mode):
    images_list = []
    global core_list
    core_list = getCoreListByExecMode(mode)
    images_list = images_list + list(set(getCoreImages()))
    
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

def getElastestCoreImagesByExecMode(mode, without_tag):
    images_list = getAllCoreImagesByExecMode(mode)

    elastest_images = []
    for image in images_list:
        if(image.startswith(et_image_name_prefix)):
            if(without_tag):
                image_splited = image.split(':')
                elastest_images.append(image_splited[0])
            else:
                elastest_images.append(image)
    return elastest_images

def getElasTestCoreImagesAsString(mode):
    images_list = getElastestCoreImagesByExecMode(mode, False)    
    return ",".join(map(str,images_list))


def getPreloadedImages(elastest_images):    
    images_list = []
    for image_to_pulling in images_to_pre_pulling:
        for et_image in elastest_images:
            if image_to_pulling in et_image:
                images_list.append(et_image)
                break

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

def pullPreloadImages(elastest_images):
    images_list = getPreloadedImages(elastest_images)
    for image in images_list:       
        if (not existsLocalImage(image)):            
            pullImage(image)
