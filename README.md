# Test Against Active AI Threats Using Claude Code to Help

A comprehensive guide and toolkit for testing application security using AI-driven penetration testing agents — specifically **Strix**, an open-source framework of autonomous AI agents that find vulnerabilities and validate them with working proof-of-concept exploits.

## The Problem with Traditional Security Testing

| Approach | Cost | Speed | False Positives | Proof of Exploit |
|----------|------|-------|-----------------|------------------|
| Manual pentest | $15,000–$50,000+ | 2–4 weeks | Low | Yes |
| SAST/DAST tools (Snyk, Veracode, etc.) | $10,000–$30,000/year | Minutes | High | No |
| **AI agent pentesting (Strix)** | **Free (open source)** | **Minutes to hours** | **Low (PoC-validated)** | **Yes** |

Traditional scanners flag "possible" vulnerabilities. You then spend hours manually verifying each one. A human pentest gives you proof but costs five figures and happens once or twice a year. AI-driven pentesting agents change this equation by automating dynamic exploitation and delivering validated findings with real evidence.

## What Is Strix?

[Strix](https://github.com/usestrix/strix) is an open-source (Apache 2.0) AI penetration testing framework. Teams of AI agents coordinate like a real pentest squad:

- **Recon Agent** — Maps your attack surface, discovers endpoints, identifies technologies
- **Auth/Session Agent** — Probes authentication flows, session handling, JWT weaknesses
- **Exploit Agent** — Writes and executes actual exploits, confirms they work, saves proof
- **Reporting Agent** — Documents findings with full request/response chains and remediation steps

### How It Differs from Static Scanners

A traditional scanner says: *"Possible SQL injection on /api/login"*

Strix does this instead:
1. Identifies the injection point
2. Crafts a payload (e.g., time-based blind SQLi)
3. Sends the request
4. Measures response timing to confirm exploitation
5. Saves the full HTTP request/response as proof
6. Generates remediation guidance

### Verified Capabilities

| Claim | Status | Details |
|-------|--------|---------|
| Open source, Apache 2.0 | **Confirmed** | [GitHub repo](https://github.com/usestrix/strix) with ~20k stars |
| Multi-agent architecture | **Confirmed** | Specialized agents for recon, auth, exploitation, reporting |
| Scans source code, GitHub repos, live URLs | **Confirmed** | All three target types supported |
| Full toolkit (HTTP proxy, browser, terminal, Python runtime) | **Confirmed** | Ships with proxy, Playwright browser, shell, Python environment |
| Dynamic exploitation in sandboxed Docker | **Confirmed** | Runs inside Docker for isolation |
| GitHub Actions CI/CD integration | **Confirmed** | Blocks PRs that introduce vulnerabilities |
| "Zero false positives" | **Exaggerated** | Significantly *reduced* via PoC validation, but not literally zero |
| "Every finding has a working exploit" | **Aspirational** | The design goal; not guaranteed in all cases (Alpha software, v0.8.1) |
| `pip install strix-agent` | **Confirmed** | Available on PyPI; `pipx install strix-agent` recommended |

### Vulnerability Coverage

- **Access Control**: IDOR, privilege escalation, authentication bypass
- **Injection**: SQL, NoSQL, command injection, LDAP, XPath
- **Server-Side**: SSRF, XXE, insecure deserialization, path traversal
- **Client-Side**: XSS (reflected, stored, DOM), CSRF, prototype pollution
- **Business Logic**: Race conditions, workflow manipulation, price tampering
- **Auth/Session**: JWT flaws, session fixation, weak credential policies
- **Infrastructure**: Misconfigurations, exposed debug endpoints, information disclosure

## Repository Structure

```
.
├── README.md                          # This file
├── docs/
│   ├── setup-guide.md                 # Installation and configuration
│   ├── threat-methodology.md          # AI-driven threat testing methodology
│   ├── ci-cd-integration.md           # CI/CD pipeline integration guide
│   └── fact-check.md                  # Detailed fact-check of Strix claims
├── vulnerable-app/
│   ├── app.py                         # Intentionally vulnerable Flask app
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Container for safe testing
│   ├── docker-compose.yml             # Full stack with database
│   └── init.sql                       # Database seed with test data
├── strix-config/
│   ├── strix.yml                      # Strix configuration template
│   └── scan-profiles/
│       ├── quick-scan.yml             # Fast CI/CD scan profile
│       ├── full-scan.yml              # Comprehensive scan profile
│       └── auth-focused.yml           # Authentication-focused scan
└── .github/
    └── workflows/
        └── security-scan.yml          # GitHub Actions workflow
```

## Quick Start

```bash
# 1. Install Strix
pipx install strix-agent

# 2. Configure your LLM provider
export STRIX_LLM="openai/gpt-4o"      # or anthropic/claude-sonnet-4, etc.
export LLM_API_KEY="your-api-key"

# 3. Scan a local project
strix --target ./your-app-directory

# 4. Scan a GitHub repo
strix --target https://github.com/your-org/your-repo

# 5. Scan a live URL
strix --target https://staging.yourapp.com
```

## Try It on the Included Vulnerable App

```bash
# Start the vulnerable test app
cd vulnerable-app
docker compose up -d

# Run Strix against it
strix --target http://localhost:5000

# Or scan the source code directly
strix --target ./vulnerable-app
```

The included vulnerable Flask app contains intentional security flaws (SQLi, XSS, IDOR, command injection, SSRF) for safe, legal testing. See [docs/setup-guide.md](docs/setup-guide.md) for full instructions.

## CI/CD Integration

Add continuous security testing to every pull request:

```yaml
# .github/workflows/security-scan.yml (simplified)
- name: Install Strix
  run: pipx install strix-agent

- name: Run Security Scan
  run: strix -n -t ./ --scan-mode quick
  env:
    STRIX_LLM: openai/gpt-4o
    LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
```

See [docs/ci-cd-integration.md](docs/ci-cd-integration.md) for the full workflow with PR comments, artifact uploads, and merge blocking.

## Important Caveats

1. **Alpha Software** — Strix is at v0.8.1 with a "3 - Alpha" PyPI status. Expect rough edges.
2. **LLM Costs** — Each scan consumes LLM API tokens. A full scan of a large app can use significant tokens.
3. **Not a Replacement for Human Pentesters** — AI agents are a force multiplier, not a complete replacement. Complex business logic flaws and novel attack chains still benefit from human creativity.
4. **Authorization Required** — Only test applications you own or have explicit written permission to test. Unauthorized testing is illegal.
5. **Requires Python 3.12+** — The tool needs Python 3.12 or newer.

## Further Reading

- [Setup Guide](docs/setup-guide.md) — Full installation, configuration, and first scan walkthrough
- [Threat Testing Methodology](docs/threat-methodology.md) — How AI agents approach security testing differently
- [CI/CD Integration](docs/ci-cd-integration.md) — Complete GitHub Actions setup with PR gating
- [Fact-Check Analysis](docs/fact-check.md) — Detailed verification of every claim about Strix

## External Resources

- [Strix GitHub Repository](https://github.com/usestrix/strix)
- [Strix Documentation](https://docs.strix.ai)
- [Strix on PyPI](https://pypi.org/project/strix-agent/)
- [Help Net Security Coverage](https://www.helpnetsecurity.com/2025/11/17/strix-open-source-ai-agents-penetration-testing/)
- [freeCodeCamp Tutorial](https://www.freecodecamp.org/news/how-to-use-strix-the-open-source-ai-agent-for-security-testing/)
- [SOCRadar: Top 10 AI Pentest Tools](https://socradar.io/blog/top-10-ai-pentest-tools-2025/)

## License

This repository is licensed under the MIT License. Strix itself is Apache 2.0.
