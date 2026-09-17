
<div align="center">

# 🔴 Red Team vs Blue Team Lab

A Complete Cybersecurity Attack-Defense Lifecycle Project

</div>


## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Team Members](#-team-members)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Vulnerabilities](#-vulnerabilities)
- [Project Lifecycle](#-project-lifecycle)
- [Quick Start](#-quick-start)
- [Repository Structure](#-repository-structure)
- [Detection Queries](#-detection-queries)
- [Security Fixes](#-security-fixes)
- [Key Findings](#-key-findings)
- [Screenshots](#-screenshots)
- [Disclaimer](#-disclaimer)
- [References](#-references)

---

## 🎯 Project Overview

This project demonstrates a **full-spectrum cybersecurity exercise** covering the entire lifecycle of a web application security assessment — from intentional vulnerability introduction to exploitation, detection, incident response, and secure remediation.

A deliberately vulnerable **Flask web application** was built and deployed behind an **Apache web server** with **mod_wsgi**. The application was then subjected to a **black-box penetration test**, with all activities monitored by a **Wazuh SIEM** platform. The Blue Team reconstructed the attack timeline from logs, performed containment, and authored detection rules. Finally, all vulnerabilities were patched using secure coding practices, with changes tracked via **Git version control**.

&gt; **Implementation Note:** The lab was deployed on a single Kali Linux VM hosting all three logical roles (Target, SIEM, and Attacker), as permitted by the project scope.

---

## 👥 Team Members

| **Yousef Alhawi** | Student 1: Architecture & Visibility + Student 4: Mitigation & Re-Exploitation | Built the lab environment, deployed the vulnerable app, configured Wazuh SIEM, set up log forwarding, applied all code patches, and maintained Git version control. |

| **Yazan Alkhalaileh** | Student 2: Offensive (Red Team) | Performed black-box penetration testing, enumerated the attack surface, exploited all vulnerabilities, achieved RCE via webshell, and documented all findings. |

| **Alaa Alrteimeh** | Student 3: Defensive (Blue Team / IR) | Reconstructed the attack timeline from SIEM logs and bash history, performed containment by removing attacker artifacts, checked for persistence, and built custom Wazuh detection queries. |

---

## 🏗️ Architecture & Tech Stack

### Environment
| Component | Specification |
|-----------|---------------|
| **Operating System** | Kali Linux 2025.4-vmware-amd64 |
| **Hostname** | kali |
| **IP Address** | 127.0.0.1 (localhost) / 192.168.x.x (network) |
| **CPU** | 4 cores |
| **Memory** | 4 GB |
| **Disk Space** | 80.1 GB |

### Application Stack
- **Backend Framework:** Python Flask
- **Web Server:** Apache HTTP Server 2.4
- **WSGI Module:** libapache2-mod-wsgi-py3
- **Database:** SQLite3
- **Deployment Path:** `/var/www/vulnerable-app/`

### Security Stack
- **SIEM:** Wazuh 4.7 (Indexer + Server + Dashboard)
- **Log Sources:** Apache access.log, Apache error.log, bash history
- **Attacker Tools:** Nmap, Gobuster, WhatWeb, Nessus, curl

---

## 🎯 Vulnerabilities

The application exposes four endpoints, each intentionally vulnerable:

| # | Endpoint | Vulnerability | Root Cause | Impact |
|---|----------|---------------|------------|--------|
| 1 | `/upload` | **Unrestricted File Upload** | No file type/extension validation | RCE via PHP webshell |
| 2 | `/ping` | **OS Command Injection** | User input passed directly to `os.popen()` | Arbitrary command execution |
| 3 | `/search` | **Reflected XSS** | Unsanitized user input reflected in HTML | Session hijacking, credential theft |
| 4 | `/login` | **SQL Injection** | Dynamic SQL built via string concatenation | Authentication bypass, data exfiltration |

---

## 🔄 Project Lifecycle

### Phase 1: Architecture & Visibility (Student 1)
- Built the vulnerable Flask application from scratch
- Deployed Apache + mod_wsgi configuration
- Installed and configured Wazuh 4.7 SIEM
- Set up log forwarding for Apache logs and bash history
- Verified log ingestion and index confirmation in Wazuh Discover

### Phase 2: Penetration Testing (Student 2)
- **Reconnaissance:** Nmap port scan, WhatWeb fingerprinting, Gobuster directory enumeration, wafw00f WAF detection
- **Vulnerability Assessment:** Manual testing confirmed all 4 vulnerabilities
- **Exploitation:** Achieved RCE via PHP webshell uploaded through `/upload`, leveraged Command Injection on `/ping`, bypassed login via SQLi, and executed reflected XSS on `/search`
- **Post-Exploitation:** Executed `whoami`, `ls`, and `/etc/passwd` via webshell `cmd` parameter

### Phase 3: Incident Response & Detection (Student 3)
- Analyzed Wazuh SIEM alerts and Apache access logs
- Reconstructed the full attack timeline with timestamps
- Identified and removed 4 malicious artifacts: `shell.php`, `rev-shell.php`, `rev-shell.py`, `test.php`
- Verified no persistence mechanisms (`crontab -l` returned empty)
- Authored 4 custom Wazuh Discover detection queries

### Phase 4: Mitigation & Re-Exploitation (Student 4)
- Initialized Git repository in `/var/www/vulnerable-app/`
- Committed the vulnerable baseline (`4efcc9e`)
- Applied secure coding fixes for all 4 vulnerabilities
- Committed the patched version (`4b3b79f`)
- Restarted Apache and verified the "Secure Web App (Patched)" page
- Re-ran all exploit payloads — **all blocked or neutralized**
- Re-ran Student 3's detection queries against re-test logs — **all fired correctly**

---

## 🚀 Quick Start

### Prerequisites
```bash
sudo apt update
sudo apt install python3 python3-pip apache2 libapache2-mod-wsgi-py3 sqlite3
