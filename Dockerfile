FROM edujgurjc/alpine-python-compose

## netcat
RUN  apk add --no-cache netcat-openbsd

# Start
RUN mkdir /elastest-toolbox


# Copy scripts folder
COPY scripts /elastest-toolbox/scripts


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


RUN cd /elastest-toolbox/scripts

# Python prints in order
ENV PYTHONUNBUFFERED=0

# Commands
WORKDIR /elastest-toolbox/scripts

ENTRYPOINT ["python","main.py"]

CMD ["-h"]
