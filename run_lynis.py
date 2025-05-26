import subprocess
import os
import json
import argparse
import sys

LYNIS_REPORT_FILE = "/var/log/lynis-report.dat"

def run_lynis_scan():
    """
    Runs Lynis audit scan and parses results from the report file.
    Returns summary data or error.
    """
    if not shutil.which("lynis"):
        return {"error": "Lynis is not installed or not in PATH."}

    try:
        # Run Lynis with minimal output, assuming root access
        subprocess.run(["lynis", "audit", "system", "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists(LYNIS_REPORT_FILE):
            return {"error": f"Lynis report not found at {LYNIS_REPORT_FILE}"}

        return parse_lynis_report(LYNIS_REPORT_FILE)

    except Exception as e:
        return {"error": str(e)}

def parse_lynis_report(filepath):
    """
    Parses lynis-report.dat and extracts key metrics and findings.
    """
    results = {
        "warnings": [],
        "suggestions": [],
        "hardening_index": None,
        "tests_performed": None
    }

    try:
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("warning[]="):
                    results["warnings"].append(line.strip().split("=", 1)[1])
                elif line.startswith("suggestion[]="):
                    results["suggestions"].append(line.strip().split("=", 1)[1])
                elif line.startswith("hardening_index="):
                    results["hardening_index"] = line.strip().split("=")[1]
                elif line.startswith("tests_performed="):
                    results["tests_performed"] = line.strip().split("=")[1]
    except Exception as e:
        return {"error": f"Failed to parse report: {e}"}

    return results

def main():
    parser = argparse.ArgumentParser(description="Run Lynis system audit and extract results.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = run_lynis_scan()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        else:
            print(f"Hardening Index: {result['hardening_index']}")
            print(f"Tests Performed: {result['tests_performed']}")
            print("\nWarnings:")
            for w in result["warnings"]:
                print(f" - {w}")
            print("\nSuggestions:")
            for s in result["suggestions"]:
                print(f" - {s}")

if __name__ == "__main__":
    import shutil
    main()