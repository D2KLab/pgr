#!/bin/bash

python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt

cd doccano_api_client
pip3 install -e ./
cd ..

python3 api/rest.py