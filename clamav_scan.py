import subprocess
import argparse
import json
import shutil
import sys
import os

def run_clamav_scan(target_dir="/", scan_all=True):
    """
    Runs a ClamAV scan and returns detected threats and summary.
    """
    if not shutil.which("clamscan"):
        return {"error": "ClamAV is not installed or clamscan not found in PATH."}

    if not os.path.exists(target_dir):
        return {"error": f"Target directory does not exist: {target_dir}"}

    try:
        cmd = ["clamscan", "-r", target_dir, "--infected", "--no-summary"]
        if not scan_all:
            cmd.append("--bell")  # harmless extra flag just to allow logic branch

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        infected_files = []
        for line in result.stdout.strip().split("\n"):
            if ": " in line and "FOUND" in line:
                filepath, reason = line.rsplit(":", 1)
                infected_files.append(filepath.strip())

        summary = {
            "target": target_dir,
            "infected_count": len(infected_files),
            "infected_files": infected_files
        }
        return summary

    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Run ClamAV scan and list infected files.")
    parser.add_argument("--dir", type=str, default="/", help="Target directory to scan")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = run_clamav_scan(target_dir=args.dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        else:
            print(f"ClamAV Scan Summary for {result['target']}:")
            print(f" - Infected Files: {result['infected_count']}")
            for f in result['infected_files']:
                print(f"   ⚠️ {f}")

if __name__ == "__main__":
    main()