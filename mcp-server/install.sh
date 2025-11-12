#!/bin/bash
# Installation script for Agent Management Platform MCP Server

set -e

echo "🚀 Installing Agent Management Platform MCP Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in editable mode
echo "📥 Installing package..."
pip install -e .

# Install development dependencies
read -p "Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install -e ".[dev]"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY if you want to use LLM execution"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ../../.agents/tasks
mkdir -p ../../.agents/projects

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY (optional)"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the server: python -m agent_mcp"
echo ""
echo "For Claude Desktop integration, add this to your config:"
echo ""
echo '  "agent-management": {'
echo '    "command": "python",'
echo '    "args": ["-m", "agent_mcp"],'
echo "    \"cwd\": \"$(pwd)/src\""
echo '  }'
echo ""
