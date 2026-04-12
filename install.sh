#!/bin/bash

# ANSI colors for styling
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🛡️ Installing GitGuard DevOps Governance Tool...${NC}"

# 1. Copy the hook into the local Git repository
cp commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
echo -e "✅ Git hook successfully installed."

# 2. Boot up the Docker containers in the background (-d)
echo -e "🐳 Starting GitGuard Engine and Dashboard via Docker..."
docker-compose up -d --build

echo -e "${GREEN}🚀 Installation Complete!${NC}"
echo -e "📊 View your Analytics Dashboard here: http://localhost:8501"