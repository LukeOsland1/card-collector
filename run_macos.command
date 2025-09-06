#!/bin/bash
# Card Collector - Double-click Run for macOS
# This file can be double-clicked in Finder to start the application

# Change to the script directory
cd "$(dirname "$0")" || exit 1

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================"
echo "   Card Collector - macOS Launcher"
echo "============================================"
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please run setup first:"
    echo "  Double-click: setup.command"
    echo "  Or in terminal: ./setup_macos.sh"
    echo
    echo "Press Enter to exit..."
    read -r
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import discord, fastapi, uvicorn" 2>/dev/null; then
    echo -e "${RED}Error: Dependencies not installed${NC}"
    echo "Installing dependencies..."
    if [ -f "install_deps.py" ]; then
        python3 install_deps.py
    else
        python3 -m pip install -r requirements.txt
    fi
fi

echo -e "${GREEN}Starting Card Collector...${NC}"
echo
echo "Services will be available at:"
echo "  - Discord Bot: Check your Discord server for /card commands"
echo "  - Web Interface: http://localhost:8080"
echo "  - API Documentation: http://localhost:8080/docs"
echo
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo

# Start the application
python3 run.py

# Keep terminal open on exit
echo
echo "Card Collector stopped."
echo "Press Enter to close this window..."
read -r