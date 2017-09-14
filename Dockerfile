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

COPY elastest-data-manager/deploy /elastest-toolbox/elastest-data-manager/deploy

COPY elastest-torm/deploy /elastest-toolbox/elastest-torm/deploy

COPY elastest-service-manager/deploy /elastest-toolbox/elastest-service-manager/deploy

COPY elastest-instrumentation-manager/deploy /elastest-toolbox/elastest-instrumentation-manager/deploy

COPY elastest-platform-manager/deploy /elastest-toolbox/elastest-platform-manager/deploy

EXPOSE 8091

CMD cd /elastest-toolbox; exec ./init.sh
