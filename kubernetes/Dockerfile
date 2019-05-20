FROM edujgurjc/alpine-python-compose

RUN pip install 'docker-compose==1.22.0'
RUN pip install epm-client

## netcat
RUN  apk add --no-cache netcat-openbsd

# Start
RUN mkdir /k8s-elastest-toolbox

# Copy scripts folder
COPY platform/scripts /k8s-elastest-toolbox/scripts

# Copy the compose file to deploy the EPM
COPY platform/docker-compose-epm.yml /k8s-elastest-toolbox/epm

# Set labels
ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT

ARG COMMIT_DATE=unspecified
LABEL commit_date=$COMMIT_DATE

ARG VERSION=unspecified
LABEL version=$VERSION

RUN cd /elastest-toolbox/scripts

# Python prints in order
ENV PYTHONUNBUFFERED=0

# Commands
WORKDIR /elastest-toolbox/scripts

ENTRYPOINT ["python","main.py"]

CMD ["-h"]
