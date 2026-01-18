# Hub-Spoke Networking Module

Creates a production-ready hub-spoke network topology in Azure with VNet peering, centralized routing through NVA firewall, and Network Security Groups.

## Architecture Overview

This module implements a hub-spoke architecture enabling:
- **Hub Network**: Central network (10.0.0.0/16) containing shared services (NVA firewall, bastion)
- **Spoke Networks**: Isolated networks for workloads (AKS: 10.1.0.0/16, VMs: 10.2.0.0/16)
- **VNet Peering**: Direct connectivity between hub and spokes for internal communication
- **Centralized Routing**: All spoke egress traffic routes through NVA firewall (10.0.0.10) for inspection
- **Network Security**: NSG rules per subnet enforcing least-privilege access

## Key Features

- **No NAT Gateway**: Simplified architecture with NVA providing SNAT functionality
- **Direct Internet Access**: Firewall subnet has direct route to internet via public IP
- **Consistent NSG Pattern**: All subnets follow standardized security rule structure
- **Automatic Peering**: Hub-to-spoke VNet peering automatically configured
- **Flexible Subnet Design**: YAML-driven subnet and NSG configuration

## Resources Created

### Networking
- **Virtual Networks**: Hub VNet + multiple spoke VNets (configurable via YAML)
- **Subnets**: Segmented by function (firewall, bastion, shared services, AKS, management VMs)
- **VNet Peering**: Bidirectional hub-to-spoke peering with gateway transit disabled
- **Public IPs**: Reserved for NVA firewall management access

### Routing
- **Route Tables**: Per-subnet routing with conditional forwarding
  - **Spoke subnets**: Default route (0.0.0.0/0) → NVA firewall (10.0.0.10)
  - **Firewall subnet**: Internal route (10.0.0.0/8) → VnetLocal, default route → Internet
- **No Bastion routing**: AzureBastionSubnet excluded from custom route table assignments

### Security
- **Network Security Groups**: Per-subnet traffic rules
- **NSG Rule Pattern**:
  - Priority 100: Intra-subnet traffic (subnet → itself)
  - Priority 105: SSH from desktop IP (NVA only)
  - Priority 110-120: Service-specific rules (DNS, RDP, etc.)
  - Priority 4096: Default deny all inbound
- **Spoke Isolation**: Spokes communicate only through hub network

## Configuration

Network topology is defined via YAML configuration files in the `config/` directory:

### config/vnets.yaml
```yaml
hub-vnet:
  hub: true  # Identifies this as the hub network
  address_space:
    - 10.0.0.0/16
  subnets:
    hub-fw-snet: 10.0.0.0/24
    AzureBastionSubnet: 10.0.1.0/24
    hub-shared-snet: 10.0.3.0/24

spoke1-aks-vnet:
  address_space:
    - 10.1.0.0/16
  subnets:
    spoke1-aks-snet: 10.1.0.0/24

spoke2-mgmt-vnet:
  address_space:
    - 10.2.0.0/16
  subnets:
    spoke2-vms-snet: 10.2.0.0/24
```

### config/nsgs.yaml
```yaml
subnet_nsgs:
  hub-vnet/hub-fw-snet:
    nsg_name: devops-kt-hub-fw-snet-nsg
    rules:
      - name: AllowIntraSubnet
        priority: 100
        direction: Inbound
        access: Allow
        protocol: "*"
        source_port_range: "*"
        destination_port_range: "*"
        source_address_prefix: 10.0.0.0/25
        destination_address_prefix: "*"
      - name: AllowSSHFromDesktop
        priority: 105
        direction: Inbound
        access: Allow
        protocol: Tcp
        source_port_range: "*"
        destination_port_range: "22"
        source_address_prefix: ALLOWED_SSH_IPS  # Replaced with IPs from terraform.tfvars
        destination_address_prefix: "*"
```

**Note**: The `ALLOWED_SSH_IPS` placeholder is automatically replaced with actual IP addresses from the `allowed_ssh_ips` variable in terraform.tfvars during Terraform processing (see locals.tf).

## Usage

```hcl
module "hub_spoke" {
  source = "./modules/hub_spoke"

  project_name        = "devops-kt"
  location            = "westeurope"
  resource_group_name = "devops-kt-rg"
  nva_private_ip      = "10.0.0.10"
  
  vnets             = local.vnets
  subnet_nsgs       = local.subnet_nsgs
  default_nsg_rules = local.default_nsg_rules
  
  common_tags = {
    Environment = "dev"
    Project     = "devops-kt"
    Topology    = "HubSpoke"
  }
}
```

## Input Variables

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_name` | string | Yes | Project name for resource naming convention |
| `location` | string | Yes | Azure region (e.g., westeurope, eastus) |
| `resource_group_name` | string | Yes | Existing resource group name |
| `nva_private_ip` | string | Yes | Private IP for NVA firewall (typically 10.0.0.10) |
| `vnets` | map(object) | Yes | Virtual network definitions from vnets.yaml |
| `subnet_nsgs` | map(object) | Yes | NSG rule definitions from nsgs.yaml |
| `default_nsg_rules` | list(object) | Yes | Default NSG rules applied to all subnets |
| `common_tags` | map(string) | No | Common tags for all resources |

## Outputs

| Name | Description |
|------|-------------|
| `vnets` | Map of VNet objects with id and name |
| `vnet_ids` | Map of VNet IDs keyed by VNet name |
| `subnets` | Map of subnet objects keyed by "vnet/subnet" format |
| `subnet_ids` | Map of subnet IDs keyed by "vnet/subnet" format |
| `nsg_ids` | Map of Network Security Group IDs by subnet |
| `route_table_ids` | Map of route table IDs by subnet |

## Traffic Flow Patterns

### Spoke to Internet
1. Traffic originates in spoke subnet (e.g., AKS pod or management VM)
2. Subnet route table directs to NVA firewall (0.0.0.0/0 → 10.0.0.10)
3. NVA firewall performs iptables SNAT (source NAT)
4. Traffic egresses via NVA public IP address
5. Return traffic reverse-NAT'd back through firewall

### Firewall Subnet to Internet
1. Firewall subnet traffic destined for internet
2. Firewall route table has default route (0.0.0.0/0) → Internet
3. Direct egress via NVA public IP (no additional NAT)
4. Internal traffic (10.0.0.0/8) stays local via VnetLocal route

### Hub-to-Spoke Communication
1. Direct VNet peering between hub and each spoke
2. Traffic uses peering links (no firewall inspection for hub-spoke)
3. Internal route (10.0.0.0/8) → VnetLocal on firewall subnet
4. Bidirectional communication enabled

### Spoke-to-Spoke Communication
1. Source spoke → NVA firewall (via default route)
2. NVA inspects and forwards to destination spoke
3. Destination spoke sees traffic from firewall IP
4. Response traffic follows reverse path

## Network Layout

```
Hub VNet (10.0.0.0/16)
├── hub-fw-snet (10.0.0.0/24)         - NVA Firewall
├── AzureBastionSubnet (10.0.1.0/24)  - Azure Bastion (optional)
└── hub-shared-snet (10.0.3.0/24)     - Shared services

Spoke1 VNet (10.1.0.0/16) ─ Peered to Hub
└── spoke1-aks-snet (10.1.0.0/24)     - AKS cluster nodes

Spoke2 VNet (10.2.0.0/16) ─ Peered to Hub
└── spoke2-vms-snet (10.2.0.0/24)     - Management VMs
```

## Route Table Configuration

### Spoke Subnets
- **Default route**: 0.0.0.0/0 → Virtual Appliance (10.0.0.10)
- **Effect**: All internet-bound traffic inspected by firewall

### Firewall Subnet
- **Internal route**: 10.0.0.0/8 → VnetLocal (stay within VNet)
- **Default route**: 0.0.0.0/0 → Internet (direct egress)

### Bastion Subnet
- **No custom routes**: Azure Bastion requires default Azure routing

## Security Considerations

- **Least Privilege**: NSG rules deny by default, explicitly allow required traffic
- **Intra-Subnet Isolation**: Optional - can restrict by removing intra-subnet rules
- **Centralized Inspection**: All spoke egress traffic passes through NVA firewall
- **No Direct Internet**: Spoke resources cannot reach internet without firewall
- **Management Access**: SSH restricted to configured IP addresses (via `allowed_ssh_ips` in terraform.tfvars)

## Limitations

- **No Spoke-to-Spoke Peering**: Spokes cannot peer directly (must route through hub/firewall)
- **Single Hub**: Architecture supports one hub with multiple spokes only
- **Static Routes**: Route tables use static routes, not BGP or dynamic routing
- **No Azure Firewall**: Uses custom NVA instead of Azure Firewall service

## Troubleshooting

### Connectivity Issues
1. Verify route table associations: `az network vnet subnet show --ids <subnet-id>`
2. Check NSG rules allow traffic: `az network nsg rule list --nsg-name <nsg-name>`
3. Confirm NVA IP forwarding enabled: Check VM network interface settings
4. Test from NVA: SSH to firewall and test connectivity

### Peering Issues
1. Verify peering state is "Connected": `az network vnet peering list`
2. Check for overlapping address spaces between VNets
3. Ensure peering configured in both directions (hub-to-spoke and spoke-to-hub)

### Routing Problems
1. Use Azure Network Watcher "Next Hop" to trace routing
2. Verify effective routes on VM NIC
3. Check UDRs (User Defined Routes) take precedence over system routes

```
┌─────────────────────────────┐
│     Hub VNet (10.0.0.0/16)  │
├─────────────────────────────┤
│  ┌─ FW Subnet (10.0.0.0/24) │
│  │  ├─ NVA Firewall (10.0.0.10)
│  │  └─ NAT Gateway
│  │
│  ├─ Bastion (10.0.1.0/24)
│  │
│  ├─ DNS Inbound (10.0.2.0/24)
│  │
│  └─ DNS Outbound (10.0.3.0/24)
└─────────────────────────────┘
          ▲         ▲
          │ Peering │
     ┌────┴─────────┴────┐
     │                   │
┌────────────────┐  ┌────────────────┐
│ Spoke 1 AKS    │  │ Spoke 2 Mgmt   │
│ (10.1.0.0/16)  │  │ (10.2.0.0/16)  │
└────────────────┘  └────────────────┘
```

## Security Considerations

- **NSG Rules**: Restrict ingress to necessary ports/protocols
- **NVA Filtering**: All spoke traffic inspected by firewall
- **NAT Outbound**: Hide internal IPs behind NAT Gateway
- **VNet Isolation**: Spokes cannot communicate directly
- **Public IP**: Only bastion and NAT Gateway have public IPs
