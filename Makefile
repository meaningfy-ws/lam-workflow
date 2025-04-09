# ==============================================================================
# Define messaging
# ==============================================================================

# Begin print color
BPC = \e[1;34m
# End print color
EPC = \e[0m

ICON_DONE = [✔]
ICON_ERROR = [x]
ICON_WARNING = [!]
ICON_PROGRESS = [-]

# Usage: $(call echo_message,ICON,MESSAGE)
define echo_message
	@ echo -e '$(BPC)$(1) $(2) $(EPC)'
endef

# ==============================================================================
# Define environment variables
# ==============================================================================

SHELL=/bin/bash -o pipefail

PROJECT_PATH = $(shell pwd)
ENV_FILE_PATH = $(PROJECT_PATH)/.env
ENV_SECRETS_FILE_PATH = $(PROJECT_PATH)/.env.secrets
INFRA_FOLDER_PATH = $(PROJECT_PATH)/docker

PROJECT_NAME = $(notdir $(PROJECT_PATH))

# ==============================================================================
# Define commands
# ==============================================================================
.PHONY: update-env build-% start-services stop-services build-all

start-services: update-env
	@ $(call echo_message,$(ICON_PROGRESS),Starting $(PROJECT_NAME) services)
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) up -d --force-recreate
	@ $(call echo_message,$(ICON_DONE),Starting $(PROJECT_NAME) services si complete)

stop-services: update-env
	@ $(call echo_message,$(ICON_PROGRESS),Stoping $(PROJECT_NAME) services)
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) stop
	@ $(call echo_message,$(ICON_DONE),Stoping $(PROJECT_NAME) services is complete)

update-env:
	@ $(call echo_message,$(ICON_PROGRESS),Updating .env file)
	@ echo -e "\n# The following are secret environment variables:\n" > $(ENV_FILE_PATH)
	@ cat $(ENV_SECRETS_FILE_PATH) >> $(ENV_FILE_PATH)
	@ echo -e "\n\n# The following are technical environment variables:\n" >> $(ENV_FILE_PATH)
	@ echo PROJECT_PATH=${PROJECT_PATH} >> $(ENV_FILE_PATH)
	@ echo ENV_FILE_PATH=${ENV_FILE_PATH} >> $(ENV_FILE_PATH)
	@ echo INFRA_FOLDER_PATH=${INFRA_FOLDER_PATH} >> $(ENV_FILE_PATH)
	@ echo PROJECT_NAME=${PROJECT_NAME} >> $(ENV_FILE_PATH)
	@ $(call echo_message,$(ICON_DONE),.env file has been updated)

build-%: update-env
	@ $(call echo_message,$(ICON_PROGRESS),Building $(*) for $(PROJECT_NAME))
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) up -d --force-recreate --build $*
	@ $(call echo_message,$(ICON_DONE),Building $(*) completed for $(PROJECT_NAME))

build-all: update-env
	@ $(call echo_message,$(ICON_PROGRESS),Building all for $(PROJECT_NAME))
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) up -d --force-recreate --build
	@ $(call echo_message,$(ICON_DONE),Building all completed for $(PROJECT_NAME))