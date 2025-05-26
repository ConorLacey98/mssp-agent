import subprocess
import os
import shutil
import argparse
import json
import sys
from datetime import datetime, timedelta

def run_logwatch_summary():
    """
    Runs logwatch and captures the summary output.
    """
    try:
        result = subprocess.run(["logwatch", "--range", "yesterday", "--detail", "low", "--service", "All", "--format", "text"],
                                capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {"error": f"logwatch failed: {result.stderr.strip()}"}

        return {"logwatch_summary": result.stdout.strip()[:5000]}  # cap size to avoid overload
    except Exception as e:
        return {"error": str(e)}

def custom_log_summary():
    """
    Custom log summary fallback: counts important events from syslog/auth.log.
    """
    log_files = [
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/auth.log",
        "/var/log/secure"
    ]

    summary = {
        "found_files": [],
        "event_counts": {}
    }

    today = datetime.today()
    yesterday = today - timedelta(days=1)
    date_patterns = [today.strftime("%b %_d"), yesterday.strftime("%b %_d")]

    keywords = ["failed", "error", "denied", "unauthorized", "segfault"]

    for fpath in log_files:
        if not os.path.exists(fpath):
            continue

        summary["found_files"].append(fpath)
        try:
            with open(fpath, "r", errors="ignore") as f:
                for line in f:
                    if not any(d in line for d in date_patterns):
                        continue
                    for word in keywords:
                        if word in line.lower():
                            key = f"{os.path.basename(fpath)}:{word}"
                            summary["event_counts"][key] = summary["event_counts"].get(key, 0) + 1
        except Exception as e:
            summary["event_counts"][f"error:{fpath}"] = str(e)

    return summary

def summarize_logs():
    """
    Chooses the best method available for summarizing logs.
    """
    if shutil.which("logwatch"):
        return run_logwatch_summary()
    else:
        return custom_log_summary()

def main():
    parser = argparse.ArgumentParser(description="Summarize important log activity.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = summarize_logs()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        elif "logwatch_summary" in result:
            print("📋 Logwatch Summary:")
            print(result["logwatch_summary"])
        else:
            print("🪵 Custom Log Summary:")
            print("Files Found:", ", ".join(result.get("found_files", [])))
            print("Event Counts:")
            for k, v in result.get("event_counts", {}).items():
                print(f" - {k}: {v}")

if __name__ == "__main__":
    main()