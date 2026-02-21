# Setup Guide: AI-Driven Penetration Testing with Strix

This guide walks through installing Strix, configuring it, running your first scan, and interpreting results.

## Prerequisites

- **Python 3.12+** (required)
- **Docker** (required for sandboxed exploitation)
- **An LLM API key** (OpenAI, Anthropic, or any LiteLLM-compatible provider)
- **pipx** (recommended for isolated installation)

## Step 1: Install Strix

### Option A: pipx (Recommended)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install Strix
pipx install strix-agent
```

### Option B: Install Script

```bash
curl -sSL https://strix.ai/install | bash
```

### Option C: pip (In a Virtual Environment)

```bash
python3 -m venv strix-env
source strix-env/bin/activate
pip install strix-agent
```

### Verify Installation

```bash
strix --version
# Expected output: strix 0.8.x
```

## Step 2: Configure Your LLM Provider

Strix uses LLMs to power its agents. You need to configure which model to use and provide an API key.

```bash
# OpenAI
export STRIX_LLM="openai/gpt-4o"
export LLM_API_KEY="sk-..."

# Anthropic
export STRIX_LLM="anthropic/claude-sonnet-4"
export LLM_API_KEY="sk-ant-..."

# Any LiteLLM-compatible provider
export STRIX_LLM="provider/model-name"
export LLM_API_KEY="your-key"
```

For persistent configuration, add these to your shell profile (`~/.bashrc`, `~/.zshrc`) or use a `.env` file (never commit this):

```bash
# .env (add to .gitignore!)
STRIX_LLM=openai/gpt-4o
LLM_API_KEY=sk-...
```

## Step 3: Ensure Docker Is Running

Strix runs exploits inside Docker containers for isolation. Make sure Docker is running:

```bash
docker info
# Should show Docker daemon information without errors
```

## Step 4: Run Your First Scan

### Scan Local Source Code

```bash
strix --target ./path/to/your/project
```

### Scan a GitHub Repository

```bash
strix --target https://github.com/your-org/your-repo
```

### Scan a Live Web Application

```bash
strix --target https://staging.yourapp.com
```

### Scan with Focus Areas

```bash
# Focus on authentication
strix --target ./app --instructions "Focus on authentication and session management"

# Focus on injection flaws
strix --target ./app --instructions "Prioritize SQL injection, command injection, and SSRF"

# Quick scan for CI/CD
strix -n -t ./app --scan-mode quick
```

## Step 5: Use the Included Vulnerable App

This repository includes an intentionally vulnerable Flask application for safe testing.

### Start the Vulnerable App

```bash
cd vulnerable-app
docker compose up -d
```

This starts:
- A Flask web app on `http://localhost:5000` with intentional vulnerabilities
- A PostgreSQL database with seed data

### Run Strix Against It

```bash
# Black-box scan against the running app
strix --target http://localhost:5000

# White-box scan against the source code
strix --target ./vulnerable-app

# Combined: both source and live target
strix --target ./vulnerable-app --url http://localhost:5000
```

### Stop the Vulnerable App

```bash
cd vulnerable-app
docker compose down -v
```

## Step 6: Interpret Results

Strix produces structured reports. Each finding includes:

### Finding Structure

```
CRITICAL: SQL Injection in /api/login
├── Description: Time-based blind SQL injection via 'username' parameter
├── CVSS Score: 9.8
├── Evidence:
│   ├── Request: POST /api/login {"username": "admin' AND SLEEP(5)--", ...}
│   ├── Response Time: 5,003ms (vs. baseline 45ms)
│   └── Confirmation: Payload triggered consistent 5-second delay
├── Proof of Concept:
│   ├── Full HTTP request/response saved
│   └── Exploitation steps documented
├── Impact: Full database access, authentication bypass
└── Remediation:
    ├── Use parameterized queries / prepared statements
    ├── Input validation on username field
    └── Code location: app.py:47
```

### Report Formats

Strix generates reports in multiple formats:
- **HTML** — Interactive report with collapsible findings, suitable for sharing
- **JSON** — Machine-readable format for integration with other tools
- **Terminal** — Color-coded CLI output during the scan

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| CRITICAL | Actively exploitable, high impact | Fix immediately |
| HIGH | Exploitable with moderate difficulty | Fix before next release |
| MEDIUM | Requires specific conditions to exploit | Plan remediation |
| LOW | Minor issue, limited impact | Address in regular maintenance |
| INFO | Observation, not a vulnerability | Review for best practices |

## Step 7: Configuration File

For repeatable scans, use a configuration file. See `strix-config/strix.yml` for a template:

```yaml
target: ./app
scan_mode: full
instructions: "Focus on OWASP Top 10"
output:
  format: html
  path: ./strix-reports/
```

Run with config:

```bash
strix --config strix-config/strix.yml
```

## Troubleshooting

### "Docker not found" Error

```bash
# Install Docker
# On Ubuntu/Debian:
sudo apt-get update && sudo apt-get install docker.io docker-compose-plugin
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and back in
```

### "Python 3.12 required" Error

```bash
# Install Python 3.12+
# On Ubuntu:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.12
```

### LLM API Errors

- Verify your API key is correct and has sufficient credits
- Check that the model name matches your provider's naming convention
- Ensure your network can reach the LLM API endpoint

### Scan Hangs or Runs Too Long

- Use `--scan-mode quick` for faster scans
- Add `--timeout 600` to set a 10-minute timeout
- For large codebases, use `--instructions` to focus on specific areas

## Next Steps

- [Threat Testing Methodology](threat-methodology.md) — Understand how AI agents approach security differently
- [CI/CD Integration](ci-cd-integration.md) — Automate scanning on every pull request
- [Fact-Check Analysis](fact-check.md) — Detailed verification of Strix's claimed capabilities
