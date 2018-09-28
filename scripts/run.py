#!/usr/bin/python3 -u
import sys
sys.path.append('../version-scripts')
from ETImages import *
import shlex
import subprocess
import argparse
import os
import threading
import requests
from checkETM import *
from setEnv import *
from DockerUtils import *
from update import *
from pull import *
from stringUtils import *
from ETFiles import *
from messages import *

outputMessages={'update': 'Updating ElasTest Platform version ', 'pull-images': 'Pulling the ElasTest Platform Images '}
def getArgs(params):
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Platform command to execute: start or stop',
                        type=str, choices=set(('start', 'stop', 'update', 'pull-images')))
    parser.add_argument('--mode', '-m', help='Set ElasTest execution mode. Usage: --mode=experimental',
                        type=str, choices=set(('normal', 'experimental-lite', 'experimental')), default='normal')
    parser.add_argument('--dev', '-d', help='Configure ElasTest for development.', required=False, action='store_true')
    parser.add_argument('--pullall', '-pa', help='Force pull of all images. Usage: --pullall',
                        required=False, action='store_true')
    parser.add_argument('--pullcore', '-pc', help='Force pull of only necessary images. Usage: --pullcore',
                        required=False, action='store_true')
    parser.add_argument('--noports', '-np', help='Unbind all ports. Usage: --noports',
                        required=False, action='store_true')
    parser.add_argument('--logs', '-l', help='Show logs of all containers. Usage: --logs',
                        required=False, action='store_true')
    parser.add_argument('--server-address', '-sa',
                        help='Set server address Env Var. Usage: --server-address=XXXXXX', required=False)
    parser.add_argument('--shared-folder', '-sf',
                        required=False, help=argparse.SUPPRESS)
    parser.add_argument(
        '--user', '-u', help='Set the user to access ElasTest. Use together --password. Usage: --user=testuser', required=False)
    parser.add_argument(
        '--password', '-p', help='Set the user password to access ElasTest. Use together --user. Usage: --password=passuser', required=False)
    parser.add_argument('--testlink', '-tl', help='Start the TestLink Tool integrated with ElasTest. Usage: --testlink',
                        required=False, action='store_true')
    parser.add_argument('--jenkins', '-jk', help='Start the Jenkins Tool integrated with ElasTest. Usage: --jenkins',
                        required=False, action='store_true')                        
    parser.add_argument('--internet-disabled', '-id',
                        help='Set if internet is disabled. Usage: --internet-disabled', required=False, action='store_true')
    parser.add_argument('--master-slave', '-ms',
                        help='If you enable the master-slave mode, the TJobs will be run in a remote VM (slave). Usage: --master-slave', required=False, action='store_true')

    # Custom usage message
    usage = parser.format_usage()
    usage = usage.replace(
        "usage: main.py", "docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform start")
    parser.usage = usage

    args = parser.parse_args(params)

    # If there aren't args, show help and exit
    if len(params) == 0:
            parser.print_help()
            sys.exit(1)

    if ((args.user and not args.password) or (not args.user and args.password)):
        print 'To enable basic authentication you must specify user and password'
        print ''
        parser.print_help()
        os._exit(1)

    return args


