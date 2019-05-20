from epm_client.apis import *
from epm_client import ApiClient
from epm_client.models import *


def startK8(args):
        # STEP 1: REPLACE HERE WITH THE EPM IP !!!
        api_client = ApiClient(host="http://<EPM_IP>:8180/v1")

        # Setup the needed APIs
        key_api = key_api.KeyApi(api_client=api_client)
        worker_api = worker_api.WorkerApi(api_client=api_client)
        package_api = PackageApi(api_client=api_client)
        runtime_api = RuntimeApi(api_client=api_client)
        adapter_api = AdapterApi(api_client=api_client)
        pop_api = PoPApi(api_client=api_client)
        cluster_api = ClusterApi(api_client=api_client)


        # STEP 2: Provide the OpenStack credentials
        os_pop = PoP(interface_endpoint="http://<REPLACE>:5000/v2.0",
                        interface_info=[{"key": "type", "value": "openstack"},
                                        {"key": "username",
                                        "value": "<REPLACE>"},
                                        {"key": "password",
                                        "value": "<REPLACE>"},
                                        {"key": "project_name",
                                        "value": "<REPLACE>"},
                                        {"key": "auth_url",
                                        "value": "http://<REPLACE>:5000/v2.0"}], name="os-dc1", status="active")
        pop_api.register_po_p(os_pop)

        # STEP 3: Check if ansible adapter is available
        adapters = adapter_api.get_all_adapters()
        ansible_found = False
        for a in adapters:
        if a.type == "ansible":
                ansible_found = True
        print("Ansible adapter available: " + str(ansible_found))

        # STEP 4: Start VMs on OpenStack
        # Ideally  to test everything - Send package for initializing the Cluster
        # Send second package for adding a new node
        resource_group = package_api.receive_package(file='resources/ansible-package2.tar')
        print(resource_group)

        # This package can contain one VM, which will be added to the cluster
        resource_group_single = package_api.receive_package(file='resources/ansible-package.tar')
        print(resource_group_single)

        # STEP 5: Start the cluster from one of the resource groups
        cluster_from_resource_group = ClusterFromResourceGroup(resource_group_id=resource_group.id, type=["kubernetes"], master_id=resource_group.vdus[0].id)
        cluster = cluster_api.create_cluster(cluster_from_resource_group=cluster_from_resource_group)

        print(cluster)

        # STEP 6: Add a new worker to the Cluster (from the second resource group)
        cluster_api.add_worker(id=cluster.id, machine_id=resource_group_single.vdus[0].id)

        print(cluster_api.get_all_clusters())

        # STEP 7: Remove a node from the cluster (Note: This does not remove the VM, just makes the node inactive on the Cluster)
        cluster_api.remove_node(id=cluster.id, worker_id=cluster.nodes[0].id)

        print(cluster_api.get_all_clusters())

        # STEP 8: Remove cluster (Note: does not remove the VMs)
        cluster_api.delete_cluster(id=cluster.id)

        # Step 9: Remove OS vms
        package_api.delete_package(resource_group.id)
        package_api.delete_package(resource_group_single.id)
