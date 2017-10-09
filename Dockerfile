FROM weboaks/alpine-docker-compose

RUN apk update

# Add python
RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

## netcat
RUN  apk add --no-cache netcat-openbsd

# Start
RUN mkdir /elastest-toolbox


# Copy scripts

COPY run.py /elastest-toolbox/run.py

COPY init.py /elastest-toolbox/init.py

COPY messages.py /elastest-toolbox/messages.py

COPY checkETM.py /elastest-toolbox/checkETM.py

RUN chmod 777 /elastest-toolbox/run.py

RUN chmod 777 /elastest-toolbox/init.py

RUN chmod 777 /elastest-toolbox/checkETM.py



# Copy deploy folders of each component

COPY edm/deploy /elastest-toolbox/edm/deploy

COPY etm/deploy /elastest-toolbox/etm/deploy

COPY etm/docker /elastest-toolbox/etm/docker

COPY esm/deploy /elastest-toolbox/esm/deploy

COPY eim/deploy /elastest-toolbox/eim/deploy

COPY epm/deploy /elastest-toolbox/epm/deploy

COPY emp/deploy /elastest-toolbox/emp/deploy

# Copy platform-services

COPY platform-services /elastest-toolbox/platform-services


RUN cd /elastest-toolbox

# Python prints in order
ENV PYTHONUNBUFFERED=0

# Commands
WORKDIR /elastest-toolbox

ENTRYPOINT ["python","init.py"]

CMD ["-h"]
