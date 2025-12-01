#!/bin/bash

# Configuration
PYTHON_VERSION="python3.12"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
APP_SCRIPT="server.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AURA System Setup...${NC}"

# 1. Check for Python 3.12
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo -e "${RED}Error: $PYTHON_VERSION could not be found.${NC}"
    echo "Please install Python 3.12 to proceed."
    exit 1
fi

# 2. Check/Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment with $PYTHON_VERSION...${NC}"
    $PYTHON_VERSION -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created.${NC}"
    
    # Activate and Install Dependencies
    source $VENV_DIR/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip install -r $REQUIREMENTS_FILE
    else
        echo -e "${RED}Warning: $REQUIREMENTS_FILE not found.${NC}"
    fi
else
    echo -e "${GREEN}Virtual environment found.${NC}"
    source $VENV_DIR/bin/activate
fi

# 5. Run Application
echo -e "${GREEN}Starting Application...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop.${NC}"
python $APP_SCRIPT
