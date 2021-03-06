#!/usr/bin/python3
import os
import shlex, subprocess
import time
import urllib2
import socket
import sys
sys.path.append('../version-scripts')
import argparse
from DockerUtils import *

projectName = 'elastest'
etNetwork = projectName + "_elastest"
component = 'etm'
etmContainerName = projectName + '_' + component + '_1'
etmPort = '8091'

proxyContainerName = projectName + '_' + component + '-proxy_1'
proxyPort = '37000'

etprintEnabled = True
args = []

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING_SOLID = '\033[33m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

elastestGoogleGroupsUrl = 'https://groups.google.com/forum/#!forum/elastest-users'


# Input Arguments
def getArgs(params):
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--container', '-c', help='Sets timeout in seconds for wait to the ETM container creation. Usage: --container=800', required=False)
    parser.add_argument(
        '--running', '-r', help='Sets timeout in seconds for wait to ETM is running. Usage: --running=800')

    # Custom usage message
    usage = parser.format_usage()
    usage = usage.replace(
        "usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform wait")
    parser.usage = usage

    args = parser.parse_args(params)
    return args

# ################################### #
# ######## Generic functions ######## #
# ################################### #

# Custom print function


def etprint(msg):
    if(etprintEnabled):
        print(msg)


def checkWorking(url):
    working = False
    req = urllib2.Request(url)
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e1:
        return working
    except urllib2.URLError as e2:
        return working
    except KeyboardInterrupt:  # Hide error on SIGINT
        exit(0)
    else:
        # 200
        working = True
    return working


def waitForUrl(url, waitMsg, readyMsg):
    wait = True
    if(waitMsg):
        sys.stdout.write(waitMsg)
    while (wait):
        wait = not checkWorking(url)
        if(waitMsg):
            sys.stdout.write('.')
        time.sleep(1)
    if(waitMsg):
        print('')
    if(readyMsg):
        print(readyMsg)


# #################################### #
# ######## Elastest functions ######## #
# #################################### #


def getETMIp():
    try:
        return getContainerIp(etmContainerName, etNetwork)
    except subprocess.CalledProcessError:
        raise Exception('Could not get the ip')


def getProxyIp():
    try:
        return getContainerIp(proxyContainerName, etNetwork)
    except subprocess.CalledProcessError:
        raise Exception('Could not get the ip')


def etmContainerIp():
    ip = ''
    wait = True
    timeout = 800  # seconds
    if(args.container):
        timeout = args.container
    start_time = time.time()
    # your code
    while (wait):
        try:
            ip = getETMIp()
            wait = False
        except subprocess.CalledProcessError:
            pass
        except KeyboardInterrupt:  # Hide error on SIGINT
            exit(0)
        except Exception as error:
            pass
        if(float(time.time() - start_time) >= float(timeout)):
            etprint(FAIL + 'Timeout: container ' +
                    etmContainerName + ' not created' + ENDC)
            exit(1)
    return ip


def getEtmUrl():
    # Insert platform into network
    insertPlatformIntoNetwork()
    try:
        ip = getETMIp()
        url = 'http://' + ip + ':' + etmPort
        return url
    except subprocess.CalledProcessError:
        pass
    except KeyboardInterrupt:  # Hide error on SIGINT
        pass
    except Exception as error:
        raise Exception('Could not get the url')
    return ''


def insertPlatformIntoNetwork():
    try:
        backslashStr = '\\'
        doubleBackslash = backslashStr + backslashStr
        id = getContainerId()
        if(id == ''):
            return ''

        commandTwo = 'docker network connect ' + projectName + '_elastest ' + id
        result = subprocess.call(shlex.split(commandTwo))
        if(result > 0):
            etprint(FAIL + 'Error: Unable to register Platform on the network' + ENDC)
            exit(1)
    except subprocess.CalledProcessError:
        pass
    except KeyboardInterrupt:  # Hide error on SIGINT
        exit(0)


# Main function
def runCheckETM(params=[], printEnabled=True, proxy=False, server_address=''):
    global args
    args = getArgs(params)
    global etprintEnabled
    etprintEnabled = printEnabled

    etprint('')
    etprint('ElasTest services are starting. This will likely take some time. The ElasTest URL will be shown when ready.')
    etprint('')

    # Wait for ETM container created and
    # Get ETM container IP
    etmIP = etmContainerIp()

    # Get ETM Url
    try:
        url = getEtmUrl()
    except Exception as error:
        print(error)
        exit(1)

    final_url = url

    # Check if service is started and running
    wait = True
    working = False
    message_counter = 1

    timeout = 800  # seconds
    if(args.running):
        timeout = args.running
    start_time = time.time()
    while (wait):
        # If ETM container is exited, throw error
        etmIsNotExited = containerExistsAndIsNotExited(etmContainerName)

        if(not etmIsNotExited):

            errorRelativeFilePath = '/etmExited.log'
            errorHostPath = os.environ['ET_DATA_IN_HOST'] + \
                os.environ['ET_LOGS_RELATIVE_FOLDER_PATH'] + \
                errorRelativeFilePath
            errorContainerPath = os.environ['ET_DATA_IN_CONTAINER'] + \
                os.environ['ET_LOGS_RELATIVE_FOLDER_PATH'] + \
                errorRelativeFilePath
            etprint(FAIL + 'ERROR: ElasTest main service container (' +
                    etmContainerName + ') is Stopped or Exited' + ENDC)

            writed = writeContainerLogsToFile(
                etmContainerName, errorContainerPath)
            if(writed):
                etprint(
                    OKGREEN + 'An error file has been generated in ' + errorHostPath + ENDC)

            etprint(OKGREEN + 'Please, report the problem to us at ' +
                    elastestGoogleGroupsUrl + ENDC)

            return 1
        working = checkWorking(url)
        if (working):
            wait = False
        else:
            if (message_counter == 1):
                message_counter = 0
            if(float(time.time() - start_time) >= float(timeout)):
                etprint('Timeout: container ' +
                        etmContainerName + ' not started')
                wait = False

    if (working):
        # Get final ETM URL if is proxy and/or server_address
        if (server_address != ''):
            final_url = 'http://' + server_address + ':' + proxyPort
        elif(proxy):
            try:
                #proxy_ip = getProxyIp()
                proxy_ip = 'localhost'
                final_url = 'http://' + proxy_ip + ':' + proxyPort
            except Exception:
                etprint('ERROR: Proxy is not started')
                exit(1)

        etprint('')
        etprint(WARNING + 'ElasTest Platform is available at ' + final_url + ENDC)
        etprint('')

        # If host OS is Windows, show stop command instead of Ctrl+C
        if(hostOSIsWindows()):
            platform_version = getVersionFromHostContainer()
            etprint(OKGREEN + 'Run "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform:' +
                    platform_version + ' stop" to stop.' + ENDC)
        else:
            etprint(OKGREEN + 'Press Ctrl+C to stop.' + ENDC)
        return 0
    else:
        etprint(FAIL + 'ERROR: ElasTest Platform not started correctly' + ENDC)
        return 1
