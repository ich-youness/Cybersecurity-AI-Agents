# Cybersecurity Multi-Agent Automation with CrewAI

---

## 📖 Project Overview

**Cybersecurity Multi-Agent Automation with CrewAI** is a comprehensive, modular platform for automating cybersecurity reconnaissance and reporting using a multi-agent system built on [crewAI](https://crewai.com).  

It orchestrates a suite of specialized AI agents and tools to perform:
- Web security scans  
- Vulnerability assessments  
- Automated reporting  

Results are delivered seamlessly via **Telegram integration**.

---

## 🚀 Key Features

- **Multi-Agent Orchestration**  
  - Agents are defined for reconnaissance, reporting, HTML report generation, and Telegram result delivery.  
  - Each agent is configurable via YAML files for roles, goals, and backstories.

- **Automated Reconnaissance & Scanning**  
  - Supports a wide range of security tools:  
    *Nmap, OWASP ZAP, DirBuster, SQLMap, SSL scanner, Metasploit, Sublist3r, Whois, DNSRecon, Scrapy, WAFW00F,* and more.  
  - Performs targeted scans based on user input.

- **Centralized Data Management**  
  - Scan results are stored in a **PostgreSQL** database.  
  - Enables result caching, historical lookups, and efficient reporting.

- **Automated Reporting**  
  - Generates detailed, customizable reports in **text, HTML, and PDF** formats.  
  - Covers executive summaries, methodologies, technical findings, and recommendations.

- **Telegram Integration**  
  - Automatically sends scan results and reports to users via **Telegram**.  
  - Ensures fast and secure delivery.

---

## ⚙️ Configuration

- **Agents & Tasks**  
  - Define and customize agents in `agents.yaml`.  
  - Define and customize tasks in `tasks.yaml`.

- **Custom Tools**  
  - Extend functionality by adding new tools in the `tools/` directory.

---

## 🛠️ Usage

### 1. Install Dependencies

Ensure **Python 3.10–3.12** and [UV](https://docs.astral.sh/uv/) are installed.  

```bash
pip install uv
crewai install
```

The system will:

- Execute the configured scans
- Generate reports  
- Send results via Telegram

## 🔄 Typical Workflow

1. User specifies scan targets and desired tools
2. Recon agent performs scans and stores results
3. Reporting agent compiles findings into detailed reports
4. HTML agent generates visually rich reports
5. Telegram agent delivers results to the user
