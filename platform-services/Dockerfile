FROM alpine:3.5

COPY ebs/elastestservice.json /platform-services/ebs-elastestservice.json
COPY eds/elastestservice.json /platform-services/eds-elastestservice.json
COPY ems/elastestservice.json /platform-services/ems-elastestservice.json
COPY ess/elastestservice.json /platform-services/ess-elastestservice.json
COPY eus/elastestservice.json /platform-services/eus-elastestservice.json

# Set labels
ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT

ARG COMMIT_DATE=unspecified
LABEL commit_date=$COMMIT_DATE

ARG VERSION=unspecified
LABEL version=$VERSION

CMD exec top 2>&1 >/dev/null
