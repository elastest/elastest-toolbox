FROM weboaks/alpine-docker-compose

RUN apk update

RUN apk add git

# Add python
RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*

# Start
RUN mkdir /elastest-toolbox


# Copy scripts

COPY run.py /elastest-toolbox/run.py

COPY init.sh /elastest-toolbox/init.sh

RUN chmod 777 /elastest-toolbox/run.py

RUN chmod 777 /elastest-toolbox/init.sh



# Copy deploy folders of each component

COPY edm/deploy /elastest-toolbox/edm/deploy

COPY etm/deploy /elastest-toolbox/etm/deploy

COPY etm/docker /elastest-toolbox/etm/docker

COPY esm/deploy /elastest-toolbox/esm/deploy

COPY eim/deploy /elastest-toolbox/eim/deploy

COPY epm/deploy /elastest-toolbox/epm/deploy

COPY emp/deploy /elastest-toolbox/emp/deploy

RUN cd /elastest-toolbox

# Commands
WORKDIR /elastest-toolbox

ENTRYPOINT ["./init.sh"]

CMD ["start"]
