from epm_client.apis import *
from epm_client import ApiClient
from epm_client.models import *
import subprocess
import shlex
from checkETM import *
import time
import sys
import urllib3
import certifi
import paramiko

FNULL = subprocess.STDOUT

epm_service_name = "elastest-platform-manager"
epm_port = "8180"
epm_adapter_ansible_service_name = "epm-adapter-ansible"
epm_adapter_ansible_port = "50052"

ansiblePath = "/data/ansible"
epmComposeCommandPrefix = "docker-compose -f ../epm/deploy/docker-compose.yml -p "


def startAndWaitForEpm(dockerComposeProject):
    startEpmCommand = epmComposeCommandPrefix + \
        dockerComposeProject + " up -d"
    result = subprocess.call(shlex.split(startEpmCommand), stderr=FNULL)
    if(result == 0):
        insertPlatformIntoNetwork()

        epm_url = "http://" + epm_service_name + ":" + epm_port + "/v1"
        waitForUrl(epm_url, 'Waiting for EPM', 'EPM is available!')

        epm_adapter_ansible_url = "http://" + \
            epm_adapter_ansible_service_name + ":" + epm_adapter_ansible_port
        waitForUrl(epm_adapter_ansible_url,
                   'Waiting for EPM adapter', 'EPM is ready now!')

        return epm_url
    else:
        print(FAIL + 'Error on start EPM' + ENDC)
        print('')
        stopEpm(dockerComposeProject)
        exit(1)


def stopEpm(dockerComposeProject):
    print('Stopping EPM...')
    stopEpmCommand = epmComposeCommandPrefix + \
        dockerComposeProject + " down"
    result = subprocess.call(shlex.split(stopEpmCommand), stderr=FNULL)


def getK8sConfigFromCluster(k8s_host):
    HOST = k8s_host
    PUERTO = 22
    USUARIO = 'ubuntu'
    datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,
                 key_filename=ansiblePath + '/key')
    #  key_filename='/home/frdiaz/.elastest/k8s/key')  # ansiblePath + '/key')

    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(**datos)
    entrada, salida, error = ssh_client.exec_command('ls -la /etc/kubernetes/')
    print(salida.read())
    print('--------')
    entrada, salida, error = ssh_client.exec_command(
        'sudo cat /etc/kubernetes/admin.conf')
    # print(salida.read())
    admin_conf_content = salida.read()
    print(admin_conf_content)

    kube_file = open('~/.kube/config', 'w')

    kube_file.write(admin_conf_content)
    kube_file.close()

    ssh_client.close()


def startEtmOnK8s():
    start_etm_on_k8s_command = 'cd /kubernetes/beta-mini; kubectl create -f . -f /volumes'
    # start_etm_on_k8s_command = 'kubectl create -f /home/frdiaz/git/elastest/elastest-toolbox/kubernetes/beta-mini -f /home/frdiaz/git/elastest/elastest-toolbox/kubernetes/beta-mini/volumes'
    # start_etm_on_k8s_command = 'ls'
    subprocess.call(shlex.split(start_etm_on_k8s_command))


def startK8(args, dockerComposeProject):
    if(args.command == 'stop'):
        stopEpm(dockerComposeProject)
    elif(args.command == 'start'):
        if(args.paas_url and args.paas_user and args.paas_pass and args.paas_project_name and args.paas_type):
            # TODO check args (start, mini, etc)
            epm_url = startAndWaitForEpm(dockerComposeProject)

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
                print('Paas type: ' + args.paas_type)
                if(args.paas_type == 'openstack'):
                    os_pop = PoP(interface_endpoint=args.paas_url,
                                 interface_info=[{"key": "type", "value": args.paas_type},
                                                 {"key": "username",
                                                  "value": args.paas_user},
                                                 {"key": "password",
                                                  "value": args.paas_pass},
                                                 {"key": "project_name",
                                                  "value": args.paas_project_name},
                                                 {"key": "auth_url",
                                                  "value": args.paas_url}], name="os-dc1", status="active")
                else:
                    os_pop = PoP(interface_endpoint=args.paas_url,
                                 interface_info=[{"key": "type", "value": args.paas_type},
                                                 {"key": "aws_access_key",
                                                  "value": args.paas_user},
                                                 {"key": "aws_secret_key",
                                                  "value": args.paas_pass},
                                                 {"key": "region",
                                                  "value": args.paas_project_name}], name="os-dc1", status="active")

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
                        stopEpm(dockerComposeProject)
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
                resource_group = package_api.receive_package(
                    file=ansiblePath + '/ansible-cluster.tar')
                print('Resource group: ', resource_group)

                # # This package can contain one VM, which will be added to the cluster
                # resource_group_single = package_api.receive_package(
                #     file=ansiblePath + '/ansible-node.tar')
                # print(resource_group_single)

                # STEP 5: Start the cluster from one of the resource groups
                if(not resource_group.vdus or len(resource_group.vdus) == 0):
                    print(FAIL + 'Error: resource_group.vdus is empty or null' + ENDC)
                    print('')
                    stopEpm(dockerComposeProject)
                    exit(1)

                cluster_from_resource_group = ClusterFromResourceGroup(
                    resource_group_id=resource_group.id, type=["kubernetes"], master_id=resource_group.vdus[0].id)
                cluster = cluster_api.create_cluster(
                    cluster_from_resource_group=cluster_from_resource_group)

                print("Cluster:", cluster)
                print("K8s_Master:", resource_group.vdus[0].ip)
                getK8sConfigFromCluster(resource_group.vdus[0].ip)
                startEtmOnK8s()

                # # STEP 6: Add a new worker to the Cluster (from the second resource group)
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
        else:
            print(FAIL + 'K8 parameters are mandatory' + ENDC)
            exit(1)
