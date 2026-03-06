#!/bin/bash
set -e

# Log all output
exec > >(tee -a /var/log/nva-init.log)
exec 2>&1

echo "Starting NVA firewall initialization at $(date)"

# Install iptables-persistent first
echo "Installing iptables-persistent..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y iptables-persistent netfilter-persistent

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Get the primary network interface (the one with the public IP)
PRIMARY_IFACE=$(ip route show default | awk '/default/ {print $5}' | head -n1)
if [ -z "$PRIMARY_IFACE" ]; then
    PRIMARY_IFACE="eth0"
fi

echo "Primary interface: $PRIMARY_IFACE"

# Get the private IP address of the primary interface
PRIVATE_IP=$(ip addr show $PRIMARY_IFACE | grep "inet " | awk '{print $2}' | cut -d/ -f1)
echo "Private IP: $PRIVATE_IP"

# Configure iptables for SNAT (Source NAT) for internal traffic
echo "Configuring iptables SNAT rules..."

# Flush existing NAT rules
iptables -t nat -F
iptables -t nat -X

# Enable SNAT for internal networks (10.0.0.0/8) going to internet via primary interface
iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -o $PRIMARY_IFACE -j MASQUERADE

# Allow forwarding for established/related connections
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT

# Allow forwarding from internal networks
iptables -A FORWARD -s 10.0.0.0/8 -j ACCEPT

# Save iptables rules
echo "Saving iptables rules..."
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4

# Ensure netfilter-persistent service is enabled and started
systemctl enable netfilter-persistent
systemctl restart netfilter-persistent

# Verify configuration
echo "Verification:"
echo "IP forwarding status:"
sysctl net.ipv4.ip_forward

echo "Current NAT rules:"
iptables -t nat -L -v -n

echo "Current FORWARD rules:"
iptables -L FORWARD -v -n

echo "NVA firewall initialization completed at $(date)"

# ============================================================
# Python API Services (api1 on port 5000, api2 on port 5001)
# ============================================================

echo "Installing Python and Flask for API services..."
apt-get install -y python3 python3-pip python3-venv

# Create application directory
mkdir -p /opt/apis
python3 -m venv /opt/apis/venv
/opt/apis/venv/bin/pip install flask

# ----- API1 (port 5000) -----
cat > /opt/apis/api1.py << 'PYEOF'
"""
API1 - Flask application running on port 5000
Serves / endpoints and /health for load balancer health checks.
"""
from flask import Flask, jsonify
import socket
import datetime

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "api1",
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

@app.route("/")
def root():
    return jsonify({
        "service": "api1",
        "message": "Welcome to API1",
        "hostname": socket.gethostname(),
        "endpoints": ["/", "/status", "/health"]
    }), 200

@app.route("/status")
def status():
    return jsonify({
        "service": "api1",
        "status": "running",
        "port": 5000,
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
PYEOF

# ----- API2 (port 5001) -----
cat > /opt/apis/api2.py << 'PYEOF'
"""
API2 - Flask application running on port 5001
Serves / endpoints and /health for load balancer health checks.
"""
from flask import Flask, jsonify
import socket
import datetime

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "api2",
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

@app.route("/")
def root():
    return jsonify({
        "service": "api2",
        "message": "Welcome to API2",
        "hostname": socket.gethostname(),
        "endpoints": ["/", "/status", "/health"]
    }), 200

@app.route("/status")
def status():
    return jsonify({
        "service": "api2",
        "status": "running",
        "port": 5001,
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
PYEOF

# ----- Systemd service for API1 -----
cat > /etc/systemd/system/api1.service << 'SVCEOF'
[Unit]
Description=API1 Flask Service (port 5000)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/apis
ExecStart=/opt/apis/venv/bin/python /opt/apis/api1.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
SVCEOF

# ----- Systemd service for API2 -----
cat > /etc/systemd/system/api2.service << 'SVCEOF'
[Unit]
Description=API2 Flask Service (port 5001)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/apis
ExecStart=/opt/apis/venv/bin/python /opt/apis/api2.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
SVCEOF

# Enable and start API services
systemctl daemon-reload
systemctl enable api1.service api2.service
systemctl start api1.service api2.service

echo "API services started: api1 (port 5000), api2 (port 5001)"
echo "API deployment completed at $(date)"
