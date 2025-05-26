#!/bin/bash

# install.sh – Linux-only setup script for MSSP agent
# Usage: sudo ./install.sh

AGENT_DIR="/opt/mssp-agent"
CRON_FILE="/etc/cron.d/mssp-agent"
PY_SCRIPTS=("check_ssh_logins.py" "check_open_ports.py" "check_patch_status.py" "run_lynis.py" "log_summary.py" "check_vuln_feeds.py" "clamav_scan.py")

echo "[*] Creating agent directory: $AGENT_DIR"
mkdir -p "$AGENT_DIR"

echo "[*] Copying scripts to agent directory..."
for script in "${PY_SCRIPTS[@]}"; do
    cp "$script" "$AGENT_DIR/"
done

echo "[*] Writing configuration (edit if needed)..."
cat > "$AGENT_DIR/config.json" <<EOF
{
  "api_url": "https://server.com/api/report/",
  "token": "REPLACE_WITH_YOUR_CLIENT_TOKEN"
}
EOF

echo "[*] Creating cron job (runs every 6 hours)..."
echo "0 */6 * * * root python3 $AGENT_DIR/check_ssh_logins.py --json | curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Token REPLACE_WITH_CLIENT_TOKEN' -d @- https://server.com/api/report/" > "$CRON_FILE"
chmod 644 "$CRON_FILE"

echo "[✓] Agent installed. Edit config.json or cron timing as needed."