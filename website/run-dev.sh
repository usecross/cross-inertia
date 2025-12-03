#!/bin/bash

# Start both Vite and FastAPI dev servers
# Usage: ./run-dev.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Cross-Inertia Docs development servers...${NC}"

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo -e "${RED}Error: bun is not installed${NC}"
    echo "Install it from https://bun.sh"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    bun install
fi

# Start Vite in background
echo "Starting Vite dev server on http://localhost:5173..."
bun run dev &
VITE_PID=$!

# Give Vite a moment to start
sleep 2

# Start FastAPI
echo "Starting FastAPI dev server on http://localhost:8000..."
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Cleanup on exit
trap "kill $VITE_PID 2>/dev/null" EXIT
