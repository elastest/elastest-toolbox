outputMessages = {'update': 'Updating ElasTest Platform version ',
                  'pull-images': 'Pulling the ElasTest Platform Images '}


def printMsg(key):
    if(key == 'stop help'):
        print ''
        print '*****************************************************************************************'
        print '*  To stop press Ctrl+C or open new terminal and type:                                  *'
        print '*  docker run -v /var/run/docker.sock:/var/run/docker.sock --rm elastest/platform stop  *'
        print '*****************************************************************************************'
        print ''
    elif(key == 'stopping'):
        print ''
        print '*************************'
        print '*  Stopping components  *'
        print '*************************'
        print ''
    elif(key == 'update'):
        print ''
        print '' + outputMessages['update']
        print ''
    elif(key == 'pull-images'):
        print ''
        print '' + outputMessages['pull-images']
        print ''
    elif(key == 'elastest_home_error'):
        print ''
        print 'ERROR: It is necessary to configure a volume to store ElasTest data'
        print 'eg. -v ~/.elastest:/data'
    elif(key == 'credentials_already_established'):
        print ''
        print 'WARNING! The credentials for Jenkins and TestLink have already been established.'
        print 'These credentials were set at the first start up of ElasTest.'
        print 'You can see them in the service page on ElasTest.'
        print ''
