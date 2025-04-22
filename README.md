# lam-workflow
The deployment package for the LAM services.

This repository provides the enterprise architecture and description of capabilities necessary for the digital transformation of the asset publishing life-cycle workflow.   

# System Requirements for Project Services

The following table outlines the system requirements for each of the project services. Each service is allocated the same resources to ensure consistent performance and scalability across the application stack.

## Resource Allocation

- **CPU:** 2048 millicores (2 vCPU)
- **Memory:** 8 GB RAM

## Service Resource Table

| Service Name                     | CPU Value     | Memory Value |
|----------------------------------|---------------|---------------|
| lam-validator-api               | 2048 (2 vCPU) | 8 GB RAM      |
| lam-validator-ui                | 2048 (2 vCPU) | 8 GB RAM      |
| rdf-validator-celery-worker     | 2048 (2 vCPU) | 8 GB RAM      |
| redis                           | 2048 (2 vCPU) | 8 GB RAM      |
| lam-generation-service-api      | 2048 (2 vCPU) | 8 GB RAM      |
| lam-generation-service-ui       | 2048 (2 vCPU) | 8 GB RAM      |
| lam-generation-celery-worker    | 2048 (2 vCPU) | 8 GB RAM      |
| fuseki                          | 2048 (2 vCPU) | 8 GB RAM      |


# Installation

