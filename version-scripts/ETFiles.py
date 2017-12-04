#!/usr/bin/python3
import yaml
import json

# ET CORE DOCKER COMPOSE FILES (ETM, EDM, EIM, ESM, EMP and EPM)
emp = '../emp/deploy/docker-compose.yml'
edm = '../edm/deploy/docker-compose.yml'
esm = '../esm/deploy/docker-compose.yml'
eim = '../eim/deploy/docker-compose.yml'
epm = '../epm/deploy/docker-compose.yml'

etm_complementary_normal = '../etm/deploy/docker-compose-complementary.yml'
etm_main_normal = '../etm/deploy/docker-compose-main.yml'

etm_complementary_lite = '../etm/docker/docker-compose-complementary.yml'
etm_main_lite = '../etm/docker/docker-compose-main.yml'

etm_proxy = '../etm/docker/docker-compose-proxy.yml'

# ET TSS JSON FILES (EUS, EBS, ESS, EDS, EMS)
eus = '../eus/elastestservice.json'
ebs = '../ebs/elastestservice.json'
ess = '../ess/elastestservice.json'
eds = '../eds/elastestservice.json'
ems = '../ems/elastestservice.json'

# ET Test Engines DOCKER COMPOSE FILES (ECE and ERE)
ece = '../etm/elastest-torm/src/main/resources/test_engines/ece.yml'
ere = '../etm/elastest-torm/src/main/resources/test_engines/ere.yml'

# EUS Browsers file
eus_browsers = '../eus/browsers/docker-browser.properties'
eus_properties = '../eus/application.properties'
etm_properties = '../etm/application.properties'

eus_browsers_properties_file = '../eus/browsers/docker-browser.properties'
eus_properties_file = '../eus/application.properties'
etm_properties_file = '../etm/application.properties'

# Images to pull at the start
imagesFilesToPrePull = {'eusBrowsers': eus_browsers_properties_file, 
'eusNovnc': eus_properties_file, 'etmSocat': etm_properties_file,
'eus': eus}


def getCoreList():
    core_list = [emp, edm, esm, eim, epm, etm_complementary_normal,
                 etm_main_normal, etm_complementary_lite, etm_main_lite, etm_proxy]
    return core_list


def getTSSList():
    tss_list = [eus, ebs, ess, eds, ems]
    return tss_list


def getEnginesList():
    engines_list = [ece, ere]
    return engines_list

def getBrowsers():
    return eus_browsers

def getFilePathByServiceName(service_name):
    path = ''
    if service_name == 'EUS':        
        path = eus
    return path
    

# Yaml
def getYml(path):
    with open(path, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            return yaml.load('')


def saveYml(path, yml):
    with open(path, 'w') as outfile:
        yaml.dump(yml, outfile, default_flow_style=False)


# Json

def getJson(path):
    with open(path, 'r') as stream:
        data = json.load(stream)
        return data
    return json.load('')


def saveJson(path, json_file):
    with open(path, 'w') as outfile:
        # json.dump(json_file, outfile)
        json.dump(json_file, outfile, sort_keys=True,
                  indent=4, separators=(',', ': '))

def getFilePathByImage(imageToPull):
    return imagesFilesToPrePull[imageToPull]    

# Properties
def getProperties(properties_type):    
    properties = {}
    if properties_type == 'browsers':
        properties = getPropertiesFromFile(eus_browsers)
    elif properties_type == 'novnc':
        properties = getPropertiesFromFile(eus_properties)
    elif properties_type == 'socat':
        properties = getPropertiesFromFile(etm_properties)
    else:
        print 'There are not properties for the ' + properties + ' key.'
    
    return properties

def getPropertiesFromFile(path):    
    separator = "="
    keys = {}
    
    with open(path) as f:
        for line in f:
            if separator in line:                
                name, value = line.split(separator, 1)
                keys[name.strip()] = value.strip()
        
    return keys;