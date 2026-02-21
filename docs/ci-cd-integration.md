# CI/CD Integration: Continuous AI Security Testing

Integrate Strix into your GitHub Actions pipeline to automatically scan every pull request for vulnerabilities, post findings as PR comments, and block merges that introduce security issues.

## Overview

```
PR Opened/Updated
    → GitHub Actions triggers Strix scan
    → AI agents analyze changed code
    → Findings posted as PR comments with PoC evidence
    → PR check fails if critical/high vulnerabilities found
    → Merge blocked until issues resolved
```

This gives you **continuous pentesting on every PR** rather than annual audits.

## GitHub Actions Workflow

### Full Workflow

Create `.github/workflows/security-scan.yml`:

```yaml
name: AI Security Scan

on:
  pull_request:
    branches: [main, develop]
  # Optional: scheduled full scans
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM UTC

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  security-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for accurate diff analysis

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Strix
        run: |
          python -m pip install --upgrade pip pipx
          pipx install strix-agent

      - name: Run Security Scan
        run: strix -n -t ./ --scan-mode quick --output json --output-path ./strix-report.json
        env:
          STRIX_LLM: ${{ vars.STRIX_LLM || 'openai/gpt-4o' }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

      - name: Upload Scan Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: strix-security-report
          path: ./strix-report.json
          retention-days: 30

      - name: Check for Critical Findings
        if: always()
        run: |
          if [ -f ./strix-report.json ]; then
            CRITICAL=$(python3 -c "
          import json, sys
          with open('./strix-report.json') as f:
              report = json.load(f)
          findings = report.get('findings', [])
          critical_high = [f for f in findings if f.get('severity') in ('CRITICAL', 'HIGH')]
          print(len(critical_high))
          ")
            if [ "$CRITICAL" -gt 0 ]; then
              echo "::error::Found $CRITICAL critical/high severity vulnerabilities. See scan report for details."
              exit 1
            fi
          fi
```

### Configuration Variables and Secrets

In your GitHub repository settings:

**Secrets** (Settings → Secrets and variables → Actions → Secrets):
- `LLM_API_KEY` — Your LLM provider API key

**Variables** (Settings → Secrets and variables → Actions → Variables):
- `STRIX_LLM` — Model identifier (e.g., `openai/gpt-4o`, `anthropic/claude-sonnet-4`)

## Scan Modes for CI/CD

| Mode | Use Case | Approximate Token Usage |
|------|----------|------------------------|
| `quick` | PR checks, fast feedback | Lower |
| `standard` | Pre-merge validation | Moderate |
| `full` | Scheduled scans, release gates | Higher |

### Quick Scan (Recommended for PRs)

Focuses on changed files and their immediate dependencies:

```yaml
- name: Run Quick Scan
  run: strix -n -t ./ --scan-mode quick
```

### Full Scan (Scheduled)

Comprehensive scan of the entire codebase:

```yaml
- name: Run Full Scan
  run: strix -n -t ./ --scan-mode full
```

### Focused Scan (Custom)

Target specific areas:

```yaml
- name: Run Auth-Focused Scan
  run: strix -n -t ./ --instructions "Focus on authentication, session management, and access control"
```

## Branch Protection Rules

To enforce security scanning, configure branch protection:

1. Go to **Settings → Branches → Branch protection rules**
2. Add rule for `main` (or your default branch)
3. Enable **Require status checks to pass before merging**
4. Add `security-scan` as a required check
5. Enable **Require branches to be up to date before merging**

This prevents any PR from merging until the Strix scan passes.

## Cost Management

### Controlling LLM Token Usage

Each scan consumes LLM API tokens. To manage costs:

1. **Use `quick` mode for PRs** — Scans only changed code, uses fewer tokens
2. **Use `full` mode on schedule** — Run comprehensive scans weekly, not per-PR
3. **Set token budgets** — Configure maximum token spend per scan
4. **Skip scans for non-code changes** — Add path filters:

```yaml
on:
  pull_request:
    branches: [main]
    paths:
      - '**.py'
      - '**.js'
      - '**.ts'
      - '**.go'
      - '**.java'
      - '**.rb'
      # Skip docs-only PRs
      - '!**.md'
      - '!docs/**'
```

### Caching

Cache Strix's reconnaissance data to speed up repeated scans:

```yaml
- name: Cache Strix Data
  uses: actions/cache@v4
  with:
    path: ~/.strix/cache
    key: strix-${{ hashFiles('**/requirements.txt', '**/package-lock.json') }}
```

## Multiple Environments

### Staging Deployment Scan

Scan a live staging environment after deployment:

```yaml
  scan-staging:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Strix
        run: pipx install strix-agent
      - name: Scan Staging
        run: strix -n -t https://staging.yourapp.com --scan-mode standard
        env:
          STRIX_LLM: ${{ vars.STRIX_LLM }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
```

## Interpreting CI Results

### Passing Scan

```
✓ AI Security Scan — No critical or high severity vulnerabilities found
  → 3 medium, 2 low findings (see report artifact for details)
```

### Failing Scan

```
✗ AI Security Scan — 2 critical vulnerabilities found
  → CRITICAL: SQL Injection in api/users.py:47 (PoC attached)
  → CRITICAL: IDOR in api/invoices.py:123 (PoC attached)
  → See strix-security-report artifact for full details
```

### Reviewing Findings

1. Click on the failed check in the PR
2. Download the `strix-security-report` artifact
3. Each finding includes the full exploit PoC, request/response chain, and remediation steps
4. Fix the issues and push — the scan will re-run automatically

## Comparison: Before and After

### Before (Traditional Approach)

```
Developer writes code → Merges to main → Annual pentest finds SQLi
→ 11 months of exposure → Emergency fix → $30K pentest cost
```

### After (Continuous AI Testing)

```
Developer writes code → Opens PR → Strix finds SQLi in 10 minutes
→ PR blocked → Developer fixes before merge → Zero exposure
→ Marginal LLM API cost per scan
```
