#!/bin/bash
# Card Collector - Double-click Setup for macOS
# This file can be double-clicked in Finder to run the setup

# Change to the script directory
cd "$(dirname "$0")" || exit 1

# Run the setup script
./setup_macos.sh

# Keep terminal open
echo
echo "Press Enter to close this window..."
read -r