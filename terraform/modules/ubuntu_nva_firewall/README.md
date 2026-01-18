# Ubuntu NVA Firewall Module

Creates an Ubuntu-based Network Virtual Appliance (NVA) firewall with public IP for centralized routing, NAT, and traffic inspection in a hub-spoke architecture.

## Overview

This module provisions a single-NIC Linux VM configured as the network gateway and firewall:
- **IP Forwarding** enabled for routing traffic between spoke networks and internet
- **iptables SNAT** for network address translation (masquerading internal networks)
- **Public IP** for SSH management and internet egress
- **Automated Configuration** via init script (iptables-persistent, routing rules)
- **Static Private IP** (10.0.0.10) serving as default gateway for all spoke subnets

## Architecture

```
                          Internet
                             ↑↓
                      [Public IP: NVA]
                             │
┌─────────────────────────────────────────────────────┐
│  Hub VNet (10.0.0.0/16)                             │
│  ┌───────────────────────────────────────────────┐  │
│  │  Firewall Subnet (10.0.0.0/24)               │  │
│  │  ┌─────────────────────────────────────────┐ │  │
│  │  │ Ubuntu NVA Firewall                     │ │  │
│  │  │ - Private IP: 10.0.0.10 (static)        │ │  │
│  │  │ - Public IP: Attached for SSH + NAT     │ │  │
│  │  │ - IP Forwarding: Enabled                │ │  │
│  │  │ - iptables SNAT: 10.0.0.0/8 → Internet  │ │  │
│  │  │ - Init Script: Auto-configures firewall │ │  │
│  │  │ - NSG: SSH from allowed IPs only        │ │  │
│  │  └─────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ Default Gateway (10.0.0.10)
        ┌──────────────┴──────────────┐
        ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  Spoke 1 VNet    │          │  Spoke 2 VNet    │
│  (10.1.0.0/16)   │          │  (10.2.0.0/16)   │
│  - AKS Cluster   │          │  - Management VMs│
│  0.0.0.0/0 → NVA │          │  0.0.0.0/0 → NVA │
└──────────────────┘          └──────────────────┘
```

## Resources Created

### Compute Resources
- **Virtual Machine**: Ubuntu 22.04 LTS configured as router/firewall
- **Network Interface**: Single NIC with static IP (10.0.0.10)
- **Public IP**: Attached to NIC for management SSH and internet egress
- **OS Disk**: Managed disk (Premium or Standard based on VM size)

### Network Resources
- **Public IP Address**: Standard SKU with static allocation
- **Network Interface**: Configured with:
  - Static private IP: 10.0.0.10
  - IP forwarding enabled
  - Public IP association
  - Optional accelerated networking

### Security Resources
- **Network Security Group**: Traffic rules including:
  - Priority 100: Intra-subnet traffic
  - Priority 105: SSH from configured IP addresses (via `allowed_ssh_ips` in terraform.tfvars)
  - Priority 4096: Default deny all inbound
- **SSH Authentication**: Password-based (configurable via terraform.tfvars)
- **Init Script**: Automated firewall configuration on first boot

## Key Features

- **Single-NIC Design**: Simplified architecture - no separate NAT Gateway needed
- **Ubuntu 22.04 LTS**: Long-term support with security updates
- **IP Forwarding**: Kernel-level routing between networks
- **iptables SNAT**: Automatic source NAT for 10.0.0.0/8 → Internet
- **Public IP Direct Attach**: SSH management and internet egress via same IP
- **Automated Init Script**: 
  - Installs iptables-persistent
  - Enables IP forwarding (sysctl)
  - Configures SNAT rules
  - Persists configuration across reboots
- **Restricted SSH**: Access limited to configured IP addresses (via `allowed_ssh_ips` in terraform.tfvars)
- **Default Gateway Role**: All spoke traffic uses 10.0.0.10 as next hop

## Usage

```hcl
module "ubuntu_nva_firewall" {
  source = "./modules/ubuntu_nva_firewall"

  project_name           = local.project_name
  location               = local.azure_location
  resource_group_name    = local.azure_resource_group_name
  firewall_subnet_id     = module.hub_spoke.subnet_ids["hub-vnet/hub-fw-snet"]
  
  # NVA Configuration from YAML
  nva_name               = local.nva_firewall.nva_name
  private_ip_address     = local.nva_firewall.private_ip_address
  vm_size                = local.nva_firewall.vm_size
  admin_password         = var.nva_admin_password
  
  # Networking Features
  enable_public_ip                = local.nva_firewall.enable_public_ip          # true
  enable_ip_forwarding            = local.nva_firewall.enable_ip_forwarding      # true
  enable_accelerated_networking   = local.nva_firewall.enable_accelerated_networking
  
  # Automated Initialization
  init_script_path      = "${path.module}/modules/ubuntu_nva_firewall/init-script.sh"
  
  common_tags = local.common_tags
}
```