### Install the Docker engine

 Please follow the official instructions located [here](https://docs.docker.com/engine/install/ubuntu/).
 
### Install Docker compose

Please follow the official instructions located [here](https://docs.docker.com/compose/install/).


### Clone the lam-workflow repository to your target machine 
Either open a shell and run the following:

```
git clone https://github.com/meaningfy-ws/lam-workflow.git
``` 

or unzip the project that you received.

### Prepare [`.env`](.env) file

Ensure that you have .env file in project root folder with following minimal variables:
```env

# The following are secret environment variables:

RDF_VALIDATOR_API_PORT=
RDF_VALIDATOR_UI_PORT=
RDF_VALIDATOR_API_LOCATION=
RDF_VALIDATOR_UI_LOCATION=
RDF_VALIDATOR_GUNICORN_TIMEOUT=
RDF_VALIDATOR_GUNICORN_API_WORKERS=
RDF_VALIDATOR_GUNICORN_UI_WORKERS=
RDF_VALIDATOR_UI_NAME=
RDF_VALIDATOR_REPORT_TITLE=
RDF_VALIDATOR_TEMPLATE_LOCATION=
RDF_VALIDATOR_HTML_REPORT_TEMPLATE_LOCATION=
RDF_VALIDATOR_SHACL_SHAPES_LOCATION=
RDF_VALIDATOR_APS_LOCATION=
RDF_VALIDATOR_ALLOWS_EXTRA_SHAPES=
LAM_GUNICORN_TIMEOUT=
LAM_API_LOCATION=
LAM_API_PORT=
LAM_GUNICORN_API_WORKERS=
LAM_UI_LOCATION=
LAM_UI_PORT=
LAM_GUNICORN_UI_WORKERS=
LAM_FUSEKI_DATA_FOLDER=
LAM_FUSEKI_LOCATION=
LAM_FUSEKI_PORT=
LAM_FUSEKI_QUERY_URL=
LAM_FUSEKI_USERNAME=
LAM_FUSEKI_PASSWORD=
LAM_FUSEKI_ADMIN_PASSWORD=
LAM_FUSEKI_EXTERNAL_PORT=
LAM_FUSEKI_JVM_ARGS=
RDF_VALIDATOR_API_SECRET_KEY=
RDF_VALIDATOR_UI_SECRET_KEY=
RDF_VALIDATOR_DEBUG=
RDFUNIT_QUERY_DELAY_MS=
RDF_VALIDATOR_REDIS_PORT=
RDF_VALIDATOR_REDIS_LOCATION=
RDF_VALIDATOR_FLOWER_PORT=

# The following are technical environment variables:

PROJECT_PATH=
ENV_FILE_PATH=
INFRA_FOLDER_PATH=
PROJECT_NAME=

```

### Starting the services

Navigate to the repository "lam-workflow" (where Git cloned the repository) or to the location where you unzipped the project.

> For additional configuration for the validator services check the **Configuration** chapter from the [tech-manual.pdf](docs/tech-manual/tech-manual.pdf)

After this preparation command, run 
```shell script
make start-services
```
in the shell window.

To stop the services run:
```shell script
make stop-services
```


# Usage
For usage examples check  the **Usage** chapter from the [tech-manual.pdf](docs/tech-manual/tech-manual.pdf)

# Documents
* The *architectural design* and the detailed deployment specifications are provided in the [Enterprise Architecture document](docs/lam-architecture/lam-enterprise-architecture.pdf). 
* The *technical guide* for installing and running the services are provided in the ["Installation guide"](docs/tech-manual/tech-manual.pdf). 


# Repository Structure
* `/docs` - the documentation specific to this project
  * `/docs/lam-architecture` - the LaTeX source of the enterprise architecture document
  * `/docs/references` - a database of literature references used in the enterprise architecture document and technical user manual 
  * `/docs/tech-manual` - the technical user manual for installing and running the services
* `/docker` - the docker files representing specification and configurations for running the services on a target server
* `/lam4doc` - source code for the LAM Generation Service
* `/validator` - source code for the Validator Service
* `README.md` - this file

# Services and their respective configurations
Please note that the configured values can be changed by modifying the [`.env`](.env) file.

### LAM Validator API

This service encapsulates the actual validation engine and exposes its functionality as an API.

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Internal URL | http://lam-validator-api | RDF_VALIDATOR_API_LOCATION | 
| Port | 10001 | RDF_VALIDATOR_API_PORT|

*NOTE:* When validating SPARQL endpoints, the fully qualified domain name of the machine must be specified. As a consequence, `localhost` will not work.

### LAM Validator UI

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Internal URL | http://lam-validator-ui | RDF_VALIDATOR_UI_LOCATION | 
| Port | 10002 | RDF_VALIDATOR_UI_PORT |

*NOTE:* When validating SPARQL endpoints, the fully qualified domain name of the machine must be specified. As a consequence, `localhost` will never work.

### LAM Generation Service API

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Internal URL | http://lam-generation-service-api | LAM_API_LOCATION | 
| Port | 4050 | LAM_API_PORT|


### LAM Generation Service API

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Internal URL | http://lam-generation-service-ui | LAM_UI_LOCATION | 
| Port | 8050 | LAM_UI_PORT|
### LAM Generation Service UI

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Internal URL | http://lam-generation-service-ui | LAM_UI_LOCATION | 
| Port | 8050 | LAM_UI_PORT|

### LAM Fuseki

This is the triple store that is used by the LAM generation service software to generate the report and indexes.

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Admin account password | admin | LAM_FUSEKI_ADMIN_PASSWORD|
| User name| admin | LAM_FUSEKI_USERNAME |
| Password | admin | LAM_FUSEKI_PASSWORD|
| Folder where Fuseki stores data | `./fuseki-lam-volume` | LAM_FUSEKI_DATA_FOLDER|
| Internal port | 3030 | LAM_FUSEKI_PORT |
| External port | 3010 | LAM_FUSEKI_EXTERNAL_PORT |
| Additional arguments passed to JVM | -Xmx2g | LAM_FUSEKI_JVM_ARGS|
| URL | http://rdf-differ-fuseki | LAM_FUSEKI_LOCATION |
| Query URL | /lam/query | LAM_FUSEKI_QUERY_URL |

> Please note that the URL is only available inside the same Docker containers network and is not visible from the outside. Its purpose is to provide a named way for a service to connect to another service.
# Requirements

### Hardware requirements

At least 8 Gb of RAM.
At least a dual core CPU.
At least 64Gb of free space.

### Software requirements 

A Linux distribution having a kernel with a version higher than 5.4.0.

### Ports

The following ports must be available on the host machine, as they will be bound to by different docker services:


|Port | Service|
|------------|-------|
|3010| LAM Fuseki|
|4050| LAM Generation Service API|
|8050| LAM Generation Service UI|
|10001| LAM Validator API|
|10002| LAM Validator UI|


# Contributing
You are more than welcome to help expand and mature this project. 

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions with the project.  

# Licence 

The documents, such as reports and specifications, available in the /doc folder, are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The source code and other scripts are licenced under [EUPL v1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) licence.
