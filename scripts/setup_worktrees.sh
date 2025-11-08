#!/usr/bin/env bash
# Setup git worktrees for 6 parallel Claude AI instances
# This enables lock-free parallel development following the BDFL model

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKTREE_BASE="${PROJECT_ROOT}/.."
DEVELOP_BRANCH="develop"

echo -e "${BLUE}🚩 Setting up Git Worktrees for Revolutionary Parallel Development 🚩${NC}"
echo -e "${YELLOW}Project Root: ${PROJECT_ROOT}${NC}"

# Ensure we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/${DEVELOP_BRANCH}; then
    echo -e "${YELLOW}Creating develop branch...${NC}"
    git checkout -b ${DEVELOP_BRANCH}
    git push -u origin ${DEVELOP_BRANCH}
    git checkout main
fi

# Function to create a worktree for an instance
create_worktree() {
    local instance_num=$1
    local instance_name="instance${instance_num}"
    local worktree_path="${WORKTREE_BASE}/marxist-rag-${instance_name}"
    local branch_name="${instance_name}/develop"

    echo -e "\n${BLUE}Setting up ${instance_name}...${NC}"

    # Check if worktree already exists
    if git worktree list | grep -q "${worktree_path}"; then
        echo -e "${YELLOW}⚠️  Worktree for ${instance_name} already exists at ${worktree_path}${NC}"
        return
    fi

    # Check if branch exists
    if ! git show-ref --verify --quiet "refs/heads/${branch_name}"; then
        echo "  Creating branch ${branch_name}..."
        git branch ${branch_name} ${DEVELOP_BRANCH}
    fi

    # Add worktree
    echo "  Creating worktree at ${worktree_path}..."
    git worktree add "${worktree_path}" ${branch_name}

    # Create instance-specific README
    cat > "${worktree_path}/INSTANCE_README.md" << EOF
# ${instance_name^^} Worktree

This is a dedicated worktree for **${instance_name}** development.

## Instance Focus
$(case ${instance_num} in
    1) echo "**Storage & Pipeline**: GCS integration, batch processing, checkpoint/resume" ;;
    2) echo "**Embeddings**: Runpod GPU integration, batch embedding generation, cost optimization" ;;
    3) echo "**Weaviate Vector DB**: Cluster deployment, sharding, backup/recovery" ;;
    4) echo "**Query & API**: FastAPI engine, Redis caching, advanced filtering" ;;
    5) echo "**MCP Integration**: Protocol implementation, PercyBrain tools, citation generation" ;;
    6) echo "**Monitoring & Testing**: Prometheus/Grafana, test coverage, benchmarking" ;;
esac)

## Workflow

