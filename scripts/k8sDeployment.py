from setEnv import *
import StringIO
import os
from ruamel.yaml import YAML
import paramiko
import certifi
import urllib3
import time
from checkETM import *
import shlex
import subprocess
from epm_client.models import *
from epm_client import ApiClient
from epm_client.apis import *
from ETFiles import *
import sys
sys.path.append('../version-scripts')

FNULL = subprocess.STDOUT

epm_service_name = "elastest-platform-manager"
epm_port = "8180"
epm_adapter_ansible_service_name = "epm-adapter-ansible"
epm_adapter_ansible_port = "50052"

ansiblePath = "/data/ansible"
epmComposeCommandPrefix = "docker-compose -f ../epm/deploy/docker-compose.yml -p "
epmComposeFilePath = "../epm/deploy/docker-compose.yml"


def startAndWaitForEpm(args, dockerComposeProject):
    if(args.dev):
        result = 0
    else:
        if(args.paas_domain):
            searchAndReplace(epmComposeFilePath, "entrypoint: python -m run --register-adapter elastest-epm elastest-epm-adapter-ansible",
                             "entrypoint: python -m run --register-adapter elastest-epm elastest-epm-adapter-ansible --register-namespace codeurjc.es")

        startEpmCommand = epmComposeCommandPrefix + \
            dockerComposeProject + " up -d"
        result = subprocess.call(shlex.split(startEpmCommand), stderr=FNULL)

    if(result == 0):
        insertPlatformIntoNetwork()

        epm_url = "http://" + epm_service_name + ":" + epm_port + "/v1"
        print('Waiting for ' + epm_url)
        waitForUrl(epm_url, 'Waiting for EPM', 'EPM is available!')

        epm_adapter_ansible_url = "http://" + \
            epm_adapter_ansible_service_name + ":" + epm_adapter_ansible_port
        waitForUrl(epm_adapter_ansible_url,
                   'Waiting for EPM adapter', 'EPM is ready now!')

        return epm_url
    else:
        print(FAIL + 'Error on start EPM' + ENDC)
        print('')
        stopEpm(args, dockerComposeProject)
        exit(1)


def stopEpm(args, dockerComposeProject):
    print('Stopping EPM...')
    if(not args.dev):
        stopEpmCommand = epmComposeCommandPrefix + \
            dockerComposeProject + " down"
        result = subprocess.call(shlex.split(stopEpmCommand), stderr=FNULL)


# def getK8sConfigFromCluster(k8s_host):
#     HOST = k8s_host
#     PUERTO = 22
#     USUARIO = 'ubuntu'
#     datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,
#                  key_filename=ansiblePath + '/key')
#     #  key_filename='/home/frdiaz/.elastest/k8s/key')  # ansiblePath + '/key')

#     ssh_client = paramiko.SSHClient()
#     ssh_client.load_system_host_keys()
#     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     # Connecting to the k8s Master
#     ssh_client.connect(**datos)
#     entrada, salida, error = ssh_client.exec_command(
#         'sudo cat /etc/kubernetes/admin.conf')
#     # Retrieve k8s client configuration from the cluster
#     admin_conf_content = salida.read()
#     print('K8s cluster configuration:', admin_conf_content)
#     # Setting the kubectl to access the cluster
#     kube_file = open('~/.kube/config', 'w')
#     kube_file.write(admin_conf_content)
#     kube_file.close()
#     ssh_client.close()


def getSshConnection(k8s_host):
    HOST = k8s_host
    PUERTO = 22
    USUARIO = 'ubuntu'
    datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,
                 key_filename=ansiblePath + '/key')
    #  key_filename='/home/frdiaz/.elastest/k8s/key')  # ansiblePath + '/key')

    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connecting to the k8s Master
    ssh_client.connect(**datos)
    return ssh_client


def closeSshConnection(ssh_client):
    if ssh_client is not None:
        ssh_client.close()


def setK8sClientConfigurarion(ssh_client):
    if ssh_client is not None:
        entrada, salida, error = ssh_client.exec_command(
            'sudo cat /etc/kubernetes/admin.conf')
        # Retrieve k8s client configuration from the cluster
        admin_conf_content = salida.read()
        print('K8s cluster configuration:', admin_conf_content)
        # Setting the kubectl to access the cluster
        kube_file = open(os.environ['HOME'] + '/.kube/config', 'w')
        kube_file.write(admin_conf_content)
        kube_file.close()


