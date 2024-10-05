#!/bin/bash

source $NVM_DIR/nvm.sh && nvm install 18 && \
    yarn global add \
        serverless \
        serverless-python-requirements \
        serverless-dotenv-plugin \
        serverless-offline \
        serverless-plugin-git-variables \
        serverless-plugin-warmup
pip3 install black autopep8 yapf bandit flake8 mypy pycodestyle pydocstyle pylint
python3 -m pip install --upgrade pip