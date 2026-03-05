#!/bin/bash

# OpenSpider Installation Script
# This script will attempt to install Node if missing, clone the repo, build it, and link the CLI.

set -e

REPO_URL="https://github.com/vbalaraman0406/OpenSpider.git"
INSTALL_DIR="$HOME/.openspider"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🕷️ Starting OpenSpider Installation...${NC}\n"

# 1. Check for Node.js
if ! command -v node >/dev/null 2>&1; then
    echo -e "${YELLOW}Node.js is not installed. Attempting to install Node.js via NVM...${NC}"
    # Install NVM
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    
    # Load NVM for this shell session
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
    
    # Install latest LTS Node
    nvm install 22
    nvm use 22
    nvm alias default 22
    echo -e "${GREEN}Node.js installed successfully: $(node -v)${NC}\n"
else
    NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$NODE_VERSION" -lt 22 ]; then
        echo -e "${RED}Error: OpenSpider requires Node.js version 22 or higher.${NC}"
        echo -e "${YELLOW}You currently have Node.js $(node -v). Please upgrade and run this script again.${NC}"
        # We could try to upgrade here, but it's safer to let the user knowingly upgrade.
        exit 1
    fi
    echo -e "${GREEN}✔ Node.js $(node -v) detected.${NC}\n"
fi

# 2. Clone the repository
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}OpenSpider directory already exists at $INSTALL_DIR. Updating repository...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo -e "${GREEN}Cloning OpenSpider to $INSTALL_DIR...${NC}"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""

# 3. Install dependencies and build
echo -e "${GREEN}Installing dependencies and building OpenSpider...${NC}"
echo "This might take a minute..."
npm install

echo -e "\n${GREEN}Building backend and frontend...${NC}"
npm run build

echo ""

# 4. Link the command globally and install PM2
echo -e "${GREEN}Installing PM2 (process manager) and linking 'openspider' globally...${NC}"
npm install -g pm2 || sudo npm install -g pm2
npm link || sudo npm link

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}🕷️ OpenSpider installed successfully! 🎉${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "\n${YELLOW}To get started, run the following command in your terminal:${NC}"
echo -e "  openspider onboard\n"
echo -e "If you installed NVM during this script, you may need to restart your terminal first."

