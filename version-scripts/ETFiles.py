#!/usr/bin/python3
import yaml
import json

# ET CORE DOCKER COMPOSE FILES (ETM, EDM, EIM, ESM, EMP and EPM)
emp = '../emp/deploy/docker-compose.yml'
edm = '../edm/deploy/docker-compose.yml'
esm = '../esm/deploy/docker-compose.yml'
eim = '../eim/deploy/docker-compose.yml'
epm = '../epm/deploy/docker-compose.yml'

etm_complementary_experimental = '../etm/deploy/docker-compose-complementary.yml'
etm_main_experimental = '../etm/deploy/docker-compose-main.yml'
platform_services = '../platform-services/docker-compose.yml'

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
eus_browsers_properties_file = '../eus/src/main/resources/docker-browser.properties'
eus_properties_file = '../eus/src/main/resources/application.properties'
etm_properties_file = '../etm/elastest-torm/src/main/resources/application.properties'

# Images to pull at the start
imagesFilesToPrePull = {'eusBrowsers': eus_browsers_properties_file,
                        'eusNovnc': eus_properties_file, 'etmSocat': etm_properties_file,
                        'eus': eus}


def getCoreList():
    core_list = [emp, edm, esm, eim, epm, etm_complementary_experimental,
                 etm_main_experimental, etm_complementary_lite, etm_main_lite, etm_proxy]
    return core_list


def getCoreListByExecMode(mode):
    if (mode == 'normal' or mode == 'experimental-lite'):
        core_list = [esm, etm_complementary_lite, etm_main_lite, etm_proxy, platform_services]
    else:
        core_list = [emp, edm, esm, eim, epm, etm_complementary_experimental,
                     etm_main_experimental, etm_proxy, platform_services]
    return core_list


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