def runPlatform(params):
    args = getArgs(params)
    dockerCommand = []
    with_security = False

    command = args.command  # start, stop, update or pull-images
    mode = args.mode
    platform_version = getVersionFromHostContainer()
   
    # ETM docker-compose files
    etmDockerComposeMainFromDocker = '../etm/docker/docker-compose-main.yml'
    etmDockerComposeMainFromDeploy = '../etm/deploy/docker-compose-main.yml'

    if(command == 'update' or command == 'pull-images'):
        message = outputMessages[command] + '...'
        print message

        if(command == 'update'):            
            updatePlatform(params[1:])
        if(command == 'pull-images'):
            pullETImages(params[1:])

    else:
        if(args.server_address):
            #setServerAddress(args.server_address)
            files_list = []
            files_list.append(etmDockerComposeMainFromDeploy)
            files_list.append(etmDockerComposeMainFromDocker)
            replaceEnvVarValue('ET_PUBLIC_HOST', args.server_address,
                               'localhost', files_list)
            replaceEnvVarValue('ET_PUBLIC_HOST_TYPE', "server_address",
                               'default', files_list)
            #set the new Jenkins location
            files_list = []
            files_list.append('../etm/docker/docker-compose-jenkins.yml')
            jenkinsPort = getKeyFromYmlMapEntry(getLineByContent(
                '8080', '../etm/docker/docker-compose-jenkins.yml'))
            replaceEnvVarValue('JENKINS_LOCATION', 'http://' +
                               args.server_address + ':' + jenkinsPort, 'none', files_list)
                
        # Config the ElasTest home
        if (command == 'start'):
            bindingVolumes = getBindingVolumes().split('|')
            for bindingVolume in bindingVolumes:
                if (not bindingVolume == '' and '/data' == bindingVolume.split(':')[1]):
                    os.environ['ET_DATA_IN_HOST'] = bindingVolume.split(':')[0]
                    os.environ['ET_DATA_IN_CONTAINER'] = bindingVolume.split(':')[1]

            if (not 'ET_DATA_IN_HOST' in os.environ):
                printMsg('elastest_home_error')
                os._exit(1)
        
        # Set credentials
        randomPass = createPassword(8,8)
        integratedAppUser = "none"
        integratedAppPass = "none"
        configPad = os.environ['ET_DATA_IN_CONTAINER'] + '/config'
        credentialsFilePath = configPad + '/credentials'
        if not checkIfDirExists(configPad):
            createDir(configPad)        
        if (checkIfFileExists(credentialsFilePath)):
            credentials = readFileByLines(credentialsFilePath, 1)[0].split(',')
            integratedAppUser = credentials[0]
            integratedAppPass = credentials[1]
        else:
            if (args.user and args.password):
                integratedAppUser = args.user
                integratedAppPass = args.password            
            else:
                integratedAppUser = 'elastest'
                integratedAppPass = randomPass
            
            writeFile(credentialsFilePath, integratedAppUser + ',' + integratedAppPass)

        
        files_list = []
        files_list.append('../etm/deploy/docker-compose-main.yml')
        files_list.append('../etm/docker/docker-compose-main.yml')
        files_list.append('../etm/docker/docker-compose-jenkins.yml')
        replaceEnvVarValue('ET_USER', integratedAppUser, 'none', files_list)
        replaceEnvVarValue('ET_PASS', integratedAppPass, 'none', files_list)

        files_list = []
        files_list.append('../etm/docker/docker-compose-testlink.yml')
        replaceEnvVarValue('TESTLINK_USERNAME', integratedAppUser, 'none', files_list)
        replaceEnvVarValue('TESTLINK_PASSWORD', integratedAppPass, 'none', files_list)

       
        # Proxy env variables   
        files_list = []
        files_list.append('../etm/docker/docker-compose-proxy.yml')        
        if (args.user and args.password):
            with_security = True
            replaceEnvVarValue('ET_SECURITY', 'true' , 'false', files_list)
            replaceEnvVarValue('ET_USER', args.user, 'none', files_list)
            replaceEnvVarValue('ET_PASS', args.password, 'none', files_list)
        
        if (mode == 'experimental'):
            if(args.dev):
                replaceEnvVarValue('LOCATION_RULES', 'nginx-dev-experimental-locations.conf', 'nginx-base-location.conf', files_list)
            else:
                replaceEnvVarValue('LOCATION_RULES', 'nginx-experimental-locations.conf', 'nginx-base-location.conf', files_list)
        
        if(mode == 'normal' or mode == 'experimental-lite'):
            replaceEnvVarValue('LOGSTASH_HOST', 'etm', 'etm-logstash', files_list)
            replaceEnvVarValue('LOGSTASH_HTTP_PATH', '/api/monitoring/', '/', files_list)
      
        if(args.logs == True):
            FNULL = subprocess.STDOUT
            instruction = ' up'
        else:
            FNULL = open(os.devnull, 'w')
            instruction = ' up -d'
   

        message = ''

        etm_proxy = '-f ../etm/docker/docker-compose-proxy.yml'
        etm_proxy_env = '-f ../etm/docker/docker-compose-proxy-env.yml'
        emp = '-f ../emp/deploy/docker-compose.yml'        
        edm = '-f ../edm/deploy/docker-compose.yml'
        esm = '-f ../esm/deploy/docker-compose.yml'
        eim = '-f ../eim/deploy/docker-compose.yml'
        epm = '-f ../epm/deploy/docker-compose.yml'
        epm_ansible_adapter = '-f ../epm/deploy/docker-compose-ansible-adapter.yml'
        etm_tlink = '-f ../etm/docker/docker-compose-testlink.yml'
        etm_tlink_ports = '-f ../etm/docker/docker-compose-testlink-ports.yml'
        etm_jenkins = '-f ../etm/docker/docker-compose-jenkins.yml'
        etm_jenkins_ports = '-f ../etm/docker/docker-compose-jenkins-ports.yml'
        mysql_elasticsearch_lite = '-f ../docker-compose-mysql-elasticsearch-lite.yml'


        platform_services = '-f ../platform-services/docker-compose.yml'

        etm_complementary = '-f ../etm/deploy/docker-compose-complementary.yml'
        etm_main = '-f ../etm/deploy/docker-compose-main.yml'
        etm = etm_complementary + ' ' + etm_main

        # If is Experimental mode
        files_list = []
        if(mode == 'experimental'):            
            dockerCommand = 'docker-compose ' + platform_services + ' ' + edm + ' ' + etm + ' ' + esm + ' ' + eim + \
                            ' ' +  etm_proxy + ' ' + etm_tlink + ' ' + etm_tlink_ports + \
                            ' ' + etm_jenkins + ' ' + etm_jenkins_ports + ' '
            # If dev mode, no start epm and emp
            if(not args.dev):
                dockerCommand = dockerCommand + epm + ' ' + emp + ' '


            #Replace emp env variables
            et_host = "localhost"
            if(args.server_address):
                et_host = args.server_address
                files_list.append('../epm/deploy/docker-compose.yml')
                replaceEnvVarValue('ET_PUBLIC_HOST', args.server_address,
                            'localhost', files_list)
            files_list = []
            files_list.append('../emp/deploy/docker-compose.yml')
            replaceEnvVarValue('GF_SERVER_DOMAIN', et_host , 'nightly.elastest.io:37000', files_list)
                                 
            message = 'Starting ElasTest Platform ' + platform_version + ' (' + mode + ' Mode)...'

            if(args.master_slave):
                files_list = []
                files_list.append(etmDockerComposeMainFromDeploy)
                replaceEnvVarValue('ET_MASTER_SLAVE_MODE', 'true',
                            'false', files_list)
                #dockerCommand = dockerCommand + ' ' + epm_ansible_adapter + ' '
        #If is Experimental-lite or Normal mode
        else:
            #Change the default execution mode
            files_list.append(etmDockerComposeMainFromDocker)
            replaceEnvVarValue('EXEC_MODE', args.mode, 'normal', files_list)

            #Initially do not bind ports
            etm_complementary_ports = '-f ../etm/docker/docker-compose-complementary-ports.yml'
            etm_main_ports = ''

            # etm root path docker-compose files:
            etm_complementary = '-f ../etm/docker/docker-compose-complementary.yml'            
            etm_main = '-f ../etm/docker/docker-compose-main.yml'
            
            if(args.dev):                
                print ''
                print 'Dev options activated.'
                print 'Binding ports.'
                etm_complementary_ports = '-f ../etm/docker/docker-compose-complementary-dev-ports.yml'
                etm_main_ports = '-f ../etm/docker/docker-compose-main-ports.yml'

            etm = etm_complementary + ' ' + etm_complementary_ports + ' ' + etm_main + ' ' + etm_main_ports
                    
            dockerCommand = 'docker-compose ' + platform_services + ' ' + etm + ' ' + \
                etm_proxy + ' '
            message = 'Starting ElasTest Platform ' + platform_version + ' (' + mode + ' mode)...'

            # If the testlink option is used, add the docker-compose file of the Testlink tool
            if(args.testlink):
                dockerCommand = dockerCommand + ' ' + etm_tlink + ' ' + etm_tlink_ports
            else:
                files_list = []
                files_list.append(etmDockerComposeMainFromDeploy)
                files_list.append(etmDockerComposeMainFromDocker)
                replaceEnvVarValue('ET_ETM_TESTLINK_HOST', 'none',
                                'etm-testlink', files_list)


            # If the jenkins option is used, add the docker-compose file of the Jenkins tool
            if(args.jenkins):
                dockerCommand = dockerCommand + ' ' + etm_jenkins + ' ' + etm_jenkins_ports
            else:
                files_list = []
                files_list.append(etmDockerComposeMainFromDeploy)
                files_list.append(etmDockerComposeMainFromDocker)
                replaceEnvVarValue('ET_ETM_JENKINS_HOST', 'none',
                                'etm-jenkins', files_list)                                
        
        # Add the project name to the docker-compose command
        dockerCommand = dockerCommand + ' -p elastest'

        elastest_images = getElasTestImagesAsString(mode)
        elastest_core_images = getElasTestCoreImagesAsString(mode)
        files_list = []
        files_list.append(etmDockerComposeMainFromDeploy)
        files_list.append(etmDockerComposeMainFromDocker)
        replaceEnvVarValue('ET_IMAGES', elastest_images,
                        'elastest/platform', files_list)
        replaceEnvVarValue('ET_CORE_IMAGES', elastest_core_images, 'elastest/platform', files_list)


        # Get timezone and set it to ETM
        timezone='UTC'
        response = requests.get('http://ip-api.com/line?fields=timezone')
        if(response.status_code == requests.codes.ok):
            timezone = response.text
        else:
            # Re-try with other url (This has Max 50 requests/day restriction)
            response = requests.get('https://timezoneapi.io/api/ip')
            if(response.status_code == requests.codes.ok):    
                timezoneRequestData = response.json()
                if(timezoneRequestData['meta']['code'] == '200'):
                    timezone =  timezoneRequestData['data']['timezone']['id']

        print 'Timezone: ' + timezone
        replaceEnvVarValue('HOST_TIMEZONE', timezone,
                    'UTC', files_list)

        # If internet is disabled
        if(args.internet_disabled):
            replaceEnvVarValue('ET_INTERNET_DISABLED', 'true', 'false', files_list)

        # If command=stop
        if(command == 'stop'):
            instruction = ' down --timeout 90'
            message = 'Stopping ElasTest Platform (' + mode + ' mode)...'

        if(len(dockerCommand) > 0):
            # If Force pull or pull necessary images, do pull for each image
            if(command != 'stop'):
                print 'Pulling some necessary images...'
                print ''
                pullPreloadImages(elastest_images)
                print 'Preload images finished.'

                if(args.pullall):
                    print 'Pulling the ElasTest images...'
                    print ''
                    pullAllImages()
                elif(args.pullcore):
                    print 'Pulling the ElasTest core images...'
                    print ''
                    try:
                        subprocess.call(shlex.split(dockerCommand + ' pull'))
                    except KeyboardInterrupt:  # Hide error on SIGINT
                        exit(1)

            dockerCommand = dockerCommand + instruction
            print ''
            print message
            print ''

            # Run docker-compose up/down
            try:
                if(args.logs and command == 'start'):
                    # If print logs, run in bg
                    subprocess.Popen(shlex.split(dockerCommand), stderr=FNULL)
                else:
                    result = subprocess.call(shlex.split(dockerCommand), stderr=FNULL)
                    if(result == 0 and command == 'start'):
                        check_params = [[], True]
                        # Set proxy value to True
                        check_params.append(True)
                        if(args.server_address):
                            check_params.append(args.server_address)

                        # Run check ETM in bg
                        check_thread = threading.Thread(target=runCheckETM, args=check_params)
                        check_thread.daemon = True
                        check_thread.start()
                return 0
            except KeyboardInterrupt:  # Hide error on SIGINT
                pass
            except subprocess.CalledProcessError:
                return 1
