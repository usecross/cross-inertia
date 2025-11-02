#!/bin/bash
# Development runner script for the Inertia FastAPI example

echo "🚀 Starting Inertia FastAPI Example..."
echo ""

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo "⚠️  Bun not found. Using npm instead."
    echo "   Install Bun for faster package management: https://bun.sh"
    PKG_MANAGER="npm"
else
    PKG_MANAGER="bun"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    $PKG_MANAGER install
    echo ""
fi

echo "Starting servers..."
echo "  - Vite dev server: http://localhost:5173"
echo "  - FastAPI server:  http://127.0.0.1:8000"
echo ""
echo "Open http://127.0.0.1:8000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start both servers
trap 'kill 0' SIGINT  # Kill all background processes on Ctrl+C

# Start Vite dev server
$PKG_MANAGER run dev &

# Wait a moment for Vite to start
sleep 2

# Start FastAPI server (let Python find the package from parent venv)
uv run fastapi dev main.py

# Wait for all background processes
wait
