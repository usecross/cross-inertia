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
    ./examples/fastapi/run-dev.sh

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
