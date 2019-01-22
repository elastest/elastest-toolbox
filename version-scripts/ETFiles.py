#!/usr/bin/python3
import yaml
import json
import fileinput
import os

# ET CORE DOCKER COMPOSE FILES (ETM, EDM, EIM, ESM, EMP and EPM)
emp = '../emp/deploy/docker-compose.yml'
edm = '../edm/deploy/docker-compose.yml'
edm_lite = '../edm/deploy/docker-compose-lite.yml'
esm = '../esm/deploy/docker-compose.yml'
eim = '../eim/deploy/docker-compose.yml'
epm = '../epm/deploy/docker-compose.yml'

etm_complementary_experimental = '../etm/deploy/docker-compose-complementary.yml'
etm_main_experimental = '../etm/deploy/docker-compose-main.yml'
platform_services = '../platform-services/docker-compose.yml'

etm_complementary_lite = '../etm/docker/docker-compose-complementary.yml'
mysql_elasticsearch_lite = '../docker-compose-mysql-elasticsearch-lite.yml'
etm_main_lite = '../etm/docker/docker-compose-main.yml'
etm_eim = '../etm/docker/docker-compose-eim.yml'

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
eus_browsers_properties_file = '../eus/browsers/docker-browser.properties'
eus_properties_file = '../eus/application.properties'
etm_properties_file = '../etm/application.properties'

# Images to pull at the start
imagesFilesToPrePull = {'eusBrowsers': eus_browsers_properties_file,
                        'etmSocat': etm_properties_file,
                        'eus': eus}

tss_images_files = {'eus': eus, 'ebs': ebs, 'ess': ess, 'eds': eds, 'ems': ems}


def getCoreList():
    core_list = [emp, edm_lite, esm, eim, epm, etm_complementary_experimental, platform_services,
                 etm_main_experimental, etm_complementary_lite, etm_main_lite, etm_proxy]
    return core_list


def getCoreListByExecMode(mode):
    # Normal or experimental-lite
    if (mode == 'normal' or mode == 'experimental-lite'):
        core_list = [etm_complementary_lite,
                     etm_main_lite, etm_proxy, platform_services]
    # Experimental
    else:
        core_list = [emp, edm_lite, esm, eim, epm, etm_complementary_experimental,
                     etm_main_experimental, etm_proxy, platform_services]
    return core_list


def getTSSFile(tss):
    return tss_images_files[tss]


def getTSSList():
    tss_list = [eus, ebs, ess, eds, ems]
    return tss_list


def getEnginesList():
    engines_list = [ece, ere]
    return engines_list


def getFilePathByImage(imageToPull):
    return imagesFilesToPrePull[imageToPull]

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
        json.dump(json_file, outfile, indent=4, separators=(',', ': '))


def getLineByContent(content, path):
    result = ''
    for line in fileinput.input(path):
        if(content in line):
            result = line
    return result


def checkIfDirExists(path):
    return os.path.exists(path)


def createDir(path):
    os.makedirs(path)


def checkIfFileExists(path):
    return os.path.isfile(path)


def readFileByLines(path, linesToRead):
    myfile = open(path)
    with myfile:
        head = [next(myfile) for x in xrange(linesToRead)]
    myfile.close()
    return head


def writeFile(path, content):
    file = open(path, 'a')
    file.write(content + '\n')
    file.close()
