# 🛡️ MSSP Agent

A lightweight Python-based agent for collecting system security data and sending it to a central dashboard (via API). Designed to be used in a modular MSSP-style Django-based monitoring platform.

---

## 🔧 Features

-  Standalone or agent-mode execution
-  Sends JSON data to your Django backend via POST
-  Includes 7 core security checks:
  - Failed SSH login attempts
  - Open ports (via nmap)
  - OS patch status (apt/yum/dnf)
  - Lynis audit results
  - System log summaries
  - ClamAV malware scan results
  - Recent CVEs from NVD feed

---

## Project Structure

```text
mssp-agent/
├── check_ssh_logins.py
├── check_open_ports.py
├── check_patch_status.py
├── run_lynis.py
├── log_summary.py
├── check_vuln_feeds.py
├── clamav_scan.py
├── install.sh         # Linux installer
├── install.py         # Cross-platform installer
├── config.json        # Created during install
├── requirements.txt
└── README.md
```

## Quick Start
### Linux 
``` curl -sSL https://yourserver.com/install.sh | sudo bash```
### Windows 
``` python3 install.py```

## Configuration
- After install, edit the generated ~/mssp-agent/config.json file:
  ```
  {
  "api_url": "https://yourserver.com/api/report/",
  "token": "your-client-token"
  }
  ```

## API Payload
```
{
  "check": "ssh_logins",
  "data": {
    "failed_logins": [
      {
        "ip": "192.168.1.10",
        "attempts": 5,
        "usernames": ["admin", "root"]
      }
    ]
  },
  "token": "<insert client token>"
}
```
## Dependencies
``` pip install -r requirements.txt ```
- TBC

