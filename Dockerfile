FROM edujgurjc/alpine-python-compose

RUN apk add --no-cache openssl-dev libffi-dev

RUN pip install --upgrade pip

RUN pip install 'docker-compose==1.22.0'
RUN pip install epm-client
RUN pip install urllib3
RUN pip install certifi
RUN pip install paramiko
RUN pip install 'ruamel.yaml==0.15.0'

## netcat
RUN apk add --no-cache netcat-openbsd
RUN apk --no-cache add curl

# Start
RUN mkdir /elastest-toolbox

# Set labels
ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT

ARG COMMIT_DATE=unspecified
LABEL commit_date=$COMMIT_DATE

ARG VERSION=unspecified
LABEL version=$VERSION

# Copy deploy folders of each component

COPY edm/deploy /elastest-toolbox/edm/deploy

COPY etm/deploy /elastest-toolbox/etm/deploy

COPY etm/docker /elastest-toolbox/etm/docker

COPY esm/deploy /elastest-toolbox/esm/deploy

COPY eim/deploy /elastest-toolbox/eim/deploy

COPY epm/deploy /elastest-toolbox/epm/deploy

COPY emp/deploy /elastest-toolbox/emp/deploy

COPY docker-compose-mysql-elasticsearch-lite.yml /elastest-toolbox/docker-compose-mysql-elasticsearch-lite.yml

# Copy all elastestservice.json

COPY ebs/elastestservice.json /elastest-toolbox/ebs/elastestservice.json
COPY eds/elastestservice.json /elastest-toolbox/eds/elastestservice.json
COPY ems/elastestservice.json /elastest-toolbox/ems/elastestservice.json
COPY ess/elastestservice.json /elastest-toolbox/ess/elastestservice.json
COPY eus/elastestservice.json /elastest-toolbox/eus/elastestservice.json

# Copy ETM properties file
COPY etm/elastest-torm/src/main/resources/application.properties /elastest-toolbox/etm/application.properties

# Copy Test Engines files
COPY etm/elastest-torm/src/main/resources/test_engines /elastest-toolbox/etm/elastest-torm/src/main/resources/test_engines

# Copy platform-services
COPY platform-services /elastest-toolbox/platform-services

# Copy kubernetes files
COPY kubernetes/ek /kubernetes/ek
COPY kubernetes/hek /kubernetes/hek

COPY version-scripts /elastest-toolbox/version-scripts

# Copy scripts folder
COPY scripts /elastest-toolbox/scripts

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl \
    && chmod +x ./kubectl \
    && mv ./kubectl /usr/local/bin/kubectl

RUN mkdir ~/.kube \
    && cd ~/.kube \
    && touch config

RUN cd /elastest-toolbox/scripts


# Python prints in order
ENV PYTHONUNBUFFERED=0

# Commands
WORKDIR /elastest-toolbox/scripts

ENTRYPOINT ["python","main.py"]

CMD ["-h"]
