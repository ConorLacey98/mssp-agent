import os
import platform
import shutil
import json
import subprocess

AGENT_DIR = os.path.expanduser("~/mssp-agent")
PY_SCRIPTS = [
    "check_ssh_logins.py", "check_open_ports.py", "check_patch_status.py",
    "run_lynis.py", "log_summary.py", "check_vuln_feeds.py", "clamav_scan.py"
]

def install_scripts():
    print(f"[*] Creating agent directory at {AGENT_DIR}")
    os.makedirs(AGENT_DIR, exist_ok=True)

    for script in PY_SCRIPTS:
        shutil.copy(script, os.path.join(AGENT_DIR, script))
    print("[*] Scripts copied.")

    config = {
        "api_url": "https://your-server.com/api/report/",
        "token": "REPLACE_WITH_YOUR_CLIENT_TOKEN"
    }

    with open(os.path.join(AGENT_DIR, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    print("[*] config.json written.")

def schedule_task():
    os_type = platform.system()
    script_path = os.path.join(AGENT_DIR, "check_ssh_logins.py")

    if os_type == "Linux":
        cron_line = f"0 */6 * * * python3 {script_path} --json | curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Token REPLACE_WITH_YOUR_CLIENT_TOKEN' -d @- https://your-server.com/api/report/"
        cron_file = "/etc/cron.d/mssp-agent"
        try:
            with open(cron_file, "w") as f:
                f.write(cron_line + "\n")
            print("[✓] Cron job created.")
        except PermissionError:
            print("[!] Permission denied: run as sudo to install cron job.")
    elif os_type == "Windows":
        print("[*] Detected Windows. Scheduling task...")
        try:
            subprocess.run([
                "schtasks", "/Create",
                "/SC", "HOURLY",
                "/TN", "MSSPAgent",
                "/TR", f"python {script_path}",
                "/F"
            ], check=True)
            print("[✓] Scheduled task created.")
        except Exception as e:
            print("[!] Failed to create Windows task:", e)
    else:
        print("[!] Unsupported OS:", os_type)

if __name__ == "__main__":
    install_scripts()
    schedule_task()