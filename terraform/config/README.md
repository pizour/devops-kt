# Configuration Directory

This directory contains YAML configuration files for various Azure resources and modules.

## AKS and ACR Configuration

AKS and ACR configurations are now managed via YAML files:
- `aks.yaml` - AKS cluster configuration
- `acr.yaml` - ACR registry configuration

These files are automatically loaded into locals in `locals.tf` using `yamldecode()`.

### Editing Configuration

Edit the YAML files directly:
- `config/aks.yaml` - Update AKS settings
- `config/acr.yaml` - Update ACR settings
- `terraform.tfvars` - Override defaults if needed

### AKS Configuration (aks.yaml)

```yaml
aks_node_count: 2                    # Number of nodes (1-100)
aks_vm_size: "Standard_D2s_v3"       # Node VM size
kubernetes_version: null             # null = latest version
aks_enable_http_routing: false       # Enable HTTP routing
aks_enable_azure_policy: true        # Enable Azure Policy
```

### ACR Configuration (acr.yaml)

```yaml
aks_acr_name: ""                     # Empty = auto-generated
aks_acr_sku: "Basic"                 # Basic, Standard, or Premium
aks_acr_admin_enabled: false         # Enable admin account
```

### Override with terraform.tfvars

To override config file values, add them to `terraform.tfvars`:

```hcl
aks_node_count   = 3
aks_acr_sku      = "Standard"
```

## Other Configuration Files

- `vnets.yaml` - Virtual Network configuration
- `dns_zones.yaml` - Private DNS zones configuration
- `dns_resolver.yaml` - DNS resolver configuration
- `nsgs.yaml` - Network Security Groups configuration
- `nva_firewall.yaml` - Ubuntu NVA firewall configuration
- `policies.yaml` - Azure Policies configuration

All YAML files are loaded into locals in `locals.tf` and made available throughout the Terraform configuration.

