#!/bin/sh
sudo apt-get update  # To get the latest package lists
sudo apt-get --assume-yes install python3
sudo apt-get --assume-yes install python3-pip
pip3 install pyrebase
pip install Flask
