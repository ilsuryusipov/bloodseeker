#!/bin/bash

# Status working service
systemctl --user status bot.service
echo ""
echo "---"
echo ""
systemctl --user status player.service
