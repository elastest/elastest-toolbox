#!/usr/bin/python3

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

core_list = [emp, edm, esm, eim, epm, etm_complementary_normal, etm_main_normal, etm_complementary_lite, etm_main_lite]

# ET TSS JSON FILES (EUS, EBS, ESS, EDS, EMS)
eus = '../eus/elastestservice.json'
ebs = '../ebs/elastestservice.json'
ess = '../ess/elastestservice.json'
eds = '../eds/elastestservice.json'
ems = '../ems/elastestservice.json'

tss_list = [eus, ebs, ess, eds, ems]

# ET Test Engines DOCKER COMPOSE FILES (ECE and ERE)
ece = '../etm/elastest-torm/src/main/resources/test_engines/ece.yml'
ere = '../etm/elastest-torm/src/main/resources/test_engines/ere.yml'

engines_list = [ece, ere]


def getCoreList():
	return core_list

def getTSSList():
	return tss_list

def getEnginesList():
	return engines_list
