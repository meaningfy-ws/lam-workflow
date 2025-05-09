# Build RDFUnit
FROM maven:3-jdk-8 as build

ARG RDFUNIT_TAG=ef56ceb015163310e79b4a59dc5030bfb659ee70
RUN curl -L -f https://codeload.github.com/AKSW/RDFUnit/zip/${RDFUNIT_TAG} --output rdfunit-sources.zip && \
    unzip rdfunit-sources.zip && \
    rm rdfunit-sources.zip
WORKDIR /RDFUnit-${RDFUNIT_TAG}
RUN mvn -pl rdfunit-validate -am clean package -P cli-standalone -DskipTests=true

# Build for python API
FROM python:3.11.11-bullseye as target

RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install -y openjdk-11-jre

WORKDIR /usr/src/rdfunit
COPY --from=build /RDFUnit-*/rdfunit-validate/target/rdfunit-validate-*-standalone.jar /usr/src/rdfunit/rdfunit-validate.jar

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install -r requirements/common.txt

CMD gunicorn --timeout ${RDF_VALIDATOR_GUNICORN_TIMEOUT-1200} \
             --workers ${RDF_VALIDATOR_GUNICORN_API_WORKERS-2} \
             -k uvicorn.workers.UvicornWorker \
             --bind 0.0.0.0:${RDF_VALIDATOR_API_PORT} \
             --reload \
             --log-level=debug \
             validator.entrypoints.api.run:app