import subprocess
import xml.etree.ElementTree as ET
import argparse
import json
import sys

def run_scan(target="127.0.0.1", ports="1-1024"):
    """
    Runs an nmap scan on the target and returns a list of open ports with services.
    """
    try:
        cmd = ["nmap", "-p", ports, "-oX", "-", target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"Nmap error: {result.stderr.strip()}")
        return parse_nmap_output(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def parse_nmap_output(xml_output):
    """
    Parses XML output from nmap and returns structured data.
    """
    ports = []
    try:
        root = ET.fromstring(xml_output)
        for host in root.findall("host"):
            for port in host.findall(".//port"):
                state = port.find("state").attrib.get("state")
                if state == "open":
                    portid = port.attrib.get("portid")
                    proto = port.attrib.get("protocol")
                    service_elem = port.find("service")
                    service_name = service_elem.attrib.get("name") if service_elem is not None else "unknown"
                    ports.append({
                        "port": portid,
                        "protocol": proto,
                        "service": service_name
                    })
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}
    return {"open_ports": ports}

def main():
    parser = argparse.ArgumentParser(description="Scan open ports using Nmap.")
    parser.add_argument("--target", type=str, default="127.0.0.1", help="Target IP or hostname")
    parser.add_argument("--ports", type=str, default="1-1024", help="Port range to scan (e.g., 22,80 or 1-65535)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    results = run_scan(args.target, args.ports)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if "error" in results:
            print("Error:", results["error"], file=sys.stderr)
        else:
            print(f"Open ports on {args.target}:")
            for port in results["open_ports"]:
                print(f" - {port['port']}/{port['protocol']}: {port['service']}")

if __name__ == "__main__":
    main()