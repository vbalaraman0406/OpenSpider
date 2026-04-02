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

# 1b. Check for Docker (Required for True Execution Sandboxing)
echo -e "${GREEN}Verifying Docker installation (Required for Sandboxing)...${NC}"
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${YELLOW}Docker is not installed. Attempting to install Docker...${NC}"
    if [ "$(uname)" = "Darwin" ]; then
        if command -v brew >/dev/null 2>&1; then
            echo -e "${GREEN}Installing Docker via Homebrew...${NC}"
            brew install --cask docker || echo -e "${RED}Failed to install Docker. Please install Docker Desktop manually.${NC}"
            echo -e "${YELLOW}⚠️ IMPORTANT: You must launch Docker from your strictly applications folder manually to complete setup!${NC}\n"
        else
            echo -e "${RED}Homebrew not found. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop/${NC}\n"
        fi
    elif [ "$(uname)" = "Linux" ]; then
        echo -e "${GREEN}Installing Docker via official script...${NC}"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh || echo -e "${RED}Failed to install Docker. Please install manually.${NC}"
        sudo usermod -aG docker $USER || true
        rm -f get-docker.sh
        echo -e "${YELLOW}⚠️ IMPORTANT: Please log out and back in for Docker group permissions to take effect.${NC}\n"
    fi
else
    echo -e "${GREEN}✔ Docker is installed: $(docker --version)${NC}\n"
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

# 3b. Install Playwright browser (Chromium) for agent browsing
echo -e "${GREEN}Installing Playwright browser (Chromium)...${NC}"
npx playwright install chromium || echo -e "${YELLOW}⚠️  Playwright browser install failed (non-fatal)${NC}"

# Install system dependencies on Linux
if [ "$(uname)" = "Linux" ]; then
    echo -e "${GREEN}Installing Playwright system dependencies...${NC}"
    npx playwright install-deps chromium 2>/dev/null || sudo npx playwright install-deps chromium 2>/dev/null || echo -e "${YELLOW}⚠️  Could not install system deps. Run manually: sudo npx playwright install-deps chromium${NC}"
fi

echo ""

# 4. Install PM2 process manager
echo -e "${GREEN}Installing PM2 (process manager)...${NC}"
npm install -g pm2 --unsafe-perm || sudo npm install -g pm2 --unsafe-perm

# 4b. Configure PM2 to auto-start on boot
echo -e "${GREEN}Configuring PM2 to start on boot...${NC}"
# Get the startup command PM2 generates and execute it
PM2_STARTUP_CMD=$(pm2 startup 2>&1 | grep 'sudo' | head -1)
if [ -n "$PM2_STARTUP_CMD" ]; then
    echo -e "${YELLOW}Running PM2 startup command (may require password):${NC}"
    eval "$PM2_STARTUP_CMD" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  PM2 auto-start setup requires sudo. Run this manually after install:${NC}"
        echo -e "  ${PM2_STARTUP_CMD}"
        echo -e "${YELLOW}  Then run: pm2 save${NC}"
    }
    echo -e "${GREEN}✔ PM2 configured for auto-start on boot${NC}"
else
    # On some systems pm2 startup works without sudo
    pm2 startup 2>/dev/null || echo -e "${YELLOW}⚠️  Could not configure PM2 auto-start. Run 'pm2 startup' manually.${NC}"
fi

echo ""

# 5. Link the command globally
echo -e "${GREEN}Linking the 'openspider' global command...${NC}"
npm link --unsafe-perm || sudo npm link --unsafe-perm

# 5b. Create a system-wide symlink so ALL users on this machine can run openspider
OPENSPIDER_BIN=$(which openspider 2>/dev/null || npm bin -g 2>/dev/null)/openspider
if [ -f "$OPENSPIDER_BIN" ]; then
    ln -sf "$OPENSPIDER_BIN" /usr/local/bin/openspider 2>/dev/null || sudo ln -sf "$OPENSPIDER_BIN" /usr/local/bin/openspider
    echo -e "${GREEN}✔ System-wide symlink created at /usr/local/bin/openspider${NC}"
else
    # Fallback: find the binary and symlink it
    OPENSPIDER_BIN=$(find "$HOME/.nvm" /usr/local/lib /usr/lib -name "openspider" -type f 2>/dev/null | head -1)
    if [ -n "$OPENSPIDER_BIN" ]; then
        ln -sf "$OPENSPIDER_BIN" /usr/local/bin/openspider 2>/dev/null || sudo ln -sf "$OPENSPIDER_BIN" /usr/local/bin/openspider
        echo -e "${GREEN}✔ System-wide symlink created at /usr/local/bin/openspider${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not create system-wide symlink. Other users may need to add NVM to their PATH manually.${NC}"
    fi
fi

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
