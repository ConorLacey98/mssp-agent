import os
import re
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta

def find_log_file():
    """
    Detects the appropriate SSH log file.
    """
    candidates = ["/var/log/auth.log", "/var/log/secure"]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def parse_ssh_failures(log_path, days_back=1):
    """
    Parses the log file and summarizes failed SSH login attempts.
    """
    failures = defaultdict(lambda: {"count": 0, "usernames": set()})
    now = datetime.now()
    cutoff = now - timedelta(days=days_back)

    date_re = re.compile(r'^([A-Z][a-z]{2} +\d{1,2}) ')
    ssh_re = re.compile(r'Failed password for (invalid user )?(\S+) from ([\d.]+)')

    try:
        with open(log_path, "r", errors="ignore") as f:
            for line in f:
                # Filter by timestamp
                date_match = date_re.match(line)
                if not date_match:
                    continue
                log_date_str = date_match.group(1)
                try:
                    log_date = datetime.strptime(log_date_str + f" {now.year}", "%b %d %Y")
                    if log_date < cutoff:
                        continue
                except:
                    continue

                # Parse failed login
                match = ssh_re.search(line)
                if match:
                    username = match.group(2)
                    ip = match.group(3)
                    entry = failures[ip]
                    entry["count"] += 1
                    entry["usernames"].add(username)

    except Exception as e:
        return {"error": str(e)}

    # Format result
    result = []
    for ip, data in failures.items():
        result.append({
            "ip": ip,
            "attempts": data["count"],
            "usernames": sorted(data["usernames"])
        })

    return {"failed_logins": result}

def main():
    parser = argparse.ArgumentParser(description="Parse SSH login failures from system logs.")
    parser.add_argument("--days", type=int, default=1, help="Days to look back")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    log_file = find_log_file()
    if not log_file:
        print("Error: No suitable SSH log file found.", file=sys.stderr)
        sys.exit(1)

    result = parse_ssh_failures(log_file, args.days)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        else:
            print(f"SSH Failed Login Summary (last {args.days} day(s)):")
            for entry in result["failed_logins"]:
                print(f" - IP: {entry['ip']}, Attempts: {entry['attempts']}, Usernames: {', '.join(entry['usernames'])}")

if __name__ == "__main__":
    main()