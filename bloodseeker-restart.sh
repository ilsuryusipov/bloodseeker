#!/bin/bash

# Restart working service
systemctl --user restart bot.service
systemctl --user restart player.service
