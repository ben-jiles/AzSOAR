# AzSOAR - Azure Sentinel SOAR Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
![GitHub stars](https://img.shields.io/github/stars/YOURUSERNAME/azsoar)

**A modern Python framework to build, test, and run advanced SOAR playbooks for Microsoft Sentinel.**

## ✨ Features
- 🚀 CLI for rapid playbook generation (Bicep + ARM)
- 🧪 Local testing & simulation of Sentinel incidents
- 🔐 Secure Azure authentication (Managed Identity, CLI, SP)
- 📦 Rich library of enrichment & response actions
- 📊 Monitoring and cost insights

## Quick Start

```bash
pip install azsoar
azsoar --help
azsoar generate phishing-response --output ./playbooks
