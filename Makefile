include docker/.env

BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

build-volumes:
	@ docker volume create rdf-validator-shacl-shapes

start-services:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the containers'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env up -d

stop-services:
	@ echo -e '$(BUILD_PRINT)(dev) Stopping the containers'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env stop

#-----------------------------------------------------------------------------
# custom configuration commands
#-----------------------------------------------------------------------------

set-shacl-shapes:
	@ echo "$(BUILD_PRINT)Copying custom SHACL shapes"
	@ [ "$(location)" ] || ( echo ">> template 'location' is not set"; exit 1 )
	@ docker rm temp | true
	@ docker volume rm rdf-validator-shacl-shapes | true
	@ docker volume create rdf-validator-shacl-shapes
	@ docker container create --name temp -v rdf-validator-shacl-shapes:/data busybox
	@ docker cp $(location). temp:/data
	@ docker rm temp
