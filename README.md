# lam-workflow
The deployment package for the LAM services.

This repository provides the enterprise architecture and description of capabilities necessary for the digital transformation of the asset publishing life-cycle workflow.   

# Documents
* The *technical guide* for installing and running the services are provided in the ["Installation guide"](./tech-manual/tech-manual.pdf). 


# Repository Structure
* /docs - the documentation specific to this project
* /docs/references - a database of literature references used in the enterprise architecture document and technical user manual 
* /docs/tech-manual - the technical user manual for installing and runnign the services
* /docker -the docker files representing specification and configurations for running the services on a target server
* README.md - this file

# Services and their respective configurations
Please note that the configured values can be changed by modifying the [`/docker/.env`](./docker/.env) file.


### RDF Validator API

This service encapsulates the actual validation engine and exposes its functionality as an API.

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Port | 4010 | VALIDATOR_API_PORT|

*NOTE:* When validating SPARQL endpoints, the fully qualified domain name of the machine must be specified. As a consequence, `localhost` will not work.

### RDF Validator UI

|Description | Value | Associated variable|
|------------|-------|--------------------|
| Port | 8010 | VALIDATOR_UI_PORT|

*NOTE:* When validating SPARQL endpoints, the fully qualified domain name of the machine must be specified. As a consequence, `localhost` will never work.

# Requirements

### Software requirements 

A Linux distribution having a kernel with a version higher than 5.4.0.

### Ports

The following ports must be available on the host machine, as they will be bound to by different docker services:

|Port | Service|
|------------|-------|
|4010| RDF Validator API|
|8010| RDF Validator user interface|


# Deployment

### Install the Docker engine

 Please follow the official instructions located [here](https://docs.docker.com/engine/install/ubuntu/).
 
### Install Docker compose

Please follow the official instructions located [here](https://docs.docker.com/compose/install/).


### Clone the lam-workflow repository to your target machine
 
 Open a shell and paste the following line, then press `<Enter>`:

```
git clone https://github.com/meaningfy-ws/lam-workflow.git
``` 

### Download the docker images and start the containers

In the same shell, navigate to the repository "lam-workflow" (where Git cloned the repository).

To setup the custom validator run
```shell script
make location=</your-custom/shapes/location> validator-set-shacl-shapes
```

After this preparation command, run 
```shell script
make start-services
 ```
in the shell window.


# Contributing
You are more than welcome to help expand and mature this project. 

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions with the project.  

# Licence 

The documents, such as reports and specifications, available in the /doc folder, are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The scripts (stylesheets) and other executables are licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) licence.