### Configuration Files

**config/nva_firewall.yaml**:
```yaml
nva_firewall:
  enabled: true
  nva_name: fw
  private_ip_address: "10.0.0.10"
  vm_size: "Standard_D2s_v3"
  enable_public_ip: true
  enable_ip_forwarding: true
  enable_accelerated_networking: false
```

**terraform.tfvars**:
```hcl
nva_admin_password = "P@ssw0rd123!Change#Me"
```

**NSG Rules** (configured in `config/nsgs.yaml`):
```yaml
subnet_nsgs:
  hub-vnet/hub-fw-snet:
    nsg_name: devops-kt-hub-fw-snet-nsg
    rules:
      - name: AllowIntraSubnet
        priority: 100
        direction: Inbound
        protocol: "*"
        # ... intra-subnet traffic
      - name: AllowSSHFromDesktop
        priority: 105
        direction: Inbound
        protocol: Tcp
        destination_port_range: "22"
        source_address_prefix: ALLOWED_SSH_IPS  # Replaced with IPs from terraform.tfvars
```

**Note**: The `ALLOWED_SSH_IPS` placeholder is automatically replaced with actual IP addresses from `allowed_ssh_ips` variable in terraform.tfvars during Terraform processing.

## Input Variables

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_name` | string | Yes | Project name for resource naming convention |
| `location` | string | Yes | Azure region (e.g., westeurope) |
| `resource_group_name` | string | Yes | Resource group name (must exist) |
| `firewall_subnet_id` | string | Yes | Firewall subnet resource ID from hub VNet |
| `nva_name` | string | Yes | Name for NVA firewall VM (e.g., "fw") |
| `private_ip_address` | string | Yes | Static private IP address (typically 10.0.0.10) |
| `vm_size` | string | Yes | Azure VM size (e.g., Standard_D2s_v3) |
| `admin_password` | string | Yes | Admin password for VM login (from terraform.tfvars) |
| `enable_public_ip` | bool | No | Attach public IP for SSH management + NAT (default: true) |
| `enable_ip_forwarding` | bool | No | Enable IP forwarding on NIC (default: true) |
| `enable_accelerated_networking` | bool | No | Enable SR-IOV for high performance (default: false) |
| `init_script_path` | string | No | Path to init script for automated configuration |
| `common_tags` | map(string) | No | Common tags applied to all resources |

## Outputs

| Name | Description |
|------|-------------|
| `nva_id` | Virtual machine resource ID |
| `nva_name` | Virtual machine name (e.g., devops-kt-fw) |
| `nva_private_ip` | Private IP address (10.0.0.10) |
| `nva_public_ip_id` | Public IP resource ID |
| `nva_public_ip_address` | Public IP address for SSH management |
| `nva_nic_id` | Network interface resource ID |

## IP Forwarding Configuration

### Linux Kernel Level
```Automated Configuration (Init Script)

The NVA firewall is automatically configured on first boot via **init-script.sh**:

### What the Init Script Does

1. **Installs iptables-persistent**: Ensures firewall rules persist across reboots
2. **Enables IP Forwarding**: Sets `net.ipv4.ip_forward=1` via sysctl
3. **Configures iptables SNAT**: Masquerades traffic from 10.0.0.0/8 to internet
4. **Allows Forwarding**: Permits established/related connections
5. **Persists Rules**: Saves to `/etc/iptables/rules.v4`

### Init Script Contents

```bash
#!/bin/bash
# init-script.sh - NVA Firewall Automated Configuration

# Install iptables-persistent (non-interactive)
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y iptables-persistent

# Enable IP forwarding (kernel level)
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Configure iptables SNAT for internet egress
iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -j MASQUERADE

# Allow forwarding for established connections
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0 -o eth0 -j ACCEPT

# Save rules persistently
iptables-save > /etc/iptables/rules.v4
```

### Verify Configuration (After Deployment)

```bash
# SSNSG Rules (Applied to Firewall Subnet)

**Inbound Rules**:
- **Priority 100**: AllowIntraSubnet - Traffic within 10.0.0.0/25 subnet
- **Priority 105**: AllowSSHFromDesktop - SSH (port 22) from configured IP addresses (via `allowed_ssh_ips`)
- **Priority 4096**: DenyAllInbound - Default deny all other inbound

**Outbound Rules**:
- All outbound traffic allowed (for internet egress, updates, etc.)

### iptables Rules (Configured by Init Script)

**NAT Table**:
- **POSTROUTING**: MASQUERADE for 10.0.0.0/8 → Provides SNAT for internal networks

**Filter Table (FORWARD chain)**:
- **ACCEPT**: Related/established connections (return traffic)
- **ACCEPT**: Traffic between eth0 interfaces (forwarding)
SSH via Public IP (Primary Method)

```bash
# Get NVA public IP from Terraform outputs
terraform output ubuntu_nva_firewall

# SSH to NVA firewall (from allowed IP addresses only)
ssh azureuser@<nva-public-ip>
# Enter password from terraform.tfvars

# Verify firewall is functioning
ping 8.8.8.8                    # Should reach internet
ip addr show eth0               # Should show 10.0.0.10
sudo iptables -t nat -L -n -v   # View NAT rules
```

### Alternative: Azure Portal Serial Console

- Navigate to: Portal → VM → Support + Troubleshooting → Serial console
- Use for emergency access if SSH is unavailable
- Requires VM to be running

### Alternative: Azure Bastion (If Deployed)

```bash to Internet (Primary Use Case)

```
AKS Pod (10.1.0.50) → Internet
  ↓ Destination: 8.8.8.8
Route Table: 0.0.0.0/0 → 10.0.0.10 (Virtual Appliance)
  ↓
NVA Firewall (10.0.0.10)
  [iptables SNAT: 10.1.0.50 → NVA Public IP]
  ↓
Internet (8.8.8.8)
  [Sees traffic from NVA Public IP]
```

### Example 2: Spoke-to-Spoke Communication

```
Spoke1 VM (10.1.0.100) → Spoke2 VM (10.2.0.100)
  ↓ Destination: 10.2.0.100
Route Table: 0.0.0.0/0 → 10.0.0.10 (catches all non-VNet traffic)
  ↓
NVA Firewall (10.0.0.10)
  [IP forwarding - no NAT for private traffic]
  ↓
Spoke2 VM (10.2.0.100)
  [Sees source IP: 10.1.0.100]
```

### Example 3: SSH Management Access

```
Allowed IP (e.g., 109.81.125.211) → NVA Firewall
  ↓ SSH to NVA Public IP
NSG Rule (Priority 105): Allow SSH from allowed_ssh_ips list
  ↓
NVA Firewall (10.0.0.10)
  [SSH service on port 22]
  ↓
Admin Shell Access
```

### Example 4: Firewall Subnet to Internet

```

```bash
# Check VM power state and status
az vm get-instance-view -d --resource-group devops-kt-rg \
  --name devops-kt-fw --query "instanceView.statuses"

# Get NVA details including public IP
terraform output ubuntu_nva_firewall

# Test connectivity from spoke subnet
# From a VM in spoke network:
ping 10.0.0.10              # Should reach NVA
traceroute 8.8.8.8          # Should show 10.0.0.10 as first hop
```

### Verify Firewall Configuration

```bash
# SSH to NVA
ssh azureuser@<nva-public-ip>

# Check IP forwarding is enabled
sysctl net.ipv4.ip_forward
# Expected: net.ipv4.ip_forward = 1

# View NAT rules
sudo iptables -t nat -L -n -v
# Should show MASQUERADE for 10.0.0.0/8

# View forwarding rules
sudo iptables -L FORWARD -n -v
# Should show ACCEPT for related/established

# Check routing
ip route show
# Should have default route

# Test internet connectivity from NVA
ping 8.8.8.8
curl -I https://www.google.com
```

### Monitor Traffic

```bash
# Real-time connection tracking
sudo watch -n 2 'conntrack -L | wc -l'

# View active NAT connections
sudo conntrack -L -n

# Monitor network interfaces
ifconfig eth0
ip -s link show eth0

# Check for dropped packets
netstat -i
```

### NSG Flow Logs

- Enable in Azure Network Watcher
- View traffic patterns in Log Analytics
- Analyze allowed/denied connections
- Useful for security auditing

## Performance Tuning

### VM Size Considerations

| VM Size | vCPUs | RAM | Network Bandwidth | Use Case |
|---------|-------|-----|-------------------|----------|
| Standard_D2s_v3 | 2 | 8 GB | Moderate | Current deployment |
| Standard_D4s_v3 | 4 | 16 GB | High | Heavy traffic workloads |
| Standard_D8s_v3 | 8 | 32 GB | Very High | Enterprise deployments |

### Enable Accelerated Networking

For high-throughput scenarios:
```yaml
# config/nva_firewall.yaml
enable_accelerated_networking: true
```

Benefits:
- Lower latency
- Reduced jitter
- Decreased CPU utilization
- Up to 30 Gbps network throughput

### Connection Tracking Tuning

```bash
# Increase conntrack table size (if needed)
echo "net.netfilter.nf_conntrack_max = 131072" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Common Issues & Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **No internet from spokes** | Timeouts, DNS failures | 1. Verify route table: 0.0.0.0/0 → 10.0.0.10<br>2. Check IP forwarding: `sysctl net.ipv4.ip_forward`<br>3. Verify iptables SNAT rule exists |
| **SSH access denied** | Connection refused/timeout | 1. Verify NSG allows SSH from your IP<br>2. Check your IP is in `allowed_ssh_ips` list (terraform.tfvars)<br>3. Confirm VM is running |
| **High latency** | Slow connections | 1. Check VM CPU/memory usage<br>2. Enable accelerated networking<br>3. Consider larger VM size |
| **Packets dropped** | Intermittent connectivity | 1. Check `netstat -i` for drops<br>2. Review iptables FORWARD chain<br>3. Check conntrack table full |
| **Init script didn't run** | No iptables rules | 1. Check cloud-init logs: `/var/log/cloud-init-output.log`<br>2. Manually run init script<br>3. Redeploy VM |

## Cost Optimization

**Current Configuration**:
- VM: Standard_D2s_v3 (2 vCPUs, 8 GB RAM)
- Disk: Managed disk (30 GB)
- Public IP: Standard SKU, static
- **Estimated**: ~$80-100/month (region-dependent)

**Cost Reduction Options**:
1. **Smaller VM**: Standard_B2s (~$30/month) - suitable for dev/test
2. **Reserved Instances**: 1-year or 3-year commitment for 40-60% savings
3. **Auto-shutdown**: Schedule VM shutdown during non-business hours

**Important**: Do not reduce VM size below current specs for production workloads

## Security Hardening

### Post-Deployment Actions

1. **Change Default Password**:
```bash
ssh azureuser@<nva-public-ip>
passwd
```

2. **Disable Password Auth (Use SSH Keys)**:
```bash
# Generate SSH key pair (on local machine)
ssh-keygen -t rsa -b 4096 -C "nva-firewall"

# Add public key to VM
ssh azureuser@<nva-public-ip>
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Disable password authentication
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

3. **Enable Automatic Updates**:
```bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

4. **Install Fail2Ban** (SSH brute-force protection):
```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Backup and Disaster Recovery

### Backup Strategy

1. **Azure Backup** (VM level):
```bash
# Enable via Azure Portal
VM → Backup → Enable backup
```

2. **Configuration Backup** (iptables rules):
```bash
# SSH to NVA and save rules
sudo iptables-save > ~/iptables-backup-$(date +%Y%m%d).rules
```

### Disaster Recovery

**Recovery Steps** (if NVA fails):
1. Deploy new NVA VM using Terraform
2. Init script will auto-configure firewall
3. Verify routing and connectivity
4. Update DNS/documentation if public IP changed

## Related Resources

- [Azure NVA Documentation](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/nva-ha)
- [IP Forwarding in Azure](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface#enable-or-disable-ip-forwarding)
- [iptables Tutorial](https://www.frozentux.net/iptables-tutorial/iptables-tutorial.html)
- [iptables-persistent](https://packages.ubuntu.com/jammy/iptables-persistent)
- [Azure VM Sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes
Internet
```

## Monitoring & Troubleshooting

### Check NVA Status
```bash
# From Bastion/admin machine
az vm get-instance-view -d --resource-group devops-kt-rg \
  --name <nva-name> --query "instanceView.statuses"

# Check connectivity from spoke
ping 10.0.0.10
```

### View Firewall Rules
```bash
# SSH to NVA
ssh -i ~/.ssh/id_rsa azureuser@<nva-ip>

# Check UFW status
sudo ufw status verbose

# View IP forwarding
cat /proc/sys/net/ipv4/ip_forward
```

### Monitor with NSG Flow Logs
- Enabled automatically on NVA NSG
- View in Network Watcher
- Traffic patterns visible within minutes

## Cost Optimization

| Resource | Size Impact | Notes |
|----------|-------------|-------|
| VM | Standard_B2s | Sufficient for <10Gbps traffic |
| Disk | Premium vs Standard | Premium for higher throughput |
| Public IP | Standard | Only if management access needed |
| Load Balancer | Standard | For HA deployments |

## Common Issues

| Issue | Solution |
|-------|----------|
| VNet routing not working | Check route table entries, NVA IP |
| SSH timeout | Verify NSG rule allows source IP |
| Packets not forwarded | Check `sysctl net.ipv4.ip_forward` |
| High latency | Check VM size, enable accelerated networking |
| Packet loss | Monitor NSG flow logs, check NVA CPU |

## Related Resources

- [NVA Documentation](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/nva-ha)
- [IP Forwarding Guide](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface#enable-or-disable-ip-forwarding)
- [iptables Reference](https://linux.die.net/man/8/iptables)
- [ufw Manual](https://manpages.ubuntu.com/manpages/jammy/man8/ufw.8.html)
