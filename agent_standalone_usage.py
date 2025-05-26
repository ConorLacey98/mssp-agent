### check_open_ports - Agent Usage Example
# This script demonstrates how to use the check_open_ports module to scan for open ports
import check_open_ports
import requests

result = check_open_ports.run_scan("127.0.0.1")
requests.post("https://your-server.com/api/report/", json={
    "check": "open_ports",
    "data": result,
    "token": "your-agent-token"
})
# Standalone Terminal Use:
# python3 check_open_ports.py --target 192.168.1.1 --ports 22,80,443 --json



### check_vuln_feeds - Agent Usage Example
import check_vuln_feeds
import requests

result = check_vuln_feeds.fetch_recent_cves(days=3, keyword="linux")
requests.post("https://your-server.com/api/report/", json={
    "check": "vuln_feeds",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
#python3 check_vuln_feeds.py --days 2 --keyword openssh --json



### check_patch_status - Agent Usage Example
import check_patch_status
import requests

result = check_patch_status.check_patch_status()
requests.post("https://your-server.com/api/report/", json={
    "check": "patch_status",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
# python3 check_patch_status.py --json



### run_lynis - Agent Usage Example
import run_lynis
import requests

result = run_lynis.run_lynis_scan()
requests.post("https://your-server.com/api/report/", json={
    "check": "lynis_audit",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
# python3 run_lynis.py --json



### clamav_scan - Agent Usage Example
import clamav_scan
import requests

result = clamav_scan.run_clamav_scan("/home")
requests.post("https://your-server.com/api/report/", json={
    "check": "clamav",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
# scan /home:
#sudo python3 clamav_scan.py --dir /home --json
# scan root:
# sudo python3 clamav_scan.py --json



### log_summary - Agent Usage Example
import log_summary
import requests

result = log_summary.summarize_logs()
requests.post("https://your-server.com/api/report/", json={
    "check": "log_summary",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
# sudo python3 log_summary.py --json



### check_ssh_logins - Agent Usage Example
import check_ssh_logins
import requests

log_path = check_ssh_logins.find_log_file()
result = check_ssh_logins.parse_ssh_failures(log_path, days_back=1)
requests.post("https://your-server.com/api/report/", json={
    "check": "ssh_logins",
    "data": result,
    "token": "your-agent-token"
})

# Standalone Terminal Use:
# sudo python3 check_ssh_logins.py --days 1 --json