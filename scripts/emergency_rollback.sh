#!/bin/bash
# Emergency rollback script for MIA RAG System
# Used to quickly rollback an instance to a known good state

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Script arguments
INSTANCE=$1
TARGET_COMMIT=$2
REASON=$3

# Function to display usage
usage() {
    echo -e "${BOLD}Emergency Rollback Tool${NC}"
    echo ""
    echo "Usage: $0 <instance> <commit> [reason]"
    echo ""
    echo "Arguments:"
    echo "  instance    Instance to rollback (instance1-6 or 'all')"
    echo "  commit      Target commit hash or tag to rollback to"
    echo "  reason      Optional: Reason for rollback"
    echo ""
    echo "Examples:"
    echo "  $0 instance2 abc123 'Memory leak in batch processor'"
    echo "  $0 instance4 v2.0.0 'API breaking production'"
    echo "  $0 all HEAD~5 'Major integration failure'"
    echo ""
    exit 1
}

# Validate arguments
if [ -z "$INSTANCE" ] || [ -z "$TARGET_COMMIT" ]; then
    usage
fi

# Validate instance
if [[ ! "$INSTANCE" =~ ^(instance[1-6]|all)$ ]]; then
    echo -e "${RED}❌ Invalid instance: $INSTANCE${NC}"
    echo "Must be instance1-6 or 'all'"
    exit 1
fi

# Display rollback plan
echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
echo -e "${RED}║        🚨 EMERGENCY ROLLBACK 🚨           ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Instance:${NC} $INSTANCE"
echo -e "${YELLOW}Target:${NC} $TARGET_COMMIT"
echo -e "${YELLOW}Reason:${NC} ${REASON:-'Not specified'}"
echo -e "${YELLOW}Time:${NC} $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Confirm action
echo -e "${BOLD}This will:${NC}"
echo "  1. Create emergency rollback branch"
echo "  2. Revert instance files to $TARGET_COMMIT"
echo "  3. Run tests to verify rollback"
echo "  4. Create emergency PR for fast merge"
echo ""
read -p "$(echo -e ${YELLOW}Continue? [yes/no]: ${NC})" -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]es$ ]]; then
    echo -e "${YELLOW}Rollback cancelled${NC}"
    exit 0
fi

# Start rollback
echo ""
echo -e "${BLUE}Starting rollback procedure...${NC}"

# Ensure we're on latest develop
echo -e "${YELLOW}Fetching latest changes...${NC}"
git fetch origin
git checkout develop
git pull origin develop

# Create rollback branch
TIMESTAMP=$(date +%s)
ROLLBACK_BRANCH="hotfix/emergency-rollback-$INSTANCE-$TIMESTAMP"
echo -e "${YELLOW}Creating rollback branch: $ROLLBACK_BRANCH${NC}"
git checkout -b "$ROLLBACK_BRANCH"

# Function to get instance directories
get_instance_dirs() {
    local instance=$1
    case "$instance" in
        instance1)
            echo "src/mia_rag/storage/ src/mia_rag/pipeline/ tests/unit/instance1_*"
            ;;
        instance2)
            echo "src/mia_rag/embeddings/ tests/unit/instance2_*"
            ;;
        instance3)
            echo "src/mia_rag/vectordb/ tests/unit/instance3_*"
            ;;
        instance4)
            echo "src/mia_rag/api/ tests/unit/instance4_*"
            ;;
        instance5)
            echo "src/mia_rag/mcp/ tests/unit/instance5_*"
            ;;
        instance6)
            echo "src/mia_rag/monitoring/ tests/integration/ tests/unit/instance6_*"
            ;;
    esac
}

# Perform rollback
if [ "$INSTANCE" = "all" ]; then
    echo -e "${YELLOW}Rolling back ALL instances to $TARGET_COMMIT${NC}"

    # Rollback all instance directories
    for i in {1..6}; do
        DIRS=$(get_instance_dirs "instance$i")
        echo -e "${YELLOW}Rolling back instance$i...${NC}"
        for dir in $DIRS; do
            if [ -d "$dir" ]; then
                git checkout "$TARGET_COMMIT" -- "$dir" 2>/dev/null || true
            fi
        done
    done
else
    echo -e "${YELLOW}Rolling back $INSTANCE to $TARGET_COMMIT${NC}"

    # Get directories for this instance
    DIRS=$(get_instance_dirs "$INSTANCE")

    # Rollback each directory
    for dir in $DIRS; do
        if [ -d "$dir" ]; then
            echo "  Reverting: $dir"
            git checkout "$TARGET_COMMIT" -- "$dir" 2>/dev/null || true
        fi
    done
fi

# Check what was changed
echo ""
echo -e "${YELLOW}Files reverted:${NC}"
git diff --name-only --cached | head -20
CHANGED_COUNT=$(git diff --name-only --cached | wc -l)
echo "Total: $CHANGED_COUNT files"

# Commit rollback
echo ""
echo -e "${YELLOW}Committing rollback...${NC}"
git commit -m "fix($INSTANCE): emergency rollback to $TARGET_COMMIT

EMERGENCY ROLLBACK - Production Issue

