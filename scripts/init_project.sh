#!/bin/bash

# Initialize MIA RAG Project
# Author: Persphone Raskova
# Repository: https://github.com/percy-raskova/marxists.org-rag-db

set -e

echo "🚀 Initializing MIA RAG System Project"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this script from the project root"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: MIA RAG System development environment

- Complete development environment for 6 parallel Claude Code instances
- Mise task orchestration system
- Poetry dependency management
- TDD with 80% coverage requirement
- Interface contracts v1.0.0
- Pre-commit hooks with boundary protection

Author: Persphone Raskova"
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already initialized"
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version (>= $required_version required)"
else
    echo "❌ Python $python_version is too old (>= $required_version required)"
    exit 1
fi

# Install Poetry if not present
if ! command -v poetry &> /dev/null; then
    echo ""
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Poetry installed"
else
    echo "✅ Poetry is already installed"
fi

# Install Mise if not present
if ! command -v mise &> /dev/null; then
    echo ""
    echo "📦 Installing Mise..."
    curl https://mise.run | sh
    export PATH="$HOME/.local/bin:$PATH"
    eval "$(mise activate bash)"
    echo "✅ Mise installed"
else
    echo "✅ Mise is already installed"
fi

# Install base dependencies
echo ""
echo "📦 Installing Python dependencies..."
poetry install --only main,dev
echo "✅ Dependencies installed"

# Install pre-commit hooks
echo ""
echo "🔗 Installing pre-commit hooks..."
poetry run pre-commit install
echo "✅ Pre-commit hooks installed"

# Check for MIA archive
echo ""
echo "📚 Checking for MIA archive..."
archive_path="/home/user/Downloads/dump_www-marxists-org/www.marxists.org.tar.gz.part"
if [ -f "$archive_path" ]; then
    size=$(du -h "$archive_path" | cut -f1)
    echo "✅ Found partial archive: $size (195GB of 200GB)"
    echo "ℹ️  Resume download from: https://archive.org/details/dump_www-marxists-org"
else
    echo "⚠️  MIA archive not found"
    echo "Download from: https://archive.org/details/dump_www-marxists-org"
fi

# Create work-logs directory
mkdir -p work-logs
touch work-logs/.gitkeep

# Display instance selection
echo ""
echo "🤖 Claude Code Instance Setup"
echo "=============================="
echo "To set up a specific instance (1-6), run:"
echo ""
echo "  mise run instance1:setup  # Storage & Pipeline"
echo "  mise run instance2:setup  # Embeddings"
echo "  mise run instance3:setup  # Weaviate"
echo "  mise run instance4:setup  # API"
echo "  mise run instance5:setup  # MCP"
echo "  mise run instance6:setup  # Monitoring"
echo ""
echo "Or manually:"
echo "  python scripts/identify_instance.py --set instance<N>"
echo ""

# Show available Mise tasks
echo "📋 Available Mise Tasks"
echo "======================="
mise tasks | head -20
echo ""
echo "Run 'mise tasks' to see all available tasks"

# Final message
echo ""
echo "✨ Project initialization complete!"
echo ""
echo "Next steps:"
echo "1. Choose your instance: mise run instance<N>:setup"
echo "2. Read documentation: AI-AGENT-INSTRUCTIONS.md"
echo "3. Check boundaries: INSTANCE-BOUNDARIES.md"
echo "4. Start with TDD: Write tests first!"
echo ""
echo "Repository: https://github.com/percy-raskova/marxists.org-rag-db"
echo ""
echo "Happy coding! 🚩"