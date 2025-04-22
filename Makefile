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
#ENV_SECRETS_FILE_PATH = $(PROJECT_PATH)/.env.secrets
INFRA_FOLDER_PATH = $(PROJECT_PATH)/docker
REQUIREMENTS_FOLDER_PATH = $(PROJECT_PATH)/requirements

PROJECT_NAME = $(notdir $(PROJECT_PATH))

# ==============================================================================
# Define commands
# ==============================================================================
.PHONY: update-env build-% start-services stop-services build-all check-uv start-%

start-services: build-all
	@ $(call echo_message,$(ICON_PROGRESS),Starting $(PROJECT_NAME) services)
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) up -d --force-recreate
	@ $(call echo_message,$(ICON_DONE),Starting $(PROJECT_NAME) services si complete)

start-%: build-%
	@ $(call echo_message,$(ICON_PROGRESS),Starting $(PROJECT_NAME) $* service)
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) up $* -d --force-recreate
	@ $(call echo_message,$(ICON_DONE),Starting $(PROJECT_NAME) $* service si complete)

stop-services:
	@ $(call echo_message,$(ICON_PROGRESS),Stoping $(PROJECT_NAME) services)
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) stop
	@ $(call echo_message,$(ICON_DONE),Stoping $(PROJECT_NAME) services is complete)

update-requirements: check-uv
	@ $(call echo_message,$(ICON_PROGRESS),Updating $(PROJECT_NAME) requirements)
	@ uv sync
	@ uv export -o $(REQUIREMENTS_FOLDER_PATH)/common.txt --no-group dev --no-group docs --no-cache --no-header --quiet --no-hashes
	@ uv export -o $(REQUIREMENTS_FOLDER_PATH)/dev.txt --all-groups --no-cache --no-header --quiet --no-hashes
	@ $(call echo_message,$(ICON_DONE),Requirements for $(PROJECT_NAME) services are updated)

check-uv:
	@command -v uv > /dev/null 2>&1 || { \
		echo "$(ICON_ERROR) Error: 'uv' is not installed."; \
		echo "$(ICON_WARNING) Please install it. Source: https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; \
	}

build-%:
	@ $(call echo_message,$(ICON_PROGRESS),Building $(*) for $(PROJECT_NAME))
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) build $*
	@ $(call echo_message,$(ICON_DONE),Building $(*) completed for $(PROJECT_NAME))

build-all:
	@ $(call echo_message,$(ICON_PROGRESS),Building all for $(PROJECT_NAME))
	@ docker-compose --file $(INFRA_FOLDER_PATH)/docker-compose.yml --env-file $(ENV_FILE_PATH) build
	@ $(call echo_message,$(ICON_DONE),Building all completed for $(PROJECT_NAME))