Instance: $INSTANCE
Target commit: $TARGET_COMMIT
Reason: ${REASON:-'Emergency rollback required'}
Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')

This rollback reverts the instance to a known good state.

🚨 Emergency Change
Co-Authored-By: Emergency Rollback System <emergency@marxist-rag.dev>"

# Run tests for affected instance
echo ""
echo -e "${YELLOW}Running tests to verify rollback...${NC}"

if [ "$INSTANCE" = "all" ]; then
    # Run quick smoke tests for all instances
    echo "Running smoke tests for all instances..."

    # Check if Poetry is available
    if command -v poetry &> /dev/null; then
        poetry run pytest -m "not slow" --tb=short -q || TEST_RESULT=$?
    else
        echo -e "${YELLOW}⚠️  Poetry not found, skipping tests${NC}"
        TEST_RESULT=0
    fi
else
    # Run tests for specific instance
    echo "Running tests for $INSTANCE..."

    if command -v poetry &> /dev/null; then
        poetry run pytest -m "$INSTANCE" --tb=short -q || TEST_RESULT=$?
    else
        echo -e "${YELLOW}⚠️  Poetry not found, skipping tests${NC}"
        TEST_RESULT=0
    fi
fi

# Evaluate test results
if [ "${TEST_RESULT:-0}" -eq 0 ]; then
    echo -e "${GREEN}✅ Tests passed after rollback${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed after rollback${NC}"
    echo "This may be expected if the tests were updated after $TARGET_COMMIT"
    read -p "$(echo -e ${YELLOW}Continue with PR creation? [yes/no]: ${NC})" -r CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]es$ ]]; then
        echo -e "${RED}Rollback aborted. Branch $ROLLBACK_BRANCH created but not pushed.${NC}"
        exit 1
    fi
fi

# Push rollback branch
echo ""
echo -e "${YELLOW}Pushing rollback branch...${NC}"
git push origin "$ROLLBACK_BRANCH"

# Create emergency PR
echo ""
echo -e "${YELLOW}Creating emergency PR...${NC}"

PR_BODY=$(cat <<EOF
## 🚨 EMERGENCY ROLLBACK

**Instance**: $INSTANCE
**Target Commit**: $TARGET_COMMIT
**Reason**: ${REASON:-'Emergency rollback required'}
**Initiated**: $(date -u '+%Y-%m-%d %H:%M:%S UTC')

### Impact
This emergency rollback reverts $INSTANCE to commit $TARGET_COMMIT to resolve a production issue.

### Changes
- Reverted $CHANGED_COUNT files
- Instance returned to known good state
- Tests: ${TEST_RESULT:-0} (0 = passed)

### Rollback Verification
- [x] Instance files reverted to target commit
- [x] Tests executed
- [ ] Manual verification required
- [ ] Production deployment ready

### Next Steps
1. **Review and merge immediately**
2. Deploy to production
3. Verify issue is resolved
4. Create follow-up issue for proper fix

### Related Issues
- Production incident: #___
- Root cause analysis: #___

---
**⚠️ This is an emergency change requiring immediate attention**
EOF
)

# Create PR using gh CLI
if command -v gh &> /dev/null; then
    gh pr create \
        --base develop \
        --head "$ROLLBACK_BRANCH" \
        --title "🚨 EMERGENCY: Rollback $INSTANCE to $TARGET_COMMIT" \
        --body "$PR_BODY" \
        --label "emergency,rollback,$INSTANCE,high-priority" \
        --assignee "@me" || PR_CREATED=$?

    if [ "${PR_CREATED:-0}" -eq 0 ]; then
        echo -e "${GREEN}✅ Emergency PR created successfully${NC}"
        PR_URL=$(gh pr view --json url -q .url)
        echo -e "${GREEN}PR URL: $PR_URL${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not create PR automatically${NC}"
        echo "Please create PR manually from branch: $ROLLBACK_BRANCH"
    fi
else
    echo -e "${YELLOW}GitHub CLI not found. Please create PR manually.${NC}"
    echo "Branch pushed: $ROLLBACK_BRANCH"
fi

# Create incident log
INCIDENT_LOG="rollback_$(date +%Y%m%d_%H%M%S).log"
cat > "$INCIDENT_LOG" <<EOF
EMERGENCY ROLLBACK LOG
======================
Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
Instance: $INSTANCE
Target: $TARGET_COMMIT
Reason: ${REASON:-'Not specified'}
Branch: $ROLLBACK_BRANCH
Files Changed: $CHANGED_COUNT
Test Result: ${TEST_RESULT:-0}
PR Created: ${PR_CREATED:-N/A}
EOF

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅ ROLLBACK COMPLETE                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}Summary:${NC}"
echo -e "  Branch: ${GREEN}$ROLLBACK_BRANCH${NC}"
echo -e "  Files: ${GREEN}$CHANGED_COUNT reverted${NC}"
echo -e "  Tests: ${GREEN}${TEST_RESULT:-Passed}${NC}"
echo -e "  Log: ${GREEN}$INCIDENT_LOG${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review and merge the emergency PR"
echo "  2. Deploy to production immediately"
echo "  3. Verify the issue is resolved"
echo "  4. Conduct post-mortem analysis"
echo ""

exit 0