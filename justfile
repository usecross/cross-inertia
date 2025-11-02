# Justfile for Cross-Inertia
# Run `just` to see all available commands

# Default recipe - show available commands
default:
    @just --list

# Install FastAPI demo dependencies
demo-install:
    @echo "📦 Installing Python dependencies with uv..."
    uv sync
    @echo ""
    @echo "📦 Installing frontend dependencies..."
    cd examples/fastapi && bun install
    @echo ""
    @echo "✅ All demo dependencies installed!"

# Run the FastAPI demo (both servers)
demo-fastapi:
    @echo "🚀 Starting FastAPI demo..."
    @echo "  - Vite dev server: http://localhost:5173"
    @echo "  - FastAPI server:  http://127.0.0.1:8000"
    @echo ""
    @echo "Open http://127.0.0.1:8000 in your browser"
    @echo ""
    @echo "Press Ctrl+C to stop both servers"
    @echo ""
    @just _run-servers

# Build the FastAPI demo for production
demo-build:
    @echo "🏗️  Building FastAPI demo for production..."
    cd examples/fastapi && bun run build
    @echo "✅ Build complete!"

# Clean demo build artifacts
demo-clean:
    @echo "🧹 Cleaning demo build artifacts..."
    cd examples/fastapi && rm -rf static/build .vite node_modules bun.lockb
    @echo "✅ Clean complete!"

# Internal recipe for running servers
_run-servers:
    #!/usr/bin/env bash
    set -euo pipefail
    
    cd examples/fastapi
    
    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo "⚠️  Frontend dependencies not installed."
        echo "   Run: just demo-install"
        exit 1
    fi
    
    # Trap to kill all background jobs on exit
    trap 'kill 0' SIGINT SIGTERM EXIT
    
    # Start Vite dev server
    bun run dev &
    VITE_PID=$!
    
    # Wait for Vite to start
    sleep 2
    
    # Start FastAPI server (run from root so uv finds workspace)
    cd ../..
    uv run --directory examples/fastapi fastapi dev examples/fastapi/main.py &
    API_PID=$!
    
    # Wait for both processes
    wait $VITE_PID $API_PID
