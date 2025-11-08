#!/bin/bash
# Install git hooks for MIA RAG System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Installing Git Hooks for MIA RAG      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    echo "Run this script from the project root."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Function to install a hook
install_hook() {
    local hook_name=$1
    local source_file=".githooks/$hook_name"
    local target_file=".git/hooks/$hook_name"

    if [ -f "$source_file" ]; then
        echo -e "${YELLOW}Installing $hook_name hook...${NC}"

        # Backup existing hook if it exists
        if [ -f "$target_file" ] && [ ! -L "$target_file" ]; then
            echo -e "${YELLOW}  Backing up existing $hook_name to $target_file.backup${NC}"
            mv "$target_file" "$target_file.backup"
        fi

        # Create symlink
        ln -sf "../../$source_file" "$target_file"

        # Make executable
        chmod +x "$source_file"

        echo -e "${GREEN}  ✅ $hook_name hook installed${NC}"
    else
        echo -e "${YELLOW}  ⚠️  $hook_name hook not found at $source_file${NC}"
    fi
}

# Install hooks
echo -e "${BLUE}Installing hooks...${NC}"
echo ""

install_hook "pre-commit"
install_hook "commit-msg"
install_hook "pre-push"

echo ""

# Configure git to use hooks directory (alternative method)
echo -e "${BLUE}Configuring git hooks path...${NC}"
git config core.hooksPath .githooks
echo -e "${GREEN}✅ Git configured to use .githooks directory${NC}"

echo ""

# Check Python dependencies for hooks
echo -e "${BLUE}Checking Python dependencies...${NC}"

# Check if required Python packages are available
REQUIRED_PACKAGES=("click" "rich" "pyyaml")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing Python packages for hooks:${NC}"
    echo "  ${MISSING_PACKAGES[*]}"
    echo ""
    echo "Install with:"
    echo "  poetry install --only dev"
    echo "or:"
    echo "  pip install ${MISSING_PACKAGES[*]}"
else
    echo -e "${GREEN}✅ All required Python packages available${NC}"
fi

echo ""

# Check if scripts exist
echo -e "${BLUE}Checking required scripts...${NC}"

REQUIRED_SCRIPTS=(
    "scripts/check_boundaries.py"
    "scripts/check_interfaces.py"
    "scripts/check_todos.py"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}  ✅ $script found${NC}"
    else
        echo -e "${RED}  ❌ $script missing${NC}"
    fi
done

echo ""

# Test hooks (optional)
echo -e "${BLUE}Testing hooks...${NC}"

# Test pre-commit hook
if [ -x .githooks/pre-commit ]; then
    echo -e "${YELLOW}Testing pre-commit hook (dry run)...${NC}"
    # Create a temporary test scenario
    echo "# Test file" > /tmp/test_hook.py

    # Set instance for testing
    if [ ! -f .instance ]; then
        echo "instance1" > .instance.test
        TEST_INSTANCE=true
    fi

    # Run hook in test mode (just check it executes)
    if bash -c "cd $(pwd) && .githooks/pre-commit --dry-run 2>/dev/null || true"; then
        echo -e "${GREEN}  ✅ pre-commit hook is executable${NC}"
    fi

    # Clean up test instance
    if [ "$TEST_INSTANCE" = true ]; then
        rm -f .instance.test
    fi
fi

# Test commit-msg hook
if [ -x .githooks/commit-msg ]; then
    echo -e "${YELLOW}Testing commit-msg hook...${NC}"
    echo "feat(test): test commit message" > /tmp/test_commit_msg

    if .githooks/commit-msg /tmp/test_commit_msg >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ commit-msg hook validated test message${NC}"
    else
        echo -e "${YELLOW}  ⚠️  commit-msg hook test failed (this is OK)${NC}"
    fi

    rm -f /tmp/test_commit_msg
fi

echo ""

# Show hook configuration status
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Hook Installation Complete       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Git hooks are now active and will run on:${NC}"
echo "  • pre-commit  - Boundary checking, secret scanning, linting"
echo "  • commit-msg  - Conventional commit format validation"
echo "  • pre-push    - Interface validation, test verification"
echo ""

echo -e "${YELLOW}To bypass hooks temporarily (not recommended):${NC}"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""

echo -e "${YELLOW}To uninstall hooks:${NC}"
echo "  git config --unset core.hooksPath"
echo "  rm .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push"
echo ""

# Check if running as part of larger setup
if [ "$1" != "--quiet" ]; then
    echo -e "${GREEN}✨ Git hooks successfully installed!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Set your instance: mise run identify"
    echo "  2. Make a test commit to verify hooks"
    echo "  3. Review hook output on your first commit"
fi

exit 0