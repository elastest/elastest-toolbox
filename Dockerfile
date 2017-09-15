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

COPY down.py /elastest-toolbox/down.py

COPY init.sh /elastest-toolbox/init.sh

RUN chmod 777 /elastest-toolbox/run.py

RUN chmod 777 /elastest-toolbox/down.py

RUN chmod 777 /elastest-toolbox/init.sh



# Copy deploy folders of each component

COPY edm/deploy /elastest-toolbox/edm/deploy

COPY etm/deploy /elastest-toolbox/etm/deploy

COPY esm/deploy /elastest-toolbox/esm/deploy

COPY eim/deploy /elastest-toolbox/eim/deploy

COPY epm/deploy /elastest-toolbox/epm/deploy

COPY emp/deploy /elastest-toolbox/emp/deploy

EXPOSE 8091

CMD cd /elastest-toolbox; exec ./init.sh
