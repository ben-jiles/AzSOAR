# AzSOAR - Azure Sentinel SOAR Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Azure](https://img.shields.io/badge/Azure-Sentinel-blue)

**A modern Python CLI + framework to rapidly generate, test, deploy, and orchestrate advanced SOAR playbooks for Microsoft Sentinel.**

## ✨ Key Features

- ⚡ Fast playbook generation using Bicep + Logic Apps templates
- 🧪 Local testing & simulation framework (test safely without production)
- 🔐 Secure Azure authentication (Default, CLI, Managed Identity, Service Principal)
- 📦 Rich library of enrichment & response actions
- 📊 Execution logging, analytics, and Streamlit web dashboard
- 🔄 Highly extensible and developer-friendly

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/ben-jiles/azsoar.git
cd azsoar

python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

pip install -e .

# 2. Configure Azure
azsoar config --tenant <TENANT_ID> --subscription <SUBSCRIPTION_ID> --workspace <WORKSPACE_ID>
azsoar login
```

Ensure you have Azure CLI installed as a prerequisite for login.

### Generate & Test Your First Playbook

```bash
# Generate
azsoar generate phishing-response --name my-first-playbook

# Test locally
azsoar test ./playbooks/my-first-playbook --scenario phishing
```

## Available Commands

| Command          | Description                              |
|------------------|------------------------------------------|
| `generate`       | Generate playbook from template          |
| `test`           | Run local simulation                     |
| `enrich`         | Enrich incident with context             |
| `action`         | Execute response actions                 |
| `history`        | View execution history                   |
| `analytics`      | Show success rate & metrics              |
| `dashboard`      | Launch web dashboard                     |

## Project Structure

```
azsoar/
├── azsoar/                  # Main package
│   ├── cli.py
│   ├── config.py
│   ├── generator.py
│   ├── enrich/
│   ├── actions/
│   ├── test/
│   ├── monitoring/
│   └── dashboard.py
├── azsoar/templates/        # Ready-to-use playbook templates
├── samples/
├── docs/
├── run_dashboard.py
└── pyproject.toml
```

## Security Disclaimer

> **This tool is for authorized security operations only.**  
> Use only on environments you own or have explicit written permission to automate.  
> Always follow your organization's change management and approval processes.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License © 2026 [Benjamin Jiles]

---

**Built for Azure Security Professionals, SOC Teams, and Ethical Hackers.**