def uploadFile(file, target_path, ssh_client):
    print('Uploading file')
    entrada, salida, error = ssh_client.exec_command(
        'sudo chmod 777 /etc/kubernetes/manifests/kube-apiserver.yaml')
    ftp_client = ssh_client.open_sftp()
    ftp_client.put('kube-apiserver.yaml',
                   '/etc/kubernetes/manifests/kube-apiserver.yaml')
    ftp_client.close()
    entrada, salida, error = ssh_client.exec_command(
        'sudo chmod 600 /etc/kubernetes/manifests/kube-apiserver.yaml')


def modifyNodePortRangePort(ssh_client):
    if ssh_client is not None:
        yaml = YAML()
        entrada, salida, error = ssh_client.exec_command(
            'sudo cat /etc/kubernetes/manifests/kube-apiserver.yaml')
        cluster_api_spec_from_k8s_cluster = salida.read()
        print('Yaml as dict:', cluster_api_spec_from_k8s_cluster)
        cluster_api_spec_as_dict = yaml.load(cluster_api_spec_from_k8s_cluster)
        cluster_api_spec_as_dict['spec']['containers'][0]['command'].append(
            "--service-node-port-range=1000-40000")
        dm = StringIO.StringIO()
        yaml.dump(cluster_api_spec_as_dict, dm)
        yaml_as_string = dm.getvalue()

        print('Kube-api upadated content: ' + yaml_as_string)
        writeFile('kube-apiserver.yaml', yaml_as_string)


# # def configureNodePortPortsRange():

# def processYamlFromFile(pathFile):
#     # yamlAsString = getYml(pathFile)
#     # print('YAML as string: ', yamlAsString)
#     # print('--------------')
#     # yaml = YAML()
#     # cluster_api_spec_as_dict = yaml.load(yamlAsString.read())
#     cluster_api_spec_as_dict = getYml(pathFile)
#     print('YAML as dict: ', cluster_api_spec_as_dict)
#     print('--------------\n\n\n')
#     cluster_api_spec_as_dict['spec']['containers'][0]['command'].append("--service-node-port-range=1000-40000")
#     print('YAML as dict modified: ', cluster_api_spec_as_dict)
#     print('--------------\n\n\n')
#     # yaml_as_string_modified = yaml.dump(cluster_api_spec_as_dict, stream=None, default_flow_style=True)
#     yaml_as_string_modified = yaml.dump(cluster_api_spec_as_dict, default_flow_style=False)
#     print ('dict modified: ' + yaml_as_string_modified)
#     print('YAML as string modified: ' + yaml_as_string_modified)
#     writeFile(os.environ['PWD'] + '/cluster_api2.yml', yaml.dump(cluster_api_spec_as_dict, default_flow_style=False))
#     #+ pathFile,yaml_as_string_modified)


def startEtm(paas_type):
    print('Deploying the ETM....')
    start_etm_on_k8s_command = 'kubectl create'
    if(paas_type == 'openstack'):
        start_etm_on_k8s_command += ' -f /kubernetes/ek/storage-class/openstack-storage-class.yaml'
    else:
        start_etm_on_k8s_command += ' -f /kubernetes/ek/storage-class/aws-storage-class.yaml'

    start_etm_on_k8s_command += ' -f /kubernetes/ek -f /kubernetes/ek/volumes'

    subprocess.call(shlex.split(start_etm_on_k8s_command))


def checkParametersByPaas(args):
    interface_info = []
    if(args.paas_type and args.paas_type == 'openstack' and args.paas_url and args.paas_user and args.paas_pass and args.paas_project_name and args.ansible_file):
        interface_info = [{"key": "type", "value": args.paas_type},
                          {"key": "username",
                           "value": args.paas_user},
                          {"key": "password",
                           "value": args.paas_pass},
                          {"key": "project_name",
                           "value": args.paas_project_name},
                          {"key": "auth_url",
                           "value": args.paas_url}]
    elif(args.paas_type and args.paas_type == 'aws' and args.paas_user and args.paas_pass and args.paas_project_name and args.ansible_file):
        interface_info = [{"key": "type", "value": args.paas_type},
                          {"key": "aws_access_key",
                           "value": args.paas_user},
                          {"key": "aws_secret_key",
                           "value": args.paas_pass},
                          {"key": "region",
                           "value": args.paas_project_name}]
    else:
        print(FAIL + 'K8 parameters are mandatory' + ENDC)
        exit(1)

    return interface_info


