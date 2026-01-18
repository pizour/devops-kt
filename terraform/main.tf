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

# AKS Module
module "aks" {
  source = "./modules/aks"

  cluster_name        = "${local.azure_resource_group_name}-aks"
  dns_prefix          = replace(local.azure_resource_group_name, "-", "")
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  resource_group_id   = azurerm_resource_group.main.id

  subnet_id = module.hub_spoke.subnet_ids["spoke1-aks-vnet/spoke1-aks-snet"]

  default_node_pool_name = "agentpool"
  node_count             = local.aks.aks_node_count
  vm_size                = local.aks.aks_vm_size
  kubernetes_version     = local.aks.kubernetes_version

  service_cidr   = "10.240.0.0/16"
  dns_service_ip = "10.240.0.10"

  enable_http_application_routing = local.aks.aks_enable_http_routing
  enable_azure_policy             = local.aks.aks_enable_azure_policy

  common_tags = local.common_tags

  depends_on = [
    azurerm_resource_group.main,
    module.hub_spoke
  ]
}


