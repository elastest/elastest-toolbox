AWS CloudFormation Template
===

----------

## Introduction

This repo includes all the necessary to easy deploy Elastest on AWS.

Also contains the recipe to deploy Elastest with Jenkins CI.

## How to use it

First of all you'll need an AWS account. To achive that, follow those [steps](http://docs.aws.amazon.com/AmazonSimpleDB/latest/DeveloperGuide/AboutAWSAccounts.html).

Then, you can go to [AWS CloudFormation Pane](https://eu-west-1.console.aws.amazon.com/cloudformation/) and create a **new stack**. You will need the **json** included on this repo to complete the task. The form you'll see on the second step have to be filled with the following information:

| Parameter | Value | Details | 
|-----------|-------|---------|
| Stack name | The name of the stack | Elastest is OK | 
| ElastestPassword | elastest | Password to access the platform | 
| ElastestUsername | elastest | Username to access the platform | 
| ElastestVersion | latest | which version of elastest do you want to launch | 
| InstanceType | m4.large | Elastest needs resources to run, please be genereous | 
| KeyName |  | RSA key to access the instance through SSH | 
| SwapSize | 4 | The amount of swap memory in GB | 

When the stack finished the deployment, you can check *output* tab to see the URL to access your application.

## Updating Elastest

In order to update Elastest, run this command first:

```
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock elastest/platform update
```

Then restart Elastest.

```
# systemctl stop docker-elastest
# systemctl start docker-elastest
```

And just wait a few second to start.

**Elastest! Happy Testing!**

## How it's work

This deployment is bases in Cloud Formation, which is an AWS product for IAC (infrastructure as code). So, with a YAML template we can tell AWS that we want an EC2 Instance (Virtual Machine), with specific features, like Memory, Disc capacity or CPU.

With that we've the Instance, but what about the code... To achive that, we use Ansible.

Ansible is a product from Red Hat allow you to define how to configure a instance. Ansible is software that automates software provisioning, configuration management, and application deployment. It's also based on YAML files where one can define task to do on remote or local systems.

Let's deep deeper. We can think of the deployment as two parts:

On the first, part we create an instance with the features of CPU, Disk and Memory, and, also, the network security groups which allow the user to reach the services, we create a paging space (Swap memory) which improve system performance.

On the second part, Ansible will provisioning the instance turning the input values into configured services. To do that we use one of Cloud Formation utilities. The capacity of executing scripts inside the instances. So, in the end, we're creating the instance and executing a script which turn the input values into configured serviced using Ansible.

The Ansible playbook (this is the name that templates received) will do:

1. Will install Docker. Docker is a computer program that performs operating-system-level virtualization also known as containerization.
2. Will configure the instance in order to run ElasticSearch. ElasticSearch is a search engine based on Lucene. It provides a distributed, multitenant-capable full-text search engine with an HTTP web interface and schema-free JSON documents. It's known about this issue with the memory and the number of open file descriptors.
3. Will configure the system to automatically start Elastest in every boot up.
4. Also will create maintenance scripts to remove Elastest in order to not deal with duplicated conetainers that could cause malfuctions or even Elastest not to start.
5. At the end, will send a signal to CloudFormation API to let it known the work is done.

And that's it. When Cloud Formation recived the signal will show in the Output tab the URL you can use to reach the service.