include docker/.env

BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

start-services:
	@ echo -e '$(BUILD_PRINT)(dev) Starting the containers'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env up -d

stop-services:
	@ echo -e '$(BUILD_PRINT)(dev) Stopping the containers'
	@ docker-compose --file docker/docker-compose.yml --env-file docker/.env stop
