# How to run ElasTest
- First give permissions: 
```
kubectl create clusterrolebinding default-admin --clusterrole cluster-admin --serviceaccount=default:default
```
- Clone toolbox project
```
git clone elastest/elastest-toolbox
```
- Navigate to folder
```
cd elastest-toolbox/kubernetes/beta-mini
```
- Start ElasTest
```
kubectl create -f . -f volumes/
```
*-f volumes it’s only necessary first time, but there is no problem if it is used at another time, although error messages will be output*

# How to access
- Run `kubectl get service etm-proxy` to view info and get CLUSTER-IP. You can also directly execute this command that returns only the ip: `kubectl describe service etm-proxy | grep IP: | sed -E 's/IP:[[:space:]]+//'`
- Open your browser and navigate to http://CLUSTER-IP:37000

# How to stop:
```
kubectl delete -f .
```

*don't include the volumes folder if you don't want to lose the elastest data, as the volumes will be deleted*

# Minikube
If you use minikube you must start it with the `--extra-config=apiserver.service-node-port-range=1000-40000` parameter to change the default ports.

On the other hand, you must follow the steps in the section `How to run ElasTest` and then get the ip with `minikube ip`. Type in your browser this ip with port `37000` to access ElasTest