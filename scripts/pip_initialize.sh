#!/bin/bash

cd /home/deploy/FeePick

sudo apt update
sudo apt -y upgrade

source venv/bin/activate

pip install -r --ignore-installed requirements.txt