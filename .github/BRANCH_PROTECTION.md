# Branch Protection Rules

This document describes the branch protection configuration for the Marxist RAG repository.

## Configuration Summary

| Branch | Protection Level | Merge Strategy | Who Can Push |
|--------|-----------------|----------------|--------------|
| `main` | **Strict** | Merge commit (--no-ff) | BDFL only |
| `develop` | **Medium** | Squash merge | BDFL only |
| `instance*/*` | **Light** | Rebase | Anyone |

## Branch: `main`

**Purpose**: Production-ready releases only

### Protection Rules

```yaml
required_status_checks:
  strict: true
  contexts:
    - "test-summary"
    - "validate-instance-boundaries"
    - "validate-interface-contracts"

required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  dismissal_restrictions:
    users: ["percy-raskova"]

restrictions:
  users: ["percy-raskova"]  # Only BDFL can push directly

enforce_admins: false  # BDFL can override if needed
allow_force_pushes: false
allow_deletions: false
required_linear_history: true
```

### Merge Strategy

- **Always use merge commits** (`--no-ff`)
- Preserves full history for audit trail
- Each merge represents a release or major milestone

### Example

```bash
# BDFL merging develop to main
git checkout main
git merge develop --no-ff -m "release: merge develop for v0.2.0 release"
git push origin main
```

## Branch: `develop`

**Purpose**: Integration branch for all instance development

### Protection Rules

```yaml
required_status_checks:
  strict: true
  contexts:
    - "test-summary"
    - "validate-instance-boundaries"

required_pull_request_reviews:
  required_approving_review_count: 0  # BDFL reviews manually
  dismiss_stale_reviews: false
  require_code_owner_reviews: true

restrictions:
  users: ["percy-raskova"]

enforce_admins: false
allow_force_pushes: false
allow_deletions: false
```

### Merge Strategy

- **Squash merge** from instance branches
- Cleans up commit history from AI agent iterations
- One logical commit per feature

### Example

```bash
# Merging instance PR to develop
gh pr merge 42 --squash --delete-branch
```

## Branches: `instance*/**`

**Purpose**: Development branches for each of 6 instances

### Protection Rules

```yaml
required_status_checks:
  strict: false  # Allow rebasing
  contexts:
    - "test-instances"

required_pull_request_reviews:
  required_approving_review_count: 0

enforce_admins: false
allow_force_pushes: true  # Allow AI agents to rebase/amend
allow_deletions: true     # Can delete after merge
```

### Merge Strategy

- **Rebase** within instance branches
- Keeps history linear
- Allows AI agents to iterate freely

### Example

```bash
# Working in instance branch
git checkout instance2/feature-new-model
git commit -m "feat(instance2): add initial model"
# Oops, need to fix something
git commit --amend
git push --force-with-lease
```

## Setting Up Protection Rules

### Via GitHub Web UI

1. Go to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Configure each branch pattern:
   - `main`
   - `develop`
   - `instance*/**`

### Via GitHub CLI

```bash
# Protect main branch
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=test-summary \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field restrictions[users][]=percy-raskova \
  --field enforce_admins=false \
  --field allow_force_pushes=false \
  --field required_linear_history=true

# Protect develop branch
gh api repos/{owner}/{repo}/branches/develop/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=test-summary \
  --field restrictions[users][]=percy-raskova \
  --field allow_force_pushes=false
```

### Via Terraform (Recommended for Infrastructure as Code)

