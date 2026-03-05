
output "azure_location" {
  description = "Azure location being used"
  value       = local.azure_location
}

output "azure_resource_group_name" {
  description = "Azure resource group name"
  value       = azurerm_resource_group.main.name
}

output "vnets" {
  description = "Virtual networks"
  value       = module.hub_spoke.vnets
}

output "subnets" {
  description = "All subnets keyed by vnet/subnet"
  value       = module.hub_spoke.subnets
}

output "vnet_ids" {
  description = "Map of VNet names to IDs"
  value       = module.hub_spoke.vnet_ids
}

output "subnet_ids" {
  description = "Map of subnet IDs keyed by vnet/subnet"
  value       = module.hub_spoke.subnet_ids
}

output "ubuntu_nva_firewall" {
  description = "Ubuntu NVA Firewall details"
  value = {
    nva_id     = module.ubuntu_nva_firewall.nva_id
    nva_name   = module.ubuntu_nva_firewall.nva_name
    private_ip = module.ubuntu_nva_firewall.nva_private_ip
    public_ip  = module.ubuntu_nva_firewall.nva_public_ip
    nva_nic_id = module.ubuntu_nva_firewall.nva_nic_id
  }
}

output "appgw" {
  description = "Application Gateway details"
  value = {
    appgw_id                     = module.appgw.appgw_id
    appgw_name                   = module.appgw.appgw_name
    public_ip                    = module.appgw.appgw_public_ip
    log_analytics_workspace_id   = module.appgw.log_analytics_workspace_id
    log_analytics_workspace_name = module.appgw.log_analytics_workspace_name
  }
}