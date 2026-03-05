# Resource Group
resource "azurerm_resource_group" "main" {
  name     = local.azure_resource_group_name
  location = local.azure_location

  tags = local.common_tags
}

# Hub-Spoke Networking Module
module "hub_spoke" {
  source = "./modules/hub_spoke"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  common_tags         = local.common_tags

  vnets             = local.vnets
  nva_private_ip    = local.nva_private_ip
  subnet_nsgs       = local.subnet_nsgs
  default_nsg_rules = local.default_nsg_rules
}

# Ubuntu NVA Firewall Module
module "ubuntu_nva_firewall" {
  source = "./modules/ubuntu_nva_firewall"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  nva_name            = local.nva_firewall.nva_name
  firewall_subnet_id  = module.hub_spoke.subnet_ids["hub-vnet/hub-fw-snet"]
  private_ip_address  = local.nva_firewall.private_ip_address

  vm_size                       = local.nva_firewall.vm_size
  enable_public_ip              = local.nva_firewall.enable_public_ip
  enable_ip_forwarding          = local.nva_firewall.enable_ip_forwarding
  enable_accelerated_networking = local.nva_firewall.enable_accelerated_networking

  admin_username = "azureuser"
  admin_password = var.nva_admin_password

  common_tags = local.common_tags

  depends_on = [
    azurerm_resource_group.main,
    module.hub_spoke
  ]
}

# # AKS Module
# module "aks" {
#   source = "./modules/aks"
#
#   cluster_name        = "${local.azure_resource_group_name}-aks"
#   dns_prefix          = replace(local.azure_resource_group_name, "-", "")
#   location            = local.azure_location
#   resource_group_name = azurerm_resource_group.main.name
#   resource_group_id   = azurerm_resource_group.main.id
#
#   subnet_id = module.hub_spoke.subnet_ids["spoke1-aks-vnet/spoke1-aks-snet"]
#
#   default_node_pool_name = "agentpool"
#   node_count             = local.aks.aks_node_count
#   vm_size                = local.aks.aks_vm_size
#   kubernetes_version     = local.aks.kubernetes_version
#
#   service_cidr   = "10.240.0.0/16"
#   dns_service_ip = "10.240.0.10"
#
#   enable_http_application_routing = local.aks.aks_enable_http_routing
#   enable_azure_policy             = local.aks.aks_enable_azure_policy
#
#   common_tags = local.common_tags
#
#   depends_on = [
#     azurerm_resource_group.main,
#     module.hub_spoke
#   ]
# }

# Application Gateway Module
module "appgw" {
  source = "./modules/appgw"

  appgw_name          = "${local.azure_resource_group_name}-agw"
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name

  subnet_id          = module.hub_spoke.subnet_ids["hub-vnet/hub-agw-snet"]
  backend_ip_address = module.ubuntu_nva_firewall.nva_private_ip

  sku_name = local.appgw.sku_name
  sku_tier = local.appgw.sku_tier
  capacity = local.appgw.capacity

  waf_enabled          = local.appgw.waf.enabled
  waf_firewall_mode    = local.appgw.waf.firewall_mode
  waf_rule_set_type    = local.appgw.waf.rule_set_type
  waf_rule_set_version = local.appgw.waf.rule_set_version

  frontend_port = local.appgw.frontend_port

  backend_api1_port       = local.appgw.backend.api1.port
  backend_api2_port       = local.appgw.backend.api2.port
  backend_request_timeout = local.appgw.backend.api1.request_timeout

  health_probe_path                = local.appgw.health_probe.path
  health_probe_interval            = local.appgw.health_probe.interval
  health_probe_timeout             = local.appgw.health_probe.timeout
  health_probe_unhealthy_threshold = local.appgw.health_probe.unhealthy_threshold

  log_analytics_sku            = local.appgw.log_analytics.sku
  log_analytics_retention_days = local.appgw.log_analytics.retention_in_days

  common_tags = local.common_tags

  depends_on = [
    azurerm_resource_group.main,
    module.hub_spoke,
    module.ubuntu_nva_firewall
  ]
}


