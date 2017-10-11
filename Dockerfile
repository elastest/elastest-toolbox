FROM edujgurjc/alpine-python-compose

## netcat
RUN  apk add --no-cache netcat-openbsd

# Start
RUN mkdir /elastest-toolbox


# Copy scripts folder
COPY scripts /elastest-toolbox/scripts

COPY version-scripts /elastest-toolbox/version-scripts

# Copy deploy folders of each component

COPY edm/deploy /elastest-toolbox/edm/deploy

COPY etm/deploy /elastest-toolbox/etm/deploy

COPY etm/docker /elastest-toolbox/etm/docker

COPY esm/deploy /elastest-toolbox/esm/deploy

COPY eim/deploy /elastest-toolbox/eim/deploy

COPY epm/deploy /elastest-toolbox/epm/deploy

COPY emp/deploy /elastest-toolbox/emp/deploy

# Copy all elastestservice.json

COPY ebs/elastestservice.json /elastest-toolbox/ebs/elastestservice.json
COPY eds/elastestservice.json /elastest-toolbox/eds/elastestservice.json
COPY ems/elastestservice.json /elastest-toolbox/ems/elastestservice.json
COPY ess/elastestservice.json /elastest-toolbox/ess/elastestservice.json
COPY eus/elastestservice.json /elastest-toolbox/eus/elastestservice.json

# Copy Test Engines files

COPY etm/elastest-torm/src/main/resources/test_engines /elastest-toolbox/etm/elastest-torm/src/main/resources/test_engines


# Copy platform-services

COPY platform-services /elastest-toolbox/platform-services


RUN cd /elastest-toolbox/scripts

# Python prints in order
ENV PYTHONUNBUFFERED=0

# Commands
WORKDIR /elastest-toolbox/scripts

ENTRYPOINT ["python","main.py"]

CMD ["-h"]
