#!/bin/bash

cd /home/deploy/FeePick

sudo apt update
sudo apt -y upgrade

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt