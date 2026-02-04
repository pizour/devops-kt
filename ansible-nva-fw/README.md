# NVA Firewall Ansible Configuration

This Ansible project configures an Azure VM as a Network Virtual Appliance (NVA) firewall.

## Project Structure

```
ansible-nva-fw/
├── .ansible-lint                       # Ansible linting configuration
├── ansible.cfg                          # Ansible configuration
├── configure-nva-firewall.yml          # Main playbook
├── prod/                               # Production inventory
│   ├── inventory                       # Inventory file
│   ├── group_vars/
│   │   └── nva_firewalls.yml          # Group variables
│   └── host_vars/
│       └── nva-firewall-01.yml        # Host-specific variables
└── roles/                              # Ansible roles
    ├── prerequisites/                  # Install required packages
    │   ├── tasks/
    │   │   └── main.yml
    │   └── handlers/
    │       └── main.yml
    ├── ip_forwarding/                  # Configure IP forwarding
    │   ├── tasks/
    │   │   └── main.yml
    │   └── handlers/
    │       └── main.yml
    └── firewall/                       # Configure iptables firewall
        ├── tasks/
        │   └── main.yml
        ├── handlers/
        │   └── main.yml
        └── templates/
            └── rules.v4.j2             # Jinja2 template for iptables rules
```

## Functionality

The playbook performs the following tasks:

1. **Prerequisites Role**:
   - Updates apt cache
   - Installs `iptables-persistent` and `netfilter-persistent`
   - Enables netfilter-persistent service

2. **IP Forwarding Role**:
   - Enables IP forwarding in `/etc/sysctl.conf`
   - Applies sysctl settings
   - Verifies IP forwarding is enabled

3. **Firewall Role**:
   - Detects primary network interface
   - Generates iptables rules from Jinja2 template
   - Configures NAT rules (MASQUERADE for allowed networks)
   - Sets up FORWARD chain rules with optional port filtering
   - Optionally enables logging for dropped packets
   - Deploys rules to `/etc/iptables/rules.v4` with backup
   - Restores iptables rules and restarts netfilter-persistent service

## Configuration

### Before Running

1. **Update inventory file** (`prod/inventory`):
   - Replace `<VM_PUBLIC_IP_OR_HOSTNAME>` with your VM's actual IP or hostname
   - Update `ansible_user` if different from `azureuser`

2. **Adjust variables** if needed:
   - Group variables: `prod/group_vars/nva_firewalls.yml`
   - Host variables: `prod/host_vars/nva-firewall-01.yml`

### Key Variables

**Network Configuration:**
- `main_internal_network_cidr`: Primary internal network CIDR (default: `10.0.0.0/8`)
- `allowed_networks`: List of networks allowed to forward through firewall (default: `["10.0.0.0/8"]`)
- `firewall_default_interface`: Default network interface (default: `eth0`)

**Package Installation:**
- `required_packages`: List of packages to install (iptables-persistent, netfilter-persistent)

**IP Forwarding:**
- `ip_forward_enabled`: Enable IP forwarding (default: `true`)

**Firewall Features:**
- `allowed_forward_ports`: Optional list of specific ports to allow (empty = allow all)
  - Example: `[{ port: 80, protocol: tcp }, { port: 443, protocol: tcp }]`
- `enable_drop_logging`: Log dropped packets for debugging (default: `false`)

**Template Features:**
The firewall role uses a Jinja2 template (`rules.v4.j2`) that:
- Loops through `allowed_networks` to create dynamic NAT and FORWARD rules
- Conditionally creates port-specific rules if `allowed_forward_ports` is defined
- Conditionally adds logging rules if `enable_drop_logging` is enabled

## Usage

### Run the full playbook:

```bash
ansible-playbook configure-nva-firewall.yml
```

### Run specific roles using tags:

```bash
# Install packages only
ansible-playbook configure-nva-firewall.yml --tags prerequisites

# Configure IP forwarding only
ansible-playbook configure-nva-firewall.yml --tags ip_forwarding

# Configure firewall only
ansible-playbook configure-nva-firewall.yml --tags firewall
```

### Check mode (dry-run):

```bash
ansible-playbook configure-nva-firewall.yml --check
```

### Verbose output:

```bash
ansible-playbook configure-nva-firewall.yml -v
```

## Testing Connection

Before running the playbook, test connectivity:

```bash
ansible nva_firewalls -m ping
```

## Requirements

- Ansible 2.9 or higher
- SSH access to the target VM
- Sudo privileges on the target VM
- Ubuntu/Debian-based target system

## Advanced Configuration

### Adding Multiple Networks

Edit `prod/group_vars/nva_firewalls.yml`:

```yaml
allowed_networks:
  - "10.0.0.0/8"
  - "172.16.0.0/12"
  - "192.168.0.0/16"
```

### Restricting to Specific Ports

To only allow web traffic instead of all traffic:

```yaml
allowed_forward_ports:
  - { port: 80, protocol: tcp }
  - { port: 443, protocol: tcp }
```

### Enable Debug Logging

To troubleshoot connectivity issues:

```yaml
enable_drop_logging: true
```

Then check logs: `sudo tail -f /var/log/kern.log | grep iptables-dropped`

## Notes

- The playbook is idempotent and can be run multiple times safely
- All changes are logged and verified
- Firewall rules are persisted across reboots via iptables-persistent
- The configuration replicates init-script.sh functionality with added flexibility
- Uses Jinja2 templates for dynamic rule generation
- Creates backups of iptables rules before changes
- `DEBIAN_FRONTEND=noninteractive` prevents interactive prompts during package installation
- Uses `ansible.builtin.shell` module for iptables-restore to support shell redirection

## Troubleshooting

If you encounter issues:

1. Verify SSH connectivity: `ssh azureuser@<VM_IP>`
2. Check inventory file syntax: `ansible-inventory --list`
3. Run with verbose output: `ansible-playbook configure-nva-firewall.yml -vvv`
4. Verify variables: `ansible-inventory --host nva-firewall-01`
