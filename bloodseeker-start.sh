#!/bin/bash

# Restart working service
systemctl --user start bot.service
systemctl --user start player.service
