node('docker'){
    
    stage " Download Elastest-toolbox"

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

            stage "Commit platform submodules"
    
              "Commit platform submodules"

                echo ("Commit submodules if is necessary")     
		withCredentials([usernamePassword(credentialsId: 'GitHub-elastest', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
		    sh ('cd scripts; chmod 755 updateSubmodules.sh; ./updateSubmodules.sh')
		}


            stage "Platform-Services image build"
    
              "Create platform-services docker image"
            
                echo ("Creating elastest/platform-services image..")                
                sh 'docker build --build-arg GIT_COMMIT=$(git rev-parse HEAD) --build-arg COMMIT_DATE=$(git log -1 --format=%cd --date=format:%Y-%m-%d) -t elastest/platform-services . -f platform-services/Dockerfile'
    
            stage "Publish Platform-Services docker image"
    
                echo ("Publish elastest/platform-services image")
                def platformservicesimage = docker.image('elastest/platform-services')
                //this is work arround as withDockerRegistry is not working properly 
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'elastestci-dockerhub',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                    platformservicesimage.push()
                }
            
            
            stage "Platform image build"
    
              "Create platform docker image"
            
                echo ("Creating elastest/platform image..")                
                sh 'docker build --build-arg GIT_COMMIT=$(git rev-parse HEAD) --build-arg COMMIT_DATE=$(git log -1 --format=%cd --date=format:%Y-%m-%d) -t elastest/platform:dev .'
    
            stage "IT Test ETM is running"
	         sh 'cd scripts; chmod 755 it.sh; ./it.sh'

            stage "Publish Platform docker image"
    
                echo ("Publish elastest/platform image")
                def platformimage = docker.image('elastest/platform:dev')
                //this is work arround as withDockerRegistry is not working properly 
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'elastestci-dockerhub',
                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    sh 'docker login -u "$USERNAME" -p "$PASSWORD"'
                    platformimage.push()
                }

        }
}
