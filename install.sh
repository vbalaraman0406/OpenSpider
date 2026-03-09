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

# 4. Install PM2 process manager
echo -e "${GREEN}Installing PM2 (process manager)...${NC}"
npm install -g pm2 --unsafe-perm || sudo npm install -g pm2 --unsafe-perm

echo ""

# 5. Link the command globally
echo -e "${GREEN}Linking the 'openspider' global command...${NC}"
npm link --unsafe-perm || sudo npm link --unsafe-perm

# 6. Ensure NVM and npm global bin are in PATH permanently and for this session
NVM_SNIPPET='
# NVM (Node Version Manager) - added by OpenSpider installer
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'

# Detect shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

if [ -n "$SHELL_PROFILE" ]; then
    if ! grep -q 'NVM_DIR' "$SHELL_PROFILE" 2>/dev/null; then
        echo -e "${GREEN}Adding NVM to $SHELL_PROFILE for future sessions...${NC}"
        echo "$NVM_SNIPPET" >> "$SHELL_PROFILE"
    fi
    # Source immediately so the current shell session picks it up
    # shellcheck disable=SC1090
    source "$SHELL_PROFILE" 2>/dev/null || true
fi

# Also load NVM and update PATH for the current session directly
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add npm global bin to PATH for the current session
NPM_BIN=$(npm bin -g 2>/dev/null || npm root -g | sed 's|/node_modules||')/bin
if [ -d "$NPM_BIN" ]; then
    export PATH="$NPM_BIN:$PATH"
fi

echo -e "\n${GREEN}==========================================${NC}"
echo -e "${GREEN}🕷️ OpenSpider installed successfully! 🎉${NC}"
echo -e "${GREEN}==========================================${NC}"
echo -e "\n${YELLOW}To get started, run:${NC}"
echo -e "  openspider onboard\n"
