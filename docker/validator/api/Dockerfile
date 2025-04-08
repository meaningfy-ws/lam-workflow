# Build RDFUnit
FROM maven:3-jdk-8 as build

RUN curl https://codeload.github.com/AKSW/RDFUnit/zip/master --output rdfunit-sources.zip
RUN unzip rdfunit-sources.zip
WORKDIR /RDFUnit-master
RUN mvn -pl rdfunit-validate -am clean package -P cli-standalone -DskipTests=true

# Build for python API
FROM python:3.11.11-bullseye as target

RUN apt-get update -y \
&& apt-get upgrade -y \
&& apt-get install -y openjdk-11-jre

WORKDIR /usr/src/rdfunit
COPY --from=build /RDFUnit-master/rdfunit-validate/target/rdfunit-validate-*-standalone.jar /usr/src/rdfunit/rdfunit-validate.jar

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install --upgrade pip
RUN pip install -r requirements/common.txt

#ENV RDF_VALIDATOR_SHACL_SHAPES_LOCATION=/usr/src/shacl-shapes

#COPY shacl-shapes/ /usr/src/app/shacl-shapes

CMD gunicorn --timeout ${RDF_VALIDATOR_GUNICORN_TIMEOUT-1200} --workers ${RDF_VALIDATOR_GUNICORN_API_WORKERS-2} --bind 0.0.0.0:${RDF_VALIDATOR_API_PORT} --reload --log-level=debug validator.entrypoints.api.run:app