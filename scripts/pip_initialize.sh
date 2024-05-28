#!/bin/bash

cd /home/deploy/FeePick

sudo apt update
sudo apt upgrade

python -m venv venv
source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt