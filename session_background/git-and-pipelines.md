# Git & CI/CD Pipelines
## DevOps Knowledge Transfer – Session 4

**Author:** Zdenek Pyszko  
**Date:** February 2026  
**Audience:** Infrastructure Engineers  
**Duration:** ~2 hours  
**Level:** Beginner to Intermediate

---

## Agenda

| # | Topic | Time |
|---|-------|------|
| 1 | Git Fundamentals | 25 min |
| 2 | Merge / Pull Requests | 10 min |
| 3 | Platform Comparison (GitHub / GitLab / Bitbucket) | 10 min |
| 4 | Branching Strategies | 10 min |
| — | **Break** | **5 min** |
| 5 | CI/CD Pipelines – Concepts | 10 min |
| 6 | CI vs CD – What's the Difference? | 5 min |
| 7 | CI/CD Tooling Comparison | 10 min |
| 8 | Secrets Handling | 10 min |
| 9 | DevSecOps | 10 min |
| 10 | GitOps | 10 min |
| 11 | Hands-On: GitHub Actions Examples | 15 min |
| 12 | Q&A | 5 min |

---

## Recap: Previous Sessions

| Session | Topics Covered |
|---------|----------------|
| Session 1 | DevOps Theory, Culture, Principles |
| Session 2 | Azure Portal GUI, Resource Management |
| Session 3 | IaC – Terraform & Ansible |
| **Session 4** | **Git & CI/CD Pipelines** ← _Today_ |

---

# PART 1: GIT

---

## What Is Git?

- **Distributed Version Control System** (DVCS)
- Created by **Linus Torvalds** in 2005 (for Linux kernel development)
- Every developer has a **full copy** of the repository
- Works **offline** – most operations are local
- De-facto standard for source code management

```
Traditional VCS:     [Central Server] ←→ [Developer]

Git (Distributed):   [Remote Repo]
                      ↕         ↕
                 [Dev A Repo] [Dev B Repo]
                 (full copy)  (full copy)
```

---

## Why Git Matters for Infrastructure Engineers

- **Terraform code** → versioned in Git
- **Ansible playbooks** → versioned in Git
- **Kubernetes manifests** → versioned in Git
- **Pipeline definitions** → versioned in Git
- **Documentation** → versioned in Git

> _"If it's not in Git, it doesn't exist."_

Everything we built in previous sessions lives in a Git repo.

---

## Git Architecture – The Three Areas

```
┌──────────────┐    git add     ┌──────────────┐   git commit   ┌──────────────┐
│              │  ──────────►   │              │  ──────────►   │              │
│  Working     │                │  Staging     │                │  Local        │
│  Directory   │                │  Area        │                │  Repository   │
│              │   ◄──────────  │  (Index)     │                │  (.git/)      │
│  (your files)│   git restore  │              │                │              │
└──────────────┘                └──────────────┘                └──────┬───────┘
                                                                       │
                                                          git push ↕   │  ↕ git pull/fetch
                                                                       │
                                                                ┌──────┴───────┐
                                                                │   Remote     │
                                                                │   Repository │
                                                                │  (GitHub...) │
                                                                └──────────────┘
```

---

## Essential Git Commands – Setup

```bash
# Configure your identity (one-time setup)
git config --global user.name "Zdenek Pyszko"
git config --global user.email "zdenek@example.com"

# View your configuration
git config --list

# Set default branch name
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "code --wait"
```

---

## Essential Git Commands – Getting Started

### Clone – Download an existing repository
```bash
# Clone a remote repository (HTTPS)
git clone https://github.com/org/devops-kt.git

# Clone a remote repository (SSH – recommended)
git clone git@github.com:org/devops-kt.git

# Clone into a specific folder
git clone git@github.com:org/devops-kt.git my-project
```

### Init – Create a new repository
```bash
# Initialize a new repo in current directory
git init

# Initialize and set remote
git init
git remote add origin git@github.com:org/new-repo.git
```

---

## Essential Git Commands – Daily Workflow

### Status – See what's changed
```bash
git status                    # Show working tree status
git status -s                 # Short format
```

### Add – Stage changes
```bash
git add main.tf               # Stage a specific file
git add terraform/             # Stage entire directory
git add .                      # Stage everything (use carefully!)
git add -p                     # Interactive staging (patch mode)
```

### Commit – Save snapshot
```bash
git commit -m "Add hub-spoke networking module"
git commit -am "Quick fix"     # Add tracked files + commit
```

---

## Essential Git Commands – Syncing

### Pull – Get latest from remote
```bash
git pull                       # Fetch + merge from remote
git pull --rebase              # Fetch + rebase (cleaner history)
git pull origin main           # Pull specific branch
```

### Push – Upload to remote
```bash
git push                       # Push current branch
git push origin main           # Push to specific branch
git push -u origin feature/x   # Push new branch & set upstream
```

### Fetch – Download without merging
```bash
git fetch                      # Download changes, don't apply
git fetch --all                # Fetch from all remotes
```

---

## Essential Git Commands – Inspecting

```bash
# View commit history
git log                        # Full log
git log --oneline              # Compact view
git log --oneline --graph      # Visual branch graph
git log -5                     # Last 5 commits

# View changes
git diff                       # Unstaged changes
git diff --staged              # Staged changes
git diff main..feature/x       # Compare branches

# View a specific commit
git show abc1234

# Who changed what?
git blame main.tf
```

---

## Essential Git Commands – Branching

```bash
# List branches
git branch                     # Local branches
git branch -a                  # All branches (incl. remote)

# Create and switch to a new branch
git checkout -b feature/add-nsg-rules
# Modern alternative:
git switch -c feature/add-nsg-rules

# Switch to existing branch
git checkout main
git switch main

# Delete a branch
git branch -d feature/old-branch        # Safe delete
git branch -D feature/old-branch        # Force delete
```

---

## Git Branching – Visual

```
        feature/add-nsg ─── C4 ─── C5
       /                            \
main: C1 ─── C2 ─── C3 ────────────── C6 (merge)
                      \
                       hotfix/fix-route ─── C7
```

- Branches are **cheap, lightweight pointers** to a commit
- Every branch is just a file containing a commit hash (~41 bytes)
- Encourages **experimentation** without risk
- Core of every collaboration workflow

---

## Handling Merge Conflicts

### When do conflicts happen?
- Two people edit the **same lines** in the **same file**
- Git cannot automatically decide which version to keep

### What it looks like:
```
<<<<<<< HEAD
resource_group_name = "rg-hub-prod"
=======
resource_group_name = "rg-hub-production"
>>>>>>> feature/rename-rg
```

### How to resolve:
1. Open the conflicted file
2. Choose the correct version (or combine both)
3. Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
4. Stage and commit the resolution

```bash
git add main.tf
git commit -m "Resolve conflict in resource group naming"
```

---

## Merge Conflicts – Tips

| Do | Don't |
|---|---|
| Pull frequently to stay up-to-date | Let branches diverge for weeks |
| Make small, focused commits | Make huge commits touching many files |
| Communicate with your team | Assume nobody else is editing the same file |
| Use `git diff` before committing | Blindly accept one side |
| Use VS Code merge editor (visual) | Manually edit conflict markers if unsure |

### VS Code Merge Editor
- VS Code provides a **built-in 3-way merge editor**
- Shows: Current (yours) | Incoming (theirs) | Result
- Click buttons to accept changes visually

---

## Useful Git Extras

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git checkout -- .
# Modern alternative:
git restore .

# Stash changes temporarily
git stash                      # Save work-in-progress
git stash list                 # List stashes
git stash pop                  # Restore latest stash

# Tag a release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Clean untracked files
git clean -fd                  # Remove untracked files/dirs
```

---

## .gitignore – What NOT to Track

```gitignore
# Terraform
*.tfstate
*.tfstate.backup
*.tfvars
.terraform/
.terraform.lock.hcl

# Ansible
*.retry

# Secrets – NEVER commit these!
*.pem
*.key
*secret*
.env

# OS / Editor
.DS_Store
.vscode/
*.swp
```

> **Rule: If it's a secret or generated artifact, add it to `.gitignore`**

---

# PART 2: MERGE / PULL REQUESTS

---

## Merge Requests (MR) / Pull Requests (PR)

> Same concept, different names:
> - **GitHub / Bitbucket** → Pull Request (PR)
> - **GitLab** → Merge Request (MR)

### What is it?
A **formal request** to merge code from one branch into another, with:
- **Code review** by peers
- **Automated checks** (CI pipeline, linting, tests)
- **Discussion & comments** on specific lines
- **Approval workflow** before merge

---

## Pull Request Workflow

```
1. Create branch       ──►  2. Make changes & commit
                                      │
                                      ▼
4. Review & discuss   ◄──  3. Open Pull Request
        │
        ▼
5. CI checks pass     ──►  6. Approve
                                      │
                                      ▼
                             7. Merge to main
                                      │
                                      ▼
                             8. Delete feature branch
```

---

## Anatomy of a Good Pull Request

### Title
`feat: Add NSG rules for AKS subnet`

### Description Template
```markdown
## What
Added NSG rules to allow AKS traffic through the hub firewall.

## Why
AKS pods need egress access to Azure APIs and container registries.

## Changes
- Added NSG rules in `config/nsgs.yaml`
- Updated hub-spoke module route tables
- Added output for NSG IDs

## Testing
- `terraform plan` shows 3 resources to add
- Validated NSG rules against Azure documentation

## Checklist
- [ ] Code follows project conventions
- [ ] terraform fmt applied
- [ ] Documentation updated
- [ ] No secrets in code
```

---

## PR Best Practices

| Practice | Why |
|----------|-----|
| **Keep PRs small** (< 400 lines) | Easier to review, fewer bugs |
| **One concern per PR** | Simpler to understand, revert, track |
| **Write descriptive titles** | Helps reviewers prioritize |
| **Add screenshots for UI changes** | Visual verification |
| **Request specific reviewers** | Domain experts catch more issues |
| **Respond to feedback promptly** | Keeps momentum |
| **Don't approve your own PRs** | Four-eyes principle |
| **Squash commits on merge** | Clean history on main |

---

# PART 3: PLATFORM COMPARISON

---

## GitHub vs GitLab vs Bitbucket vs Azure DevOps

| Feature | GitHub | GitLab | Bitbucket | Azure DevOps |
|---------|--------|--------|-----------|--------------|
| **Owned by** | Microsoft | GitLab Inc. | Atlassian | Microsoft |
| **Repository** | Git | Git | Git (+ Mercurial legacy) | Git (+ TFVC) |
| **CI/CD** | GitHub Actions | GitLab CI/CD | Bitbucket Pipelines | Azure Pipelines |
| **Pipeline config** | `.github/workflows/*.yml` | `.gitlab-ci.yml` | `bitbucket-pipelines.yml` | `azure-pipelines.yml` |
| **Free tier** | Generous | Very generous | Limited | Generous (5 users) |
| **Self-hosted** | GitHub Enterprise | GitLab CE/EE | Bitbucket DC | Azure DevOps Server |
| **Container Registry** | GHCR | Built-in | None (use Docker Hub) | ACR integration |
| **Issue Tracking** | Issues + Projects | Issues + Boards | Jira integration | Boards (Agile) |
| **Best for** | Open source, community | All-in-one DevOps | Atlassian shops | Microsoft / Azure shops |

---

## Platform Comparison – CI/CD Syntax Side-by-Side

### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: terraform init
      - run: terraform validate
```

### GitLab CI
```yaml
# .gitlab-ci.yml
validate:
  image: hashicorp/terraform
  stage: validate
  script:
    - terraform init
    - terraform validate
```

### Azure Pipelines
```yaml
# azure-pipelines.yml
trigger:
  - main
pool:
  vmImage: 'ubuntu-latest'
steps:
  - script: terraform init
  - script: terraform validate
```

---

## Which Platform to Choose?

```
                    ┌─────────────────────┐
                    │  What ecosystem     │
                    │  are you in?        │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ Microsoft│   │Atlassian │   │ Open Source / │
        │  / Azure │   │ (Jira,   │   │ Multi-cloud  │
        │          │   │Confluence)│   │              │
        └────┬─────┘   └────┬─────┘   └──────┬───────┘
             │              │                 │
        ┌────▼─────┐  ┌────▼──────┐   ┌──────▼───────┐
        │  Azure   │  │ Bitbucket │   │   GitHub     │
        │  DevOps  │  │           │   │   or GitLab  │
        │  or      │  └───────────┘   └──────────────┘
        │  GitHub  │
        └──────────┘
```

> **Tip:** GitHub is increasingly the industry default. Azure DevOps remains strong for enterprises already invested in the Microsoft ecosystem.

---

# PART 4: BRANCHING STRATEGIES

---

## Why Branching Strategies Matter

- Without a strategy → **chaos**: broken main branch, conflicts, unclear releases
- A branching strategy defines:
  - **How** branches are named
  - **When** branches are created and merged
  - **Who** approves merges
  - **What** triggers deployments

---

## Strategy 1: Trunk-Based Development

```
main: ── C1 ── C2 ── C3 ── C4 ── C5 ── C6 ── C7 ──►
              ↑         ↑              ↑
           short     short          short
           branch    branch         branch
           (< 1 day) (< 1 day)     (< 1 day)
```

### Characteristics
- Single long-lived branch: `main`
- Very short-lived feature branches (hours, max 1-2 days)
- Frequent integration (multiple times per day)
- Requires: strong CI, feature flags, automated testing

### Best for
- Experienced teams, mature CI/CD pipelines
- Continuous deployment environments

---

## Strategy 2: GitHub Flow

```
main: ── C1 ── C2 ──────────── C5 ── C6 (merge) ──►
                  \                  /
feature/add-fw:    C3 ── C4 ────────
                         ↑
                    Pull Request
```

### Rules
1. `main` is always deployable
2. Create a feature branch from `main`
3. Commit to the feature branch
4. Open a **Pull Request**
5. Review, discuss, test (CI)
6. Merge to `main` → deploy

### Best for
- Most teams, simple & effective
- **Recommended for infrastructure teams starting out**

---

## Strategy 3: Git Flow

```
main:    ── v1.0 ──────────────────────── v2.0 ──►
               \                          /
develop:  ── C1 ── C2 ── C4 ── C6 ── C7 ──
                    \         /
feature/x:           C3 ── C5
                              \
release/2.0:                   ── RC1 ── RC2
                                          │
hotfix/2.0.1:                          ── FIX
```

### Branches
| Branch | Purpose | Long-lived? |
|--------|---------|-------------|
| `main` | Production releases | Yes |
| `develop` | Integration branch | Yes |
| `feature/*` | New features | No |
| `release/*` | Release preparation | No |
| `hotfix/*` | Production fixes | No |

### Best for
- Projects with scheduled releases, complex release management

---

## Strategy 4: Environment Branching

```
main:      ── C1 ── C2 ── C3 ──►        → deploys to DEV
                          │
staging:   ── C1 ── C2 ──►              → deploys to STAGING
                    │
production:── C1 ──►                     → deploys to PROD
```

### How it works
- Each branch maps to an **environment**
- Code promotes by **merging between branches**
- Simple to understand, but can lead to divergence

### Best for
- Teams needing explicit environment control
- When pipeline-based promotion isn't available

---

## Branching Strategy Comparison

| Aspect | Trunk-Based | GitHub Flow | Git Flow | Env Branching |
|--------|------------|-------------|----------|---------------|
| **Complexity** | Low | Low | High | Medium |
| **Release cadence** | Continuous | Continuous | Scheduled | Manual |
| **Long-lived branches** | 1 (main) | 1 (main) | 2 (main+develop) | N (per env) |
| **Learning curve** | Low | Low | High | Low |
| **Merge conflicts** | Rare | Occasional | Frequent | Occasional |
| **Best for infra** | Advanced | **Recommended** | Enterprise | Legacy |

> **Recommendation for our team: GitHub Flow** – simple, PR-based, works great with Terraform and Ansible.

---

# ☕ BREAK (5 min)

---

# PART 5: CI/CD PIPELINES

---

## What Is a CI/CD Pipeline?

A **pipeline** is an automated sequence of steps that takes code from commit to production.

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐
│  Code   │───►│  Build  │───►│  Test   │───►│ Release │───►│  Deploy  │
│  Commit │    │         │    │         │    │         │    │          │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └──────────┘
     │              │              │              │               │
  Developer      Compile       Lint/Scan      Package         Push to
  pushes to      code,         Security,      artifact,       staging/
  Git repo       resolve       Unit test,     tag release     production
                 deps          Integration
```

### Key principles
- **Automated** – no manual steps
- **Repeatable** – same input → same output
- **Fast feedback** – developers know within minutes if something broke

---

## CI vs CD – What's the Difference?

### Continuous Integration (CI)
- Automatically **build and test** every code change
- Detect bugs early, before they reach production
- Runs on: every push, every PR

### Continuous Delivery (CD)
- Automatically **prepare releases** for deployment
- Code is _always_ in a deployable state
- Deployment to production requires **manual approval**

### Continuous Deployment (CD)
- Automatically **deploy to production** after all checks pass
- No manual gate – fully automated
- Requires very mature testing & monitoring

```
CI ──────────►  CD (Delivery) ──────────►  CD (Deployment)
Build & Test    + Package & Stage          + Auto-deploy to Prod
                  (manual approval)          (no approval needed)
```

---

## CI vs CD – For Infrastructure

| Stage | CI (Continuous Integration) | CD (Continuous Delivery/Deployment) |
|-------|----------------------------|--------------------------------------|
| **Terraform** | `terraform fmt -check` | `terraform apply` (with approval) |
| | `terraform validate` | Deploy to staging → production |
| | `terraform plan` | State management |
| | `tflint`, `checkov`, `tfsec` | |
| **Ansible** | `ansible-lint` | `ansible-playbook` execution |
| | `yamllint` | Rolling deployments |
| | `ansible --syntax-check` | |
| **Kubernetes** | `kubectl apply --dry-run` | `kubectl apply` |
| | `kubeval`, `kube-score` | Helm upgrades |
| | Image scanning | ArgoCD sync |

---

# PART 6: CI/CD TOOLING

---

## CI/CD Tooling Landscape

```
┌───────────────────────────────────────────────────────────┐
│                    CI/CD Tools                             │
├──────────────────┬────────────────┬───────────────────────┤
│  Cloud-Native    │  Self-Hosted   │  GitOps-Focused       │
├──────────────────┼────────────────┼───────────────────────┤
│ GitHub Actions   │ Jenkins        │ ArgoCD                │
│ GitLab CI/CD     │ TeamCity       │ Flux                  │
│ Azure Pipelines  │ Bamboo         │ Spinnaker             │
│ Bitbucket Pipes  │ GoCD           │                       │
│ AWS CodePipeline │ Drone CI       │                       │
│ Google Cloud     │ Concourse      │                       │
│   Build          │                │                       │
└──────────────────┴────────────────┴───────────────────────┘
```

---

## GitHub Actions vs Azure DevOps vs Jenkins

| Feature | GitHub Actions | Azure DevOps | Jenkins |
|---------|---------------|--------------|---------|
| **Type** | Cloud-native | Cloud / Server | Self-hosted |
| **Config** | YAML in repo | YAML or GUI | Groovy (Jenkinsfile) |
| **Learning curve** | Low | Medium | High |
| **Marketplace** | 20,000+ Actions | Extensions | 1,800+ plugins |
| **Runners** | GitHub-hosted or self-hosted | MS-hosted or self-hosted | Always self-hosted |
| **Cost** | Free tier (2000 min/mo) | Free (5 users, 1800 min/mo) | Free (open source) |
| **Maintenance** | None (cloud) | Low (cloud) | High (you manage servers) |
| **Scalability** | Auto-scales | Auto-scales | Manual scaling |
| **Secret management** | GitHub Secrets | Variable Groups + Key Vault | Credentials plugin |
| **Best for** | GitHub repos | Azure-heavy orgs | Highly customized builds |

---

## GitHub Actions vs Azure DevOps vs Jenkins – When to Choose

### Choose GitHub Actions when:
- Your code is already on GitHub
- You want **simplest possible setup**
- You need the largest ecosystem of pre-built actions
- You want to be on the **most popular** platform

### Choose Azure DevOps when:
- Deep Azure integration needed (Key Vault, ACR, AKS, ARM)
- You need **Boards, Artifacts, Test Plans** (all-in-one)
- Enterprise compliance requirements (Azure AD integration)
- Your company already pays for Microsoft E3/E5 licenses

### Choose Jenkins when:
- You need **full control** over the CI/CD infrastructure
- Complex, highly customized pipelines
- Air-gapped / on-premises environments
- Legacy systems integration

---

# PART 7: SECRETS HANDLING

---

## Secrets Handling – The Problem

### What are secrets?
- API keys, tokens, passwords
- TLS certificates, SSH keys
- Database connection strings
- Service principal credentials
- Storage account keys

### What goes wrong:
```bash
# ❌ NEVER DO THIS
terraform.tfvars:
  client_secret = "super-secret-password-123"

# ❌ NEVER DO THIS
git commit -m "Add Azure credentials"

# ❌ NEVER DO THIS
echo $PASSWORD | docker login
```

> **If a secret is committed to Git, consider it compromised.**  
> Git history retains it **forever** (even after deletion).

---

## Secrets Handling – Best Practices

| Practice | Implementation |
|----------|---------------|
| **Never hardcode secrets** | Use environment variables or vault references |
| **Use a secrets manager** | Azure Key Vault, HashiCorp Vault, AWS Secrets Manager |
| **CI/CD Secrets** | GitHub Secrets, Azure DevOps Variable Groups |
| **Rotate secrets regularly** | Automate rotation with Key Vault |
| **Scan for secrets** | Pre-commit hooks, CI scanning (gitleaks, trufflehog) |
| **Use `.gitignore`** | Exclude `*.tfvars`, `.env`, `*.pem`, `*.key` |
| **Least privilege** | Only give pipelines the secrets they need |
| **Audit access** | Log who accessed which secret and when |

---

## Secrets in CI/CD – Examples

### GitHub Actions
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - run: terraform apply -auto-approve
        env:
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
```

### Azure DevOps – Variable Groups + Key Vault
```yaml
variables:
  - group: 'production-secrets'  # Linked to Azure Key Vault

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: 'Production'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        terraform apply -auto-approve
```

---

## Secrets Scanning Tools

| Tool | Type | Description |
|------|------|-------------|
| **gitleaks** | Pre-commit + CI | Scans git history for secrets |
| **trufflehog** | Pre-commit + CI | Finds high-entropy strings, credentials |
| **git-secrets** | Pre-commit hook | Prevents committing AWS keys |
| **GitHub Secret Scanning** | Platform | Built-in for GitHub repos |
| **Azure DevOps Credential Scanner** | Platform | Integrated in Azure DevOps |
| **detect-secrets** (Yelp) | Pre-commit + CI | Customizable secret detection |

### Example: gitleaks as pre-commit hook
```bash
# Install gitleaks
brew install gitleaks

# Scan current repo
gitleaks detect --source . -v

# Use as pre-commit hook (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

---

# PART 8: DEVSECOPS

---

## What Is DevSecOps?

> **DevSecOps = Development + Security + Operations**

Security is **shifted left** – integrated at every stage of the pipeline, not bolted on at the end.

```
Traditional:
  Dev ──► Ops ──► Security Review (too late!)

DevSecOps:
  ┌──────────────────────────────────────────────────┐
  │ Security integrated at EVERY stage               │
  │                                                  │
  │  Code → Scan → Build → Test → Deploy → Monitor  │
  │   ▲       ▲       ▲      ▲       ▲        ▲     │
  │  lint   SAST   SCA    DAST   Secrets   Runtime   │
  │  secrets deps  images  APIs   audit    security  │
  └──────────────────────────────────────────────────┘
```

---

## DevSecOps – Security in the Pipeline

| Pipeline Stage | Security Activity | Tools |
|---------------|-------------------|-------|
| **Code** | Linting, secret scanning | gitleaks, pre-commit |
| **Build** | SAST (static analysis) | SonarQube, Semgrep, Checkov |
| **Dependencies** | SCA (component analysis) | Dependabot, Snyk, Trivy |
| **Container** | Image scanning | Trivy, Grype, Prisma Cloud |
| **IaC** | Misconfig scanning | Checkov, tfsec, KICS |
| **Deploy** | DAST (runtime testing) | OWASP ZAP, Burp Suite |
| **Runtime** | Monitoring, alerting | Defender for Cloud, Falco |

---

## DevSecOps for Infrastructure – IaC Security Scanning

### Checkov – Terraform & Kubernetes scanner
```bash
# Install
pip install checkov

# Scan Terraform
checkov -d ./terraform/

# Example output:
# Passed: 42, Failed: 3, Skipped: 0
# FAILED:
#   CKV_AZURE_1: "Ensure Azure VM has a managed disk"
#   CKV_AZURE_35: "Ensure NSG does not allow SSH from 0.0.0.0/0"
#   CKV_AZURE_9: "Ensure AKS logging is enabled"
```

### tfsec – Terraform-specific
```bash
# Install
brew install tfsec

# Scan
tfsec ./terraform/
```

### In a pipeline (GitHub Actions):
```yaml
- name: Run Checkov
  uses: bridgecrewio/checkov-action@v12
  with:
    directory: terraform/
    soft_fail: true
```

---

## DevSecOps – Shift Left Summary

```
Cost to fix a bug:

  Requirements  │ ██  ($1x)
  Design        │ ████  ($3x)
  Development   │ ████████  ($10x)
  Testing       │ ████████████████  ($30x)
  Production    │ ██████████████████████████████  ($100x)
                └──────────────────────────────────────►

  ◄─── Shift Left: Find issues HERE, not HERE ───►
         (cheaper)                    (expensive)
```

> **The earlier you catch a security issue, the cheaper it is to fix.**

---

# PART 9: GITOPS

---

## What Is GitOps?

> **GitOps** = Using Git as the **single source of truth** for infrastructure and application delivery.

### Core Principles
1. **Declarative** – Desired state described in Git (YAML, HCL, etc.)
2. **Versioned & Immutable** – Git history = audit trail
3. **Pulled Automatically** – Agent pulls desired state from Git
4. **Continuously Reconciled** – Agent ensures reality matches Git

```
┌──────────┐   push    ┌──────────┐   pull/sync  ┌─────────────┐
│Developer │ ────────► │   Git    │ ◄──────────  │  GitOps     │
│          │           │   Repo   │              │  Agent      │
└──────────┘           └──────────┘              │ (ArgoCD/    │
                                                 │  Flux)      │
                                                 └──────┬──────┘
                                                        │
                                                        ▼ reconcile
                                                 ┌─────────────┐
                                                 │ Kubernetes  │
                                                 │ Cluster     │
                                                 └─────────────┘
```

---

## GitOps vs Traditional CI/CD

| Aspect | Traditional CI/CD | GitOps |
|--------|-------------------|--------|
| **Push vs Pull** | Pipeline **pushes** to environment | Agent **pulls** from Git |
| **Source of truth** | Pipeline state / scripts | Git repository |
| **Drift detection** | Manual / none | Automatic reconciliation |
| **Credentials** | Pipeline needs cluster access | Agent runs IN the cluster |
| **Rollback** | Re-run pipeline / manual | `git revert` → auto-reconcile |
| **Audit trail** | Pipeline logs | Git history |

### Example: Rolling back in GitOps
```bash
# Oops, bad deployment!
git revert HEAD
git push

# ArgoCD/Flux detects the change and automatically
# reconciles the cluster back to the previous state.
```

---

## GitOps Tools

| Tool | Maintained by | Description |
|------|---------------|-------------|
| **ArgoCD** | CNCF (Intuit) | Declarative GitOps for Kubernetes, web UI |
| **Flux** | CNCF (Weaveworks) | Lightweight, CLI-focused, Kustomize native |
| **Rancher Fleet** | SUSE | Multi-cluster GitOps at scale |

### ArgoCD Architecture
```
┌──────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                  │
│                                                      │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │ ArgoCD   │  │ ArgoCD Repo   │  │ ArgoCD       │  │
│  │ Server   │  │ Server        │  │ Application  │  │
│  │ (UI/API) │  │ (syncs Git)   │  │ Controller   │  │
│  └──────────┘  └───────┬───────┘  └──────┬───────┘  │
│                        │                 │           │
│                        ▼                 ▼           │
│               ┌──────────────┐   ┌──────────────┐   │
│               │  Git Repo    │   │  K8s         │   │
│               │  (desired)   │   │  Resources   │   │
│               └──────────────┘   │  (actual)    │   │
│                                  └──────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## GitOps – Practical Flow for Infra Teams

```
1. Developer modifies Terraform / K8s manifests in Git
                    │
                    ▼
2. PR is opened → reviewed → CI runs (plan, lint, scan)
                    │
                    ▼
3. PR is merged to main
                    │
                    ▼
4. GitOps agent detects change
                    │
          ┌─────────┴───────────┐
          ▼                     ▼
   Kubernetes (ArgoCD)    Terraform (Atlantis)
   Auto-sync manifests    Auto-run terraform plan
   to cluster             Comment on PR, await
                          approval, then apply
```

> **Atlantis** – GitOps for Terraform: runs `plan` on PR, `apply` on merge.

---

# PART 10: GITHUB ACTIONS – HANDS-ON EXAMPLES

---

## GitHub Actions – Concepts

### Key Terms
| Term | Description |
|------|-------------|
| **Workflow** | Automated process defined in YAML (`.github/workflows/`) |
| **Event/Trigger** | What starts the workflow (`push`, `pull_request`, `schedule`) |
| **Job** | A set of steps that run on the same runner |
| **Step** | Individual task in a job (run command or use action) |
| **Action** | Reusable unit of code (from Marketplace or custom) |
| **Runner** | Machine that executes the job (GitHub-hosted or self-hosted) |

### Structure
```yaml
name: Workflow Name           # Workflow
on: [push]                    # Event/Trigger
jobs:                         # Jobs
  job-name:                   # Job
    runs-on: ubuntu-latest    # Runner
    steps:                    # Steps
      - uses: actions/checkout@v4   # Action
      - run: echo "Hello!"         # Step (shell command)
```

---

## Example 1: Terraform CI Pipeline

```yaml
# .github/workflows/terraform-ci.yml
name: Terraform CI

on:
  pull_request:
    paths:
      - 'terraform/**'
  push:
    branches: [main]
    paths:
      - 'terraform/**'

env:
  TF_VERSION: '1.7.0'
  WORKING_DIR: './terraform'

jobs:
  terraform-validate:
    name: Validate & Plan
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ env.WORKING_DIR }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

      - name: Setup TFLint
        uses: terraform-linters/setup-tflint@v4

      - name: Run TFLint
        run: tflint --recursive

      - name: Run Checkov (Security Scan)
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          soft_fail: true
          output_format: cli

  terraform-plan:
    name: Terraform Plan
    needs: terraform-validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    defaults:
      run:
        working-directory: ${{ env.WORKING_DIR }}
    env:
      ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
      ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan -out=tfplan -no-color

      - name: Comment Plan on PR
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const output = `#### Terraform Plan 📋
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            *Pushed by: @${{ github.actor }}*`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })
```

---

## Example 2: Ansible CI Pipeline

```yaml
# .github/workflows/ansible-ci.yml
name: Ansible CI

on:
  pull_request:
    paths:
      - 'ansible/**'
  push:
    branches: [main]
    paths:
      - 'ansible/**'

jobs:
  ansible-lint:
    name: Lint & Validate
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install ansible ansible-lint yamllint

      - name: Run yamllint
        run: yamllint -s ansible/

      - name: Run ansible-lint
        run: ansible-lint ansible/

      - name: Ansible Syntax Check
        run: |
          ansible-playbook ansible/gather-vm-info.yaml --syntax-check

  ansible-deploy:
    name: Run Playbook (Staging)
    needs: ansible-lint
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Ansible
        run: pip install ansible

      - name: Configure SSH Key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa

      - name: Run Playbook
        run: |
          ansible-playbook ansible/gather-vm-info.yaml \
            -i inventory/staging \
            --extra-vars "env=staging"
        env:
          ANSIBLE_HOST_KEY_CHECKING: 'false'
```

---

## Example 3: Kubernetes Manifest Validation

```yaml
# .github/workflows/k8s-ci.yml
name: Kubernetes CI

on:
  pull_request:
    paths:
      - 'kubernetes/**'

jobs:
  validate:
    name: Validate Manifests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install kubeval
        run: |
          wget https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz
          tar xf kubeval-linux-amd64.tar.gz
          sudo mv kubeval /usr/local/bin/

      - name: Validate manifests
        run: kubeval --strict kubernetes/manifest/**/*.yaml

      - name: Run kube-score
        uses: piraces/kube-score-ga@v0.3.0
        with:
          manifests-dir: kubernetes/manifest/
```

---

## Example 4: Multi-Stage Deploy Pipeline

```yaml
# .github/workflows/deploy.yml
name: Infrastructure Deploy

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  plan:
    name: Terraform Plan
    runs-on: ubuntu-latest
    outputs:
      has_changes: ${{ steps.plan.outputs.exitcode }}
    env:
      ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
      ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
      ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: terraform/
      - name: Terraform Plan
        id: plan
        run: terraform plan -detailed-exitcode -out=tfplan
        working-directory: terraform/
        continue-on-error: true
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: terraform/tfplan

  deploy-staging:
    name: Deploy to Staging
    needs: plan
    if: needs.plan.outputs.has_changes == '2'
    runs-on: ubuntu-latest
    environment: staging     # Requires manual approval in GitHub
    env:
      ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
      ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.STAGING_SUBSCRIPTION_ID }}
      ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan
          path: terraform/
      - run: terraform init
        working-directory: terraform/
      - run: terraform apply -auto-approve tfplan
        working-directory: terraform/

  deploy-production:
    name: Deploy to Production
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval in GitHub
    env:
      ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
      ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.PROD_SUBSCRIPTION_ID }}
      ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: terraform/
      - run: terraform plan -out=tfplan
        working-directory: terraform/
      - run: terraform apply -auto-approve tfplan
        working-directory: terraform/
```

---

## Example 5: Complete DevSecOps Pipeline

```yaml
# .github/workflows/devsecops.yml
name: DevSecOps Pipeline

on:
  pull_request:
    branches: [main]

jobs:
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Gitleaks – Secret Scanning
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Checkov – IaC Security
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          soft_fail: true

      - name: Trivy – Vulnerability Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          exit-code: '0'

      - name: KICS – IaC Analysis
        uses: Checkmarx/kics-github-action@v2.1.0
        with:
          path: terraform/,kubernetes/,ansible/
          fail_on: high
```

---

## GitHub Actions – Useful Triggers

```yaml
# On push to specific branches
on:
  push:
    branches: [main, develop]

# On pull request
on:
  pull_request:
    branches: [main]

# On schedule (cron)
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6 AM

# Manual trigger
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [dev, staging, prod]

# On tag creation
on:
  push:
    tags: ['v*']

# On file changes (path filter)
on:
  push:
    paths:
      - 'terraform/**'
      - '!terraform/README.md'  # Exclude docs
```

---

## GitHub Actions – Reusable Workflows

```yaml
# .github/workflows/reusable-terraform.yml
name: Reusable Terraform Workflow

on:
  workflow_call:
    inputs:
      working_directory:
        required: true
        type: string
      environment:
        required: true
        type: string
    secrets:
      ARM_CLIENT_ID:
        required: true
      ARM_CLIENT_SECRET:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
        working-directory: ${{ inputs.working_directory }}
      - run: terraform apply -auto-approve
        working-directory: ${{ inputs.working_directory }}
        env:
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
```

### Calling the reusable workflow:
```yaml
# .github/workflows/deploy-hub.yml
name: Deploy Hub Network
on:
  push:
    branches: [main]