def startK8(args, dockerComposeProject):
    if(args.command == 'stop'):
        stopEpm(args, dockerComposeProject)
    elif(args.command == 'start'):     
        info = checkParametersByPaas(args)
        epm_url = startAndWaitForEpm(args, dockerComposeProject)

        # Start EPM
        if(epm_url):
            # STEP 1: REPLACE HERE WITH THE EPM IP !!!
            api_client = ApiClient(
                host=epm_url)

            # Setup the needed APIs
            key_api = KeyApi(api_client=api_client)
            worker_api = WorkerApi(api_client=api_client)
            package_api = PackageApi(api_client=api_client)
            runtime_api = RuntimeApi(api_client=api_client)
            adapter_api = AdapterApi(api_client=api_client)
            pop_api = PoPApi(api_client=api_client)
            cluster_api = ClusterApi(api_client=api_client)

            # STEP 2: Provide the OpenStack credentials            
            print('Deploying ElasTest on ' + args.paas_type)
            os_pop = PoP(interface_endpoint=args.paas_url,
                         interface_info=info, name="os-dc1", status="active")
            
            pop_api.register_po_p(os_pop)

            # STEP 3: Check if ansible adapter is available
            wait_ansible = True
            max_retries = 5
            current_retry = 0
            while (wait_ansible):
                adapters = adapter_api.get_all_adapters()
                ansible_found = False
                for a in adapters:
                    if a.type == "ansible":
                        ansible_found = True
                        break
                wait_ansible = not ansible_found
                time.sleep(1)
                if(current_retry == max_retries):
                    print(FAIL + "Error: Ansible adapter not available after " +
                          str(max_retries) + "retries" + ENDC)
                    print('')
                    stopEpm(args, dockerComposeProject)
                    exit(1)

                if(wait_ansible):
                    print("Ansible adapter not available. Retry " +
                          str(current_retry + 1) + "/" + str(max_retries))
                max_retries = max_retries - 1
            print('')
            print("Ansible adapter available: " + str(ansible_found))

            # STEP 4: Start VMs on OpenStack
            # Ideally  to test everything - Send package for initializing the Cluster
            # Send second package for adding a new node
            print('File with the definition of the cluster:',
                  ansiblePath + '/' + args.ansible_file)
            resource_group = package_api.receive_package(
                file=ansiblePath + '/' + args.ansible_file)
            print('Resource group: ', resource_group)

            # # This package can contain one VM, which will be added to the cluster
            # resource_group_single = package_api.receive_package(
            #     file=ansiblePath + '/ansible-node.tar')
            # print(resource_group_single)

            # STEP 5: Start the cluster from one of the resource groups
            if(not resource_group.vdus or len(resource_group.vdus) == 0):
                print(FAIL + 'Error: resource_group.vdus is empty or null' + ENDC)
                print('')
                # stopEpm(args, dockerComposeProject)
                exit(1)

            cluster_from_resource_group = ClusterFromResourceGroup(
                resource_group_id=resource_group.id, type=["kubernetes"], master_id=resource_group.vdus[0].id)
            cluster = cluster_api.create_cluster(
                cluster_from_resource_group=cluster_from_resource_group)

            ssh_client = getSshConnection(resource_group.vdus[0].ip)
            setK8sClientConfigurarion(ssh_client)
            # modifyNodePortRangePortmodifyNodePortRangePort(ssh_client)
            closeSshConnection(ssh_client)

            # getK8sConfigFromCluster(resource_group.vdus[0].ip)
            startEtm(args.paas_type)

            # STEP 6: Add a new worker to the Cluster (from the second resource group)
            # cluster_api.add_worker(
            #     id=cluster.id, machine_id=resource_group_single.vdus[0].id)

            print(cluster_api.get_all_clusters())

            # # STEP 7: Remove a node from the cluster (Note: This does not remove the VM, just makes the node inactive on the Cluster)
            # cluster_api.remove_node(
            #     id=cluster.id, worker_id=cluster.nodes[0].id)

            # print(cluster_api.get_all_clusters())

            # # STEP 8: Remove cluster (Note: does not remove the VMs)
            # cluster_api.delete_cluster(id=cluster.id)

            # # Step 9: Remove OS vms
            # package_api.delete_package(resource_group.id)
            # package_api.delete_package(resource_group_single.id)