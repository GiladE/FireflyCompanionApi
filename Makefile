SHELL := /bin/bash
VENV_NAME?=venv
CMD?=help
DEPS_ENV?=dev
PYTHON=${VENV_NAME}/bin/python
IPYTHON=${VENV_NAME}/bin/ipython

SHELL := /bin/bash

.SILENT: $(VENV_NAME)/bin/activate help prepare-venv shell serve


help: ## This help
	@echo -e "\033[1m$(shell basename $(CURDIR))\033[0m" && echo 'Usage:' && echo '  make <target>' && echo '' && echo 'Targets:' && grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}' && echo ''


s: serve
serve: prepare-venv ## Run serverless offline
	AWS_ACCESS_KEY_ID=nothing AWS_SECRET_ACCESS_KEY=nothing serverless offline --noSponsor


prepare-venv: $(VENV_NAME)/bin/activate ## Install venv and install deps (Will install requirements.$DEPS_ENV.txt
$(VENV_NAME)/bin/activate: requirements.txt requirements.dev.txt requirements.production.txt
	if [ ! -d $(VENV_NAME) ]; then echo "==   Creating new venv (./$(VENV_NAME))" && python3 -m venv $(VENV_NAME);	fi
	${PYTHON} -m pip install --upgrade pip
	echo '==   Install requirements.txt' && ${PYTHON} -m pip install -r requirements.txt
	if [ -z ${BAD_ENV_WARNING} ]; then echo '==   Install requirements.${DEPS_ENV}.txt' && ${PYTHON} -m pip install -r requirements.${DEPS_ENV}.txt; else echo '==   ⚠️ Skipping requirements.${DEPS_ENV}.txt does not exist'; fi
	touch $(VENV_NAME)/bin/activate


shell: prepare-venv ## Open development console
	echo -e "==   Start shell\n"
	AWS_ACCESS_KEY_ID=nothing AWS_SECRET_ACCESS_KEY=nothing IPYTHONDIR=./.ipython ${IPYTHON}
