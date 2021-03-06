#!/usr/bin/python3
import subprocess
import shlex
import time
import sys
import os
import socket

pull_command = 'pull-images'
STDOUT = subprocess.STDOUT
FNULL = open(os.devnull, 'w')


def pullImage(image):
    pull = 'docker pull '
    pull_result = subprocess.call(shlex.split(pull + image))

    if(pull_result > 0):
        print('Error on pull image ' + image)
        exit(1)


def tagImage(image, tag):
    new_tagged = ''
    if ':' in image:
        new_tagged = image.split(':')[0] + ':' + tag
    else:
        new_tagged = image + ':' + tag

    tag_command = 'docker tag ' + image + ' ' + new_tagged
    tag_result = subprocess.call(shlex.split(tag_command))

    if(tag_result > 0):
        print('Error on tag image ' + new_tagged)
        exit(1)
    return new_tagged


def pushImage(image):
    push = 'docker push '
    push_result = subprocess.call(shlex.split(push + image))

    if(push_result > 0):
        print('Error on push image ' + image)
        exit(1)


def getBindingVolumes():
    command = 'docker inspect --format "{{ range .HostConfig.Binds }}{{.}}|{{end}}" ' + \
        os.environ['HOSTNAME']
    bindingVolumes = str(subprocess.check_output(
        shlex.split(command))).rstrip('\n')

    return bindingVolumes


def getContainerImage():
    command = 'docker inspect --format "{{ index .Config.Image }}" ' + \
        os.environ['HOSTNAME']
    image = str(subprocess.check_output(shlex.split(command))).rstrip('\n')
    return image


def getContainerId():
    return os.environ['HOSTNAME']


def getVersionFromHostContainer():
    command = 'docker inspect --format "{{ index .Config.Labels.version }}" ' + \
        os.environ['HOSTNAME']
    version = str(subprocess.check_output(shlex.split(command))).rstrip('\n')
    return version


def getRepoTag(imageTag):
    command = 'docker inspect %s --format "{{index .RepoTags}}"' % (imageTag)
    repoTag = ''
    try:
        repoTag = ''.join(subprocess.check_output(shlex.split(command)))
    except (TypeError, subprocess.CalledProcessError) as e:
        repoTag = 'imageNotExists'
    return repoTag


def getLocalImages():
    command = 'docker images --format "{{.Repository}}:{{.Tag}}"'
    local_images = []
    try:
        local_images = subprocess.check_output(
            shlex.split(command)).splitlines()
    except (TypeError, subprocess.CalledProcessError) as e:
        print('Error getting docker images: {}'.format(e))
    return local_images


def deleteVolume(name):
    print('')
    print(' Deleting some volumes....')
    command = 'docker volume rm ' + name
    subprocess.call(shlex.split(command))


def deleteImages(images):
    if (images):
        command = 'docker rmi -f ' + images
        subprocess.call(shlex.split(command), stderr=STDOUT, stdout=FNULL)


def deleteDanglingImages():
    subcommand = 'docker images -f "dangling=true" -q'
    result = str(subprocess.check_output(shlex.split(subcommand))).split('\n')
    if (''.join(result)):
        command = 'docker rmi -f ' + ' '.join(result)
        print('Deleting dangling images')
        try:
            subprocess.check_output(shlex.split(command))
        except subprocess.CalledProcessError:
            print(' Unable to delete dangling images.')


def killContainer(container, signal):
    if (signal is None or signal == ''):
        command = 'docker kill %s ' % (container)
    else:
        command = 'docker kill --signal=%s %s ' % (signal, container)

    p = subprocess.check_output(shlex.split(command))
    return p


def executePlatformCommand(image, command, dockerArgs, commandArgs):
    if (command == pull_command):
        print('')
        print(' Updating ElasTest components....')
        print('')
        command_line = ('docker run %s --rm -v /var/run/docker.sock:/var/run/docker.sock %s %s %s') % (
            dockerArgs, image, command, commandArgs)

    subprocess.call(shlex.split(command_line), stderr=STDOUT, stdout=FNULL)


def existsLocalImage(image):
    if(':' not in image):
        image + ':latest'
    return True if image in getLocalImages() else False


def containerExists(containerId):
    exists = False
    command = [
        'docker ps -a --format "{{.Names}}" | grep -E "^' + containerId + '$"']
    try:
        containerName = subprocess.check_output(
            command, shell=True).split("\n")[0]
        if(not containerName is None and containerName != ''):
            exists = True
    except TypeError:
        exists = False
    except subprocess.CalledProcessError:
        exists = False

    return exists


def containerExistsAndIsNotExited(containerId):
    if(not containerExists(containerId)):
        return False

    notExited = True
    command = 'docker container inspect -f "{{.State.ExitCode}}" ' + containerId
    try:
        exitCode = subprocess.check_output(shlex.split(command)).split("\n")[0]
        if(exitCode != '0'):
            notExited = False
    except TypeError:
        notExited = False
    except subprocess.CalledProcessError:
        notExited = False

    return notExited


def writeContainerLogsToFile(containerId, completeFilePath):
    if(not containerExists(containerId)):
        return False

    writed = True
    command = 'docker logs ' + containerId + ' >& ' + completeFilePath
    try:
        exitCode = subprocess.call(command, shell=True)
        if(exitCode != 0):
            writed = False
    except TypeError:
        writed = False
    except subprocess.CalledProcessError:
        writed = False

    return writed


def getWinHostMachineIp():
    return getIpFromTraceRoute('docker.for.win.localhost')


def getMacHostMachineIp():
    return getIpFromTraceRoute('docker.for.mac.localhost')


def getHostMachineIp():
    return getIpFromTraceRoute('host.docker.internal')


def getIpFromTraceRoute(dns):
    ip = None
    try:
        ip = socket.gethostbyname(dns)
    except socket.error:
        ip = None
    return ip


def getHostOS():
    if(not getWinHostMachineIp() is None):
        return 'Windows'
    elif(not getMacHostMachineIp() is None):
        return 'Mac'
    else:
        return 'Other'


def hostOSIsWindows():
    return getHostOS() == 'Windows'


def hostOSIsMac():
    return getHostOS() == 'Mac'


def hostOSIsOther():
    return getHostOS() == 'Other'


def getContainerIp(containerName, network):
    command = "docker inspect --format=\"{{.NetworkSettings.Networks." + network + ".IPAddress}}\" "+ containerName
    try:
        ip = subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE)
        # remove /n
        ip = ip.rstrip()
        return ip
    except subprocess.CalledProcessError:    
            raise Exception('Could not get the ip')