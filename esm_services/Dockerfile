FROM alpine:3.5

COPY ebs/elastestservice.json /esm_services/ebs-elastestservice.json
COPY eds/elastestservice.json /esm_services/eds-elastestservice.json
COPY ems/elastestservice.json /esm_services/ems-elastestservice.json
COPY ess/elastestservice.json /esm_services/ess-elastestservice.json
COPY eus/elastestservice.json /esm_services/eus-elastestservice.json

CMD exec top 2>&1 >/dev/null
