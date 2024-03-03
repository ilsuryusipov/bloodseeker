#!/bin/bash

# Stop working service
systemctl --user stop bot.service
systemctl --user stop player.service

# Create log folder
mkdir -p ./logs

# Create UrlsList.txt
touch ./UrlsList.txt

# Install unit-files
mkdir -p ~/.config/systemd/user/
cp -v *.service ~/.config/systemd/user

# Reload unit-files
systemctl --user daemon-reload

# Enable services to start at system statup
systemctl --user enable bot.service
systemctl --user enable player.service

# First run
systemctl --user start bot.service
systemctl --user start player.service

# pip3 install req
# install tor
# install vlc
