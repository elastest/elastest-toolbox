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

#How to stop:
```
kubectl delete -f .
```

*don't include the volumes folder if you don't want to lose the elastest data, as the volumes will be deleted*