jobs:
  deploy:
    uses: ./.github/workflows/reusable-terraform.yml
    with:
      working_directory: terraform/
      environment: production
    secrets: inherit
```

---

# PART 11: SUMMARY & KEY TAKEAWAYS

---

## Key Takeaways

### Git
- Git is the **foundation** of DevOps – everything starts here
- Learn the basics: `clone`, `add`, `commit`, `push`, `pull`, `branch`
- Use **Pull Requests** for every change – even your own code
- Adopt **GitHub Flow** as your branching strategy

### CI/CD
- **CI** = Build & Test on every change (fast feedback)
- **CD** = Automated delivery/deployment to environments
- Start simple, iterate – you don't need everything on day one

### Security
- **Shift left** – scan for security issues in the pipeline
- **Never commit secrets** to Git
- Use secrets managers (Key Vault, GitHub Secrets)

### GitOps
- Git as the single source of truth for infrastructure
- Pull-based model with tools like ArgoCD, Flux, Atlantis

---

## What's Next?

| Session | Topic | Status |
|---------|-------|--------|
| Session 1 | DevOps Theory & Culture | ✅ Done |
| Session 2 | Azure Portal GUI | ✅ Done |
| Session 3 | IaC – Terraform & Ansible | ✅ Done |
| Session 4 | Git & CI/CD Pipelines | ✅ Today |
| Session 5 | Containers & Kubernetes | 🔜 Next |
| Session 6 | Monitoring & Observability | 📋 Planned |

---

## Recommended Resources

### Git
- [Pro Git Book](https://git-scm.com/book/en/v2) (free)
- [Learn Git Branching](https://learngitbranching.js.org/) (interactive)
- [Oh Shit, Git!?!](https://ohshitgit.com/) (fixing mistakes)

### CI/CD & GitHub Actions
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Terraform GitHub Actions](https://github.com/hashicorp/setup-terraform)

### DevSecOps
- [Checkov Documentation](https://www.checkov.io/)
- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)

### GitOps
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [OpenGitOps](https://opengitops.dev/)

---

## Q&A

### Discussion Questions:
1. Which branching strategy fits our team best?
2. What CI checks should we implement first?
3. How do we handle Terraform state in CI/CD?
4. Should we adopt GitOps for our Kubernetes deployments?

> **Thank you!**