1. **Pull latest changes from develop**:
   \`\`\`bash
   git fetch origin
   git rebase origin/${DEVELOP_BRANCH}
   \`\`\`

2. **Create feature branch**:
   \`\`\`bash
   git checkout -b ${instance_name}/feature-description
   \`\`\`

3. **Make commits using conventional format**:
   \`\`\`bash
   git commit -m "feat(${instance_name}): add new capability"
   \`\`\`

4. **Push to remote**:
   \`\`\`bash
   git push -u origin ${instance_name}/feature-description
   \`\`\`

5. **Create PR to develop branch** (not main!)

## Boundaries

You are responsible for:
$(case ${instance_num} in
    1) echo "- src/mia_rag/storage/\n- src/mia_rag/pipeline/" ;;
    2) echo "- src/mia_rag/embeddings/" ;;
    3) echo "- src/mia_rag/vectordb/" ;;
    4) echo "- src/mia_rag/api/" ;;
    5) echo "- src/mia_rag/mcp/" ;;
    6) echo "- src/mia_rag/monitoring/\n- tests/" ;;
esac)

**DO NOT** modify files outside your boundaries without:
1. Creating an RFC in docs/rfcs/
2. Getting BDFL approval
3. Coordinating with affected instances

## Communication

- Daily sync: Update work-logs/\$(date +%Y%m%d)-${instance_name}.md
- Cross-instance requests: docs/coordination/cross-instance/
- Blocking issues: docs/coordination/BLOCKING-ISSUES.md
EOF

    echo -e "${GREEN}✅ ${instance_name} worktree created successfully${NC}"
}

# Create worktrees for instances 1-5
echo -e "\n${YELLOW}Creating worktrees for instances 1-5...${NC}"
for i in {1..5}; do
    create_worktree $i
done

echo -e "\n${YELLOW}Note: Instance 6 uses the main repository (${PROJECT_ROOT})${NC}"

# Create WORKTREES.md coordination file
cat > "${PROJECT_ROOT}/WORKTREES.md" << 'EOF'
# Git Worktree Coordination

## Active Worktrees

| Instance | Directory | Branch | Focus | Status |
|----------|-----------|--------|-------|--------|
| Instance 1 | ../marxist-rag-instance1 | instance1/develop | Storage & Pipeline | 🟢 Active |
| Instance 2 | ../marxist-rag-instance2 | instance2/develop | Embeddings | 🟢 Active |
| Instance 3 | ../marxist-rag-instance3 | instance3/develop | Vector DB | 🟢 Active |
| Instance 4 | ../marxist-rag-instance4 | instance4/develop | Query API | 🟢 Active |
| Instance 5 | ../marxist-rag-instance5 | instance5/develop | MCP Server | 🟢 Active |
| Instance 6 | . (main repo) | develop | Integration & Testing | 🟢 Active |

## Daily Workflow

### Morning Sync (Start of Session)
1. Pull latest from develop
2. Check coordination board
3. Update work log
4. Review blocking issues

### During Development
1. Commit frequently with conventional commits
2. Push every 30 minutes
3. Check for interface changes every 2 hours

### Evening Wrap-up (End of Session)
1. Push all commits
2. Update work log with progress
3. Create PR if ready
4. Flag any blocking issues

## Coordination Commands

```bash
# View all worktrees
git worktree list

# Check status of all instances
for dir in ../marxist-rag-instance*; do
    echo "=== $(basename $dir) ==="
    git -C "$dir" status --short
done

# Pull latest in all worktrees
for dir in . ../marxist-rag-instance*; do
    echo "Updating $(basename $dir)..."
    git -C "$dir" fetch origin
    git -C "$dir" rebase origin/develop
done

# Remove a worktree (if needed)
git worktree remove ../marxist-rag-instance1

# Prune stale worktrees
git worktree prune
```

## Branch Naming Convention

- Feature: `instance{N}/feature-{description}`
- Bug fix: `instance{N}/fix-{description}`
- Hotfix: `hotfix/v{version}-{description}`
- Release: `release/v{version}`

## Merge Strategy

1. Instance branches → develop (squash merge)
2. develop → main (merge commit with --no-ff)
3. Hotfix → main (direct merge, then backport)

## Conflict Resolution

If you encounter conflicts:
1. Check `docs/coordination/BLOCKING-ISSUES.md`
2. Coordinate with affected instance via cross-instance communication
3. If urgent, escalate to BDFL

## BDFL Controls

Only the BDFL (Persephone Raskova) can:
- Merge to main branch
- Create releases
- Override branch protection
- Resolve cross-instance conflicts
- Approve interface changes

---

*"Workers of all instances, unite! You have nothing to lose but your merge conflicts!"*
EOF

# Create coordination directories
echo -e "\n${YELLOW}Creating coordination directories...${NC}"
mkdir -p "${PROJECT_ROOT}/docs/coordination/cross-instance"
mkdir -p "${PROJECT_ROOT}/work-logs"
mkdir -p "${PROJECT_ROOT}/docs/rfcs"

# Create initial coordination files
cat > "${PROJECT_ROOT}/docs/coordination/BLOCKING-ISSUES.md" << 'EOF'
# Blocking Issues

Track cross-instance blocking issues here. Update daily.

## Active Blocks

*None currently*

## Resolved Blocks

*None yet*

## Format for New Blocks

```markdown
### [Issue Title]
- **Blocking**: Instance X
- **Blocked by**: Instance Y
- **Description**: Brief description
- **Priority**: HIGH/MEDIUM/LOW
- **Created**: YYYY-MM-DD
- **Target Resolution**: YYYY-MM-DD
- **Status**: 🔴 Blocked / 🟡 In Progress / 🟢 Resolved
```
EOF

cat > "${PROJECT_ROOT}/docs/coordination/README.md" << 'EOF'
# Instance Coordination

This directory contains coordination files for the 6 parallel development instances.

## Structure

```
coordination/
├── README.md                 # This file
├── BLOCKING-ISSUES.md       # Track blocking issues
├── cross-instance/          # Cross-instance communication
│   └── YYYYMMDD-instanceX-to-instanceY.md
└── daily-sync/              # Daily sync notes
    └── YYYYMMDD-sync.md
