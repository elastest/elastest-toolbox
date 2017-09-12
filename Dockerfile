FROM weboaks/alpine-docker-compose

RUN apk update

RUN apk add git

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
  && pip install virtualenv \
  && rm -rf /var/cache/apk/*


RUN mkdir /elastest-toolbox


# Copy scripts

COPY run.py /elastest-toolbox/run.py

COPY down.py /elastest-toolbox/down.py

RUN chmod 777 /elastest-toolbox/run.py



# Copy deploy folders of each component

COPY elastest-data-manager/deploy /elastest-toolbox/elastest-data-manager/deploy

COPY elastest-torm/deploy /elastest-toolbox/elastest-torm/deploy

COPY elastest-service-manager/deploy /elastest-toolbox/elastest-service-manager/deploy


EXPOSE 8091

CMD cd /elastest-toolbox; exec python run.py
