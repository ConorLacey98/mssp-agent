import requests
import datetime
import argparse
import json
import sys

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
DEFAULT_DAYS = 3  # Look back this many days

def fetch_recent_cves(days=DEFAULT_DAYS, keyword=None, max_results=25):
    """
    Fetches recent CVEs from the NVD API, optionally filtering by keyword.
    """
    try:
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=days)

        params = {
            "pubStartDate": start_date.isoformat() + "Z",
            "pubEndDate": end_date.isoformat() + "Z",
            "resultsPerPage": max_results,
        }

        if keyword:
            params["keywordSearch"] = keyword

        response = requests.get(NVD_API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        cves = []
        for item in data.get("vulnerabilities", []):
            cve_data = item.get("cve", {})
            cves.append({
                "id": cve_data.get("id"),
                "published": cve_data.get("published"),
                "summary": cve_data.get("descriptions", [{}])[0].get("value", "No description"),
                "severity": get_severity(cve_data)
            })

        return {"cves": cves}

    except Exception as e:
        return {"error": str(e)}

def get_severity(cve_data):
    """
    Extracts CVSS severity rating.
    """
    metrics = cve_data.get("metrics", {})
    cvss_data = metrics.get("cvssMetricV31") or metrics.get("cvssMetricV30") or []
    if not cvss_data:
        return "unknown"
    base_score = cvss_data[0].get("cvssData", {}).get("baseScore")
    severity = cvss_data[0].get("cvssData", {}).get("baseSeverity")
    return f"{severity} ({base_score})" if base_score else "unknown"

def main():
    parser = argparse.ArgumentParser(description="Fetch recent CVEs from NVD.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Number of days to look back")
    parser.add_argument("--keyword", type=str, help="Keyword to filter (e.g., openssh, apache)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = fetch_recent_cves(days=args.days, keyword=args.keyword)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print("Error:", result["error"], file=sys.stderr)
        else:
            print(f"Recent CVEs in last {args.days} days:")
            for cve in result["cves"]:
                print(f"- {cve['id']} ({cve['severity']})")
                print(f"  {cve['summary'][:100]}...")
                print(f"  Published: {cve['published']}")
                print()

if __name__ == "__main__":
    main()