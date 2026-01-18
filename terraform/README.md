# DevOps-KT Azure Infrastructure

This Terraform configuration deploys a production-ready Azure hub-spoke network topology with an Ubuntu-based Network Virtual Appliance (NVA) firewall and Azure Kubernetes Service (AKS).

## Architecture Overview

- **Hub-Spoke Topology**: Centralized hub network (10.0.0.0/16) with isolated spoke networks for AKS (10.1.0.0/16) and management VMs (10.2.0.0/16)
- **NVA Firewall**: Ubuntu-based firewall (10.0.0.10) with iptables SNAT for internet egress, IP forwarding enabled, and public IP for management
- **AKS Cluster**: Kubernetes cluster in dedicated spoke with full intra-cluster communication
- **Network Security**: NSG rules enforcing least-privilege access with intra-subnet and internal traffic allowed
- **Centralized Routing**: All spoke traffic routes through NVA firewall for inspection and control

## Project Structure

```
terraform/
├── main.tf                 # Main resource definitions and module calls
├── variables.tf            # Input variables (credentials only)
├── outputs.tf              # Output values (IPs, resource IDs)
├── locals.tf               # Local values and config loading
├── backend.tf              # Terraform state backend configuration
├── terraform.tfvars        # Sensitive values (credentials, passwords)
├── config/                 # YAML configuration files
│   ├── project.yaml        # Project settings and common tags
│   ├── vnets.yaml          # Virtual network and subnet definitions
│   ├── nsgs.yaml           # Network security group rules
│   ├── nva_firewall.yaml   # NVA firewall configuration
│   └── aks.yaml            # AKS cluster settings
└── modules/
    ├── hub_spoke/          # Hub-spoke networking with VNet peering
    ├── ubuntu_nva_firewall/# Ubuntu NVA firewall with iptables
    └── aks/                # Azure Kubernetes Service cluster
```

## Quick Start

### Prerequisites

- Azure subscription and service principal credentials
- Terraform >= 1.0
- Azure CLI (optional, for authentication)

### 1. Configure Credentials

Update `terraform.tfvars` with your Azure credentials:

```hcl
azure_subscription_id = "your-subscription-id"
azure_client_id       = "your-client-id"
azure_client_secret   = "your-client-secret"
azure_tenant_id       = "your-tenant-id"
nva_admin_password    = "your-secure-password"

# Add your public IP address(es) for SSH access to NVA firewall
allowed_ssh_ips = [
  "1.2.3.4",      # Your office IP
  "5.6.7.8"       # Your home IP (optional)
]
```

### 2. Customize Configuration

Edit YAML files in `config/` directory:

- **`config/project.yaml`**: Project name, location, environment, tags
- **`config/vnets.yaml`**: VNet address spaces and subnet definitions
- **`config/nsgs.yaml`**: Network security rules
- **`config/nva_firewall.yaml`**: NVA VM size, IP settings
- **`config/aks.yaml`**: AKS node count, VM size, Kubernetes version

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# View outputs
terraform output
```

## Configuration Files

### config/project.yaml
Project-wide settings and common resource tags.

```yaml
project_name: devops-kt
azure_location: westeurope
environment: dev
azure_resource_group_name: devops-kt-rg
common_tags:
  CreatedBy: Terraform
  Topology: HubSpoke
