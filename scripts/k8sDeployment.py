from epm_client.apis import *
from epm_client import ApiClient
from epm_client.models import *
import subprocess
import shlex
from DockerUtils import *
from checkETM import *
import time
import sys
import urllib3
import certifi
import paramiko

epm_service_name = "elastest-platform-manager"
epm_port = "8180"
FNULL = subprocess.STDOUT
ansiblePath = "/data/ansible"
epmComposeCommand = "docker-compose -f ../epm/deploy/docker-compose.yml -p "


def startAndWaitForEpm(dockerComposeProject):
    startEpmCommand = epmComposeCommand + \
        dockerComposeProject + " up -d"
    result = subprocess.call(shlex.split(startEpmCommand), stderr=FNULL)
    if(result == 0):
        insertPlatformIntoNetwork()

        epm_url = "http://" + epm_service_name + ":" + epm_port + "/v1"
        wait = True
        sys.stdout.write('Waiting for EPM')
        while (wait):
            wait = not checkWorking(epm_url)
            sys.stdout.write('.')
            time.sleep(1)
        print('')
        print('EPM is available!')
        return epm_url
    else:
        print('Error on start EPM')
        exit(1)


def stopEpm(dockerComposeProject):
    print('Stopping EPM...')
    stopEpmCommand = epmComposeCommand + \
        dockerComposeProject + " down"
    result = subprocess.call(shlex.split(stopEpmCommand), stderr=FNULL)

def getK8sConfigFromCluster(k8s_host):
    HOST = k8s_host
    PUERTO = 22
    USUARIO = 'ubuntu'
    datos = dict(hostname=HOST, port=PUERTO, username=USUARIO, key_filename=ansiblePath + '/key')

    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(**datos)
    entrada, salida, error = ssh_client.exec_command('ls -la')
    print(salida.read())
    print('--------')
    entrada, salida, error = ssh_client.exec_command('cat /etc/kubernetes/admin.conf')
    print(salida.read())
    ssh_client.close()

def startK8(args, dockerComposeProject):
    if(args.command == 'stop'):
        stopEpm(dockerComposeProject)
    elif(args.command == 'start'):
        if(args.paas_ip and args.paas_user and args.paas_pass and args.paas_project_name):
            # TODO check args (start, mini, etc)
            epm_url = startAndWaitForEpm(dockerComposeProject)
            time.sleep(15)
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
                paasStackUrl = "http://" + args.paas_ip + ":" + args.paas_port + "/v2.0"
                os_pop = PoP(interface_endpoint=paasStackUrl,
                             interface_info=[{"key": "type", "value": "openstack"},
                                             {"key": "username",
                                              "value": args.paas_user},
                                             {"key": "password",
                                              "value": args.paas_pass},
                                             {"key": "project_name",
                                              "value": args.paas_project_name},
                                             {"key": "auth_url",
                                              "value": paasStackUrl}], name="os-dc1", status="active")
                pop_api.register_po_p(os_pop)

                # STEP 3: Check if ansible adapter is available
                adapters = adapter_api.get_all_adapters()
                ansible_found = False
                for a in adapters:
                    if a.type == "ansible":
                        ansible_found = True
                print("Ansible adapter available: " + str(ansible_found))

                # # STEP 4: Start VMs on OpenStack
                # # Ideally  to test everything - Send package for initializing the Cluster
                # # Send second package for adding a new node
                # resource_group = package_api.receive_package(
                #     file=ansiblePath + '/ansible-cluster.tar')
                # print('Resource group: ', resource_group)

                # # # This package can contain one VM, which will be added to the cluster
                # # resource_group_single = package_api.receive_package(
                # #     file=ansiblePath + '/ansible-node.tar')
                # # print(resource_group_single)

                # # STEP 5: Start the cluster from one of the resource groups
                # cluster_from_resource_group = ClusterFromResourceGroup(
                #     resource_group_id=resource_group.id, type=["kubernetes"], master_id=resource_group.vdus[0].id)
                # cluster = cluster_api.create_cluster(
                #     cluster_from_resource_group=cluster_from_resource_group)

                # print("Cluster:", cluster)
                # print("K8s_Master:", resource_group.vdus[0].ip)
                # getK8sConfigFromCluster(resource_group.vdus[0].ip)
                

                # # # STEP 6: Add a new worker to the Cluster (from the second resource group)
                # # cluster_api.add_worker(
                # #     id=cluster.id, machine_id=resource_group_single.vdus[0].id)

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
        else:
            print('K8 parameters are mandatory')
            exit(1)
