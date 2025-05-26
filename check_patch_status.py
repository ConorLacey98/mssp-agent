import subprocess
import platform
import shutil
import argparse
import json
import sys

def detect_package_manager():
    """
    Detects which package manager is available.
    Returns 'apt', 'dnf', or 'yum', or None if unsupported.
    """
    if shutil.which("apt"):
        return "apt"
    elif shutil.which("dnf"):
        return "dnf"
    elif shutil.which("yum"):
        return "yum"
    return None

def check_apt_updates():
    """
    Returns a list of available package updates on APT-based systems.
    """
    try:
        subprocess.run(["apt", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        updates = []
        for line in lines:
            parts = line.split("/")
            if parts:
                pkg = parts[0]
                updates.append(pkg)
        return {"package_manager": "apt", "updates": updates, "count": len(updates)}
    except Exception as e:
        return {"error": str(e)}

def check_dnf_or_yum_updates(cmd):
    """
    Checks updates using dnf or yum and returns a list of packages.
    """
    try:
        result = subprocess.run([cmd, "check-update"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        updates = []
        for line in lines:
            if line and not line.startswith("Last metadata expiration"):
                parts = line.split()
                if len(parts) >= 2 and not line.startswith("Obsoleting"):
                    updates.append(parts[0])
        return {"package_manager": cmd, "updates": updates, "count": len(updates)}
    except subprocess.CalledProcessError as e:
        # check-update returns 100 if updates are available, but still successful
        lines = e.stdout.strip().split("\n")
        updates = []
        for line in lines:
            if line and not line.startswith("Last metadata expiration"):
                parts = line.split()
                if len(parts) >= 2 and not line.startswith("Obsoleting"):
                    updates.append(parts[0])
        return {"package_manager": cmd, "updates": updates, "count": len(updates)}
    except Exception as e:
        return {"error": str(e)}

def check_patch_status():
    """
    Detects OS type and runs appropriate update check.
    """
    pm = detect_package_manager()
    if pm == "apt":
        return check_apt_updates()
    elif pm in ["dnf", "yum"]:
        return check_dnf_or_yum_updates(pm)
    else:
        return {"error": "Unsupported package manager or OS"}

def main():
    parser = argparse.ArgumentParser(description="Check available OS package updates.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = check_patch_status()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        else:
            print(f"Package Manager: {result['package_manager']}")
            print(f"Available Updates ({result['count']}):")
            for pkg in result["updates"]:
                print(f" - {pkg}")

if __name__ == "__main__":
    main()