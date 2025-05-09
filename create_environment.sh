#!/bin/bash

python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

echo '########################################################'
echo "Environment created in .venv"
echo "Run 'source .venv/bin/activate' to activate it"
echo '########################################################'


