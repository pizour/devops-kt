#!/bin/bash
set -e

# Log all output
exec > >(tee -a /var/log/nva-init.log)
exec 2>&1

# echo "Starting NVA firewall initialization at $(date)"

# # Install iptables-persistent first
# echo "Installing iptables-persistent..."
# export DEBIAN_FRONTEND=noninteractive
# apt-get update
# apt-get install -y iptables-persistent netfilter-persistent

# # Enable IP forwarding
# echo "Enabling IP forwarding..."
# echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
# sysctl -p

# # Get the primary network interface (the one with the public IP)
# PRIMARY_IFACE=$(ip route show default | awk '/default/ {print $5}' | head -n1)
# if [ -z "$PRIMARY_IFACE" ]; then
#     PRIMARY_IFACE="eth0"
# fi

# echo "Primary interface: $PRIMARY_IFACE"

# # Get the private IP address of the primary interface
# PRIVATE_IP=$(ip addr show $PRIMARY_IFACE | grep "inet " | awk '{print $2}' | cut -d/ -f1)
# echo "Private IP: $PRIVATE_IP"

# # Configure iptables for SNAT (Source NAT) for internal traffic
# echo "Configuring iptables SNAT rules..."

# # Flush existing NAT rules
# iptables -t nat -F
# iptables -t nat -X

# # Enable SNAT for internal networks (10.0.0.0/8) going to internet via primary interface
# iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -o $PRIMARY_IFACE -j MASQUERADE

# # Allow forwarding for established/related connections
# iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT

# # Allow forwarding from internal networks
# iptables -A FORWARD -s 10.0.0.0/8 -j ACCEPT

# # Save iptables rules
# echo "Saving iptables rules..."
# mkdir -p /etc/iptables
# iptables-save > /etc/iptables/rules.v4

# # Ensure netfilter-persistent service is enabled and started
# systemctl enable netfilter-persistent
# systemctl restart netfilter-persistent

# # Verify configuration
# echo "Verification:"
# echo "IP forwarding status:"
# sysctl net.ipv4.ip_forward

# echo "Current NAT rules:"
# iptables -t nat -L -v -n

# echo "Current FORWARD rules:"
# iptables -L FORWARD -v -n

# echo "NVA firewall initialization completed at $(date)"
