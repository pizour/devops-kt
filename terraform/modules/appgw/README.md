# Application Gateway Module

This module deploys an Azure Application Gateway with WAF (OWASP) and Log Analytics integration.

## Features

- **Application Gateway WAF v2** with public IP
- **HTTP listener** on port 80 (no TLS)
- **Path-based routing**: `/api1/*` → backend port 5000, `/api2/*` → backend port 5001
- **Backend pool** targeting the NVA firewall VM
- **Health probes** on `/health` for each backend (HTTP)
- **WAF** with OWASP 3.2 rule set in Prevention mode
- **Log Analytics Workspace** with diagnostic settings for:
  - Application Gateway Access Logs
  - Application Gateway Performance Logs
  - Application Gateway Firewall (WAF) Logs
  - All Metrics

## Usage

```hcl
module "appgw" {
  source = "./modules/appgw"

  appgw_name          = "my-appgw"
  location            = "westeurope"
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = module.hub_spoke.subnet_ids["hub-vnet/hub-agw-snet"]
  backend_ip_address  = module.ubuntu_nva_firewall.nva_private_ip

  common_tags = local.common_tags
}
```

## Configuration

All settings are configurable via `config/appgw.yaml`. See variables.tf for full list of inputs.
