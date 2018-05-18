# ElasTest Vagrant

The Vagrantfiles in this repository starts up a Vagrant box, based on VirtualBox provider and starts ElasTest on it. Each subfolder has a Vagrantfile prepared to start ElasTest in a different mode: 

* Vagrantfile in elastest folder will start ElasTest in normal mode
* Vagrantfile in elastest-lite folder will start ElasTest in exerimental-lite mode
* Vagrantfile in elastest-experimental folder will start ElasTest in experimental mode

For more information on these modes, please refer to the [ElasTest documentation](https://elastest.io/docs/).

## Prerequisites

To run this VM you need 8GB of memory and 30GB of disk available.

You need [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/docs/installation/) installed. Vagrant boxes start by default with a 10GB hard disk attached. 
This is too small for running ElasTest. To start with a bigger disk, our Vagrantfiles make use of the Vagrant plugin `vagrant-disksize`. To install this plugin, issue the following command in a shell:

    vagrant plugin install vagrant-disksize

## Run ElasTest in a VM

Just run `vagrant up` to start the VM. Once started, the ID of the Docker container which is responsible for starting the whole ElasTest platform is shown as the very last entry of the Vagrant log:

    [...]
    default: 427f96586db4: Pull complete
    default: Digest: sha256:81e46524cc8a5394d768e261f9975162a1349b88304518873aa54164419ced9c
    default: Status: Downloaded newer image for elastest/platform:latest
    default: 9e58c843d99274f8384ba3d2541ebd805637a4c0a57c1cadfe156e4f534361e7

ElasTest won't be yet available, it will be downloading some Docker images it needs. To check when ElasTest is available we need to inspect the logs of the Docker container whose ID we gathered in the previous step:

   vagrant ssh
   docker logs -f 9e58c843d99274f8384ba3d2541ebd805637a4c0a57c1cadfe156e4f534361e7

As soon as the ElasTest URL is shown, the platform is ready. We use the URL provided to point a browser at it:

    Status: Downloaded newer image for elastest/etm:0.9.1
    0.9.1: Pulling from elastest/etm-proxy
    Digest: sha256:0736850abea475e3bdbd9a27fc9826ac23cb08f124bee848610cb3cc0a47ebc7
    Status: Downloaded newer image for elastest/etm-proxy:0.9.1
    Please wait a few seconds while we start the ElasTest services, the ElasTest URL will be shown when ready.

    ElasTest Platform is available at http://192.168.37.37:37000
    Press Ctrl+C to stop.

To configure additional jobs refer to [this part of the documentation](https://elastest.io/docs/testing/unit/).
