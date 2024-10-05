#!/bin/bash

echo "-- Update node packages --"
source $NVM_DIR/nvm.sh && nvm use 18 && \
    yarn global upgrade \
        serverless \
        serverless-python-requirements \
        serverless-dotenv-plugin \
        serverless-offline \
        serverless-plugin-git-variables \
        serverless-plugin-warmup \
    --latest
echo "-- Update python packages --"
python3 -m pip install --upgrade pip
pip3 install black autopep8 yapf bandit flake8 mypy pycodestyle pydocstyle pylint