```hcl
# main branch protection
resource "github_branch_protection" "main" {
  repository_id = github_repository.marxist_rag.node_id
  pattern       = "main"

  required_status_checks {
    strict = true
    contexts = [
      "test-summary",
      "validate-instance-boundaries",
      "validate-interface-contracts"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true

    dismissal_restrictions = [
      data.github_user.bdfl.node_id
    ]
  }

  push_restrictions = [
    data.github_user.bdfl.node_id
  ]

  enforce_admins        = false
  allows_force_pushes   = false
  allows_deletions      = false
  require_linear_history = true
}

# develop branch protection
resource "github_branch_protection" "develop" {
  repository_id = github_repository.marxist_rag.node_id
  pattern       = "develop"

  required_status_checks {
    strict = true
    contexts = [
      "test-summary",
      "validate-instance-boundaries"
    ]
  }

  push_restrictions = [
    data.github_user.bdfl.node_id
  ]

  enforce_admins      = false
  allows_force_pushes = false
  allows_deletions    = false
}

# instance branches - lighter protection
resource "github_branch_protection" "instance_branches" {
  repository_id = github_repository.marxist_rag.node_id
  pattern       = "instance*/**"

  required_status_checks {
    strict = false
    contexts = ["test-instances"]
  }

  allows_force_pushes = true
  allows_deletions    = true
}
```

## CODEOWNERS File

Create `.github/CODEOWNERS` to enforce ownership:

```
# Default owner (BDFL)
* @percy-raskova

# Instance-specific ownership (optional delegation)
/src/mia_rag/storage/ @percy-raskova
/src/mia_rag/embeddings/ @percy-raskova
/src/mia_rag/vectordb/ @percy-raskova
/src/mia_rag/api/ @percy-raskova
/src/mia_rag/mcp/ @percy-raskova
/src/mia_rag/monitoring/ @percy-raskova

# Shared interfaces require BDFL review
/src/mia_rag/interfaces/ @percy-raskova

# Documentation
/docs/ @percy-raskova
/*.md @percy-raskova

# CI/CD
/.github/ @percy-raskova
```

## Workflow Examples

### Normal Development Flow

```bash
# Instance developer creates feature branch
git checkout -b instance2/feature-gpu-batch
# ... make changes ...
git push origin instance2/feature-gpu-batch

# Create PR to develop
gh pr create --base develop --fill

# BDFL reviews and merges (squash)
gh pr merge 42 --squash
```

### Hotfix Flow

```bash
# BDFL creates hotfix from main
git checkout main
git checkout -b hotfix/v0.1.1-critical
# ... fix issue ...
git commit -m "fix: critical security vulnerability"
git push origin hotfix/v0.1.1-critical

# Create PR to main
gh pr create --base main --fill

# After merge, backport to develop
git checkout develop
git cherry-pick <hotfix-commit>
git push origin develop
```

### Release Flow

```bash
# BDFL prepares release
git checkout develop
git pull origin develop

# Merge to main
git checkout main
git merge develop --no-ff -m "release: v0.2.0"

# Trigger release workflow (creates tag, builds package)
gh workflow run release.yml -f increment=minor

# Release workflow automatically:
# - Runs tests
# - Bumps version
# - Updates CHANGELOG
# - Creates tag
# - Builds package
# - Creates GitHub release
```

## Enforcement

### Pre-commit Hooks

Branch protection is also enforced locally via pre-commit hooks:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-branch
      name: Check branch is not main
      entry: bash -c 'if [ "$(git branch --show-current)" = "main" ]; then echo "Cannot commit directly to main!"; exit 1; fi'
      language: system
      always_run: true
```

### CI Checks

GitHub Actions verify:
- All tests pass
- No boundary violations
- Conventional commit format
- No secrets in code

## Troubleshooting

### "Protected branch" error

```
remote: error: GH006: Protected branch update failed
```

**Solution**: Create a PR instead of pushing directly

### "Required status check" failing

```
remote: error: Required status check "test-summary" is failing
```

**Solution**: Fix tests before merging

### Force push rejected

```
remote: error: deny updating a ref that is not a fast-forward
```

**Solution**: Use `--force-with-lease` on instance branches only

## Summary

- **main**: Strict protection, BDFL only, merge commits
- **develop**: Medium protection, BDFL only, squash merges
- **instance branches**: Light protection, anyone, rebasing allowed

This configuration balances:
- **Safety**: main is protected
- **Coordination**: develop integrates all work
- **Flexibility**: instance branches allow iteration

---

**For questions about branch protection, contact the BDFL: @percy-raskova**