```

### config/vnets.yaml
Virtual network and subnet CIDR definitions.

- Hub VNet: 10.0.0.0/16 (firewall, bastion, shared services)
- Spoke1: 10.1.0.0/16 (AKS cluster)
- Spoke2: 10.2.0.0/16 (management VMs)

### config/nsgs.yaml
Network security group rules with consistent pattern:

- Priority 100: Intra-subnet traffic
- Priority 105: SSH from desktop (NVA only)
- Priority 110+: Service-specific rules
- Priority 4096: Default deny all inbound

### config/nva_firewall.yaml
Ubuntu NVA firewall configuration including VM size, IP address, and network settings.

### config/aks.yaml
AKS cluster configuration including node pool settings, Kubernetes version, and feature flags.

## Modules

### hub_spoke
Creates hub-spoke network topology with VNet peering, route tables, and NSGs. Implements centralized routing through NVA firewall with default routes pointing to 10.0.0.10.

[Module Documentation](modules/hub_spoke/README.md)

### ubuntu_nva_firewall
Deploys Ubuntu-based Network Virtual Appliance with:
- IP forwarding enabled
- iptables SNAT for internet egress (10.0.0.0/8 → Internet)
- Public IP for SSH management access
- Automated init script for firewall configuration

[Module Documentation](modules/ubuntu_nva_firewall/README.md)

### aks
Provisions Azure Kubernetes Service cluster in spoke network with system-assigned managed identity and network plugin integration.

[Module Documentation](modules/aks/README.md)

## State Management

Local state is used by default. For production environments, configure Azure Storage backend in `backend.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstate"
    container_name       = "tfstate"
    key                  = "devops-kt.tfstate"
  }
}
```

## Network Traffic Flow

### Spoke to Internet
1. Traffic originates in spoke subnet (AKS or VMs)
2. Default route (0.0.0.0/0) → NVA firewall (10.0.0.10)
3. NVA performs iptables SNAT
4. Traffic egresses via NVA public IP

### Firewall Subnet to Internet
1. Firewall subnet has dedicated default route (0.0.0.0/0) → Internet
2. Direct internet egress without NAT Gateway
3. Public IP attached to NVA primary interface

### Hub-to-Spoke
1. Direct VNet peering established between hub and each spoke
2. Internal routing (10.0.0.0/8) → VnetLocal for firewall subnet
3. Bidirectional traffic flow enabled

## Security Features

- **Network Segmentation**: Isolated spoke VNets with controlled hub connectivity
- **Centralized Firewalling**: All egress traffic inspected by NVA
- **NSG Protection**: Subnet-level security rules with least-privilege access
- **SSH Restrictions**: SSH access limited to configured IP addresses (via `allowed_ssh_ips` list in terraform.tfvars)
- **No Public IPs**: Spoke resources have no direct internet access
- **Secure Configuration**: Sensitive data (credentials, IPs) in terraform.tfvars, excluded from version control

## Outputs

The configuration exposes the following outputs:

- `azure_location`: Deployment region
- `azure_resource_group_name`: Resource group name
- `vnets`: Virtual network details
- `subnets`: All subnet information
- `ubuntu_nva_firewall`: NVA firewall details (IPs, IDs)

## Maintenance

### Update Allowed SSH IPs

To add or modify IP addresses allowed to SSH to NVA firewall:

```hcl
# Edit terraform.tfvars
allowed_ssh_ips = [
  "109.81.125.211",  # Existing office IP
  "198.51.100.42"    # New home/VPN IP
]

# Apply changes
terraform plan
terraform apply
```

NSG rules will be automatically updated with new IP addresses.

### Update NVA Firewall Rules

SSH to NVA using public IP and modify iptables rules:
```bash
ssh azureuser@<nva-public-ip>
sudo iptables -t nat -L -v -n  # View NAT rules
sudo iptables-save > /etc/iptables/rules.v4  # Persist changes
```

### Scale AKS Cluster
Update `config/aks.yaml`:
```yaml
aks_node_count: 3  # Increase node count
```
Then run `terraform apply`.

### Add Network Subnets
Edit `config/vnets.yaml` to add subnets, then update `config/nsgs.yaml` for security rules.

## Documentation

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Hub-Spoke Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Azure Kubernetes Service](https://learn.microsoft.com/en-us/azure/aks/)

## Troubleshooting

### Connection Issues
- Verify NSG rules allow required traffic
- Check route tables point to correct NVA IP (10.0.0.10)
- Ensure NVA firewall init script executed successfully

### AKS Issues
- Check subnet has sufficient IP space for node scaling
- Verify service CIDR (10.240.0.0/16) doesn't overlap with VNet ranges
- Review NSG rules allow AKS API server connectivity

### State Issues
- For local state conflicts, review `terraform.tfstate` file
- Consider migrating to remote state for team collaboration
