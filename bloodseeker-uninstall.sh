#!/bin/bash

# Stop working service
systemctl --user stop bot.service
systemctl --user stop player.service

# Install unit-files
rm ~/.config/systemd/user/*.service

# Reload unit-files
systemctl --user daemon-reload
