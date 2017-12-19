AWS CloudFormation Template
===

----------

## Introduction

This repo includes all the necessary to easy deploy Elastest on AWS.

## How to use it

First of all you'll need an AWS account. To achive that, follow those [steps](http://docs.aws.amazon.com/AmazonSimpleDB/latest/DeveloperGuide/AboutAWSAccounts.html).

Then, you can go to [AWS CloudFormation Pane](https://eu-west-1.console.aws.amazon.com/cloudformation/) and create a **new stack**. You will need the **json** included on this repo to complete the task. The form you'll see on the second step have to be filled with the following information:

| Parameter | Value | Details | 
| --- | --- | --- | --- |
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