```

## Communication Protocol

### Async Communication
- Use cross-instance files for non-urgent requests
- Update BLOCKING-ISSUES.md for blockers
- Create RFCs for interface changes

### Sync Points
- Daily: Update work logs
- Every 2 hours: Check for interface changes
- On PR: Verify no boundary violations

## Instance Boundaries

| Instance | Owns | Can Read | Cannot Touch |
|----------|------|----------|--------------|
| 1 | storage/, pipeline/ | interfaces/ | Other instance code |
| 2 | embeddings/ | interfaces/ | Other instance code |
| 3 | vectordb/ | interfaces/ | Other instance code |
| 4 | api/ | interfaces/ | Other instance code |
| 5 | mcp/ | interfaces/ | Other instance code |
| 6 | monitoring/, tests/ | All | Instance-specific code |

## Escalation Path

1. Try to resolve within instance
2. Coordinate via cross-instance communication
3. Update BLOCKING-ISSUES.md
4. If still blocked after 24h, escalate to BDFL
EOF

# Create a helper script for daily operations
cat > "${PROJECT_ROOT}/scripts/worktree_status.sh" << 'EOFSCRIPT'
#!/usr/bin/env bash
# Check status of all worktrees

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Worktree Status Report ===${NC}\n"

# Main repository
echo -e "${YELLOW}Main Repository (Instance 6)${NC}"
echo "Path: $(pwd)"
echo "Branch: $(git branch --show-current)"
echo "Status:"
git status --short
echo

# Check all worktrees
for worktree in $(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do
    if [[ "$worktree" != "$(pwd)" ]]; then
        echo -e "${YELLOW}$(basename $worktree)${NC}"
        echo "Path: $worktree"
        if [[ -d "$worktree" ]]; then
            cd "$worktree"
            echo "Branch: $(git branch --show-current)"
            echo "Status:"
            git status --short
            cd - > /dev/null
        else
            echo -e "${RED}Directory not found!${NC}"
        fi
        echo
    fi
done

echo -e "${GREEN}=== Summary ===${NC}"
git worktree list
EOFSCRIPT

chmod +x "${PROJECT_ROOT}/scripts/worktree_status.sh"
chmod +x "${PROJECT_ROOT}/scripts/setup_worktrees.sh"

# Final summary
echo -e "\n${GREEN}✨ Git Worktree Setup Complete! ✨${NC}"
echo
echo "Worktrees created:"
git worktree list
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Each Claude instance should work in its dedicated worktree"
echo "2. Run './scripts/worktree_status.sh' to check status"
echo "3. Read WORKTREES.md for coordination workflow"
echo "4. Update work-logs/$(date +%Y%m%d)-instance{N}.md daily"
echo
echo -e "${GREEN}🚩 The means of parallel development have been seized! 🚩${NC}"