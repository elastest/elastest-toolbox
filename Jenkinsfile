node('docker'){
    
    stage "Elastest-torm images build"

        def mycontainer = docker.image('elastest/ci-docker-compose-siblings')
        mycontainer.pull() // make sure we have the latest available from Docker Hub
        mycontainer.inside("-u jenkins -v /var/run/docker.sock:/var/run/docker.sock:rw -v ${WORKSPACE}:/home/jenkins/.m2") {
            
            checkout([
                $class: 'GitSCM', 
                branches: scm.branches, 
                doGenerateSubmoduleConfigurations: false, 
                extensions: [[
                  $class: 'SubmoduleOption', 
                  disableSubmodules: false, 
                  parentCredentials: true, 
                  recursiveSubmodules: true, 
                  reference: '', 
                  trackingSubmodules: false
                ]], 
                submoduleCfg: [], 
                userRemoteConfigs: [[url: 'https://github.com/elastest/elastest-toolbox']]
              ])
            
            
            stage "Platform image build"
    
              "Create platform docker image"
            
                echo ("Creating elastest/platform image..")                
                sh 'docker build -t elastest/platform .'
    
            stage "Publish Platform docker image"
    
                echo ("Publish elastest/platform image")
                def platformimage = docker.image('elastest/platform')
                //this is work arround as withDockerRegistry is not working properly 
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'elastestci-dockerhub',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                    platformimage.push()
                }
        }
}