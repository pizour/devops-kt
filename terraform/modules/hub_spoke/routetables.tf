# Route Tables
resource "azurerm_route_table" "route_table" {
  for_each = merge([
    for vnet_name, vnet_config in var.vnets : {
      for subnet_name, subnet_cidr in vnet_config.subnets :
      "${vnet_name}/${subnet_name}" => {
        vnet_name   = vnet_name
        subnet_name = subnet_name
      }
    }
  ]...)

  name                = "${var.project_name}-${each.value.vnet_name}-${each.value.subnet_name}-rt"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

# Routes for spoke and hub subnets (default route to NVA firewall)
resource "azurerm_route" "spoke_default_route" {
  for_each = merge([
    for vnet_name, vnet_config in var.vnets : {
      for subnet_name in keys(vnet_config.subnets) :
      "${vnet_name}/${subnet_name}" => {
        route_table_key = "${vnet_name}/${subnet_name}"
      } if subnet_name != "hub-fw-snet"
    }
  ]...)

  name                   = "default-route-to-nva"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.route_table[each.value.route_table_key].name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = var.nva_private_ip
}

# Route for firewall subnet - internal networks via vnet peering
resource "azurerm_route" "fw_internal_route" {
  name                = "internal-networks"
  resource_group_name = var.resource_group_name
  route_table_name    = azurerm_route_table.route_table["hub-vnet/hub-fw-snet"].name
  address_prefix      = "10.0.0.0/8"
  next_hop_type       = "VnetLocal"
}

# Route for firewall subnet - default route to Internet
resource "azurerm_route" "fw_default_route" {
  name                = "default-route-to-internet"
  resource_group_name = var.resource_group_name
  route_table_name    = azurerm_route_table.route_table["hub-vnet/hub-fw-snet"].name
  address_prefix      = "0.0.0.0/0"
  next_hop_type       = "Internet"
}

# Subnet Route Table Associations
# NOTE: Azure Bastion subnet (AzureBastionSubnet) cannot have custom route tables attached.
# It is excluded from route table association.
resource "azurerm_subnet_route_table_association" "subnet_rt_association" {
  for_each = {
    for key, subnet in merge([
      for vnet_name, vnet_config in var.vnets : {
        for subnet_name, subnet_cidr in vnet_config.subnets :
        "${vnet_name}/${subnet_name}" => {
          vnet_name   = vnet_name
          subnet_name = subnet_name
        }
      }
    ]...) :
    key => subnet if !contains(split("/", key), "AzureBastionSubnet")
  }

  subnet_id      = azurerm_subnet.subnet["${each.value.vnet_name}/${each.value.subnet_name}"].id
  route_table_id = azurerm_route_table.route_table["${each.value.vnet_name}/${each.value.subnet_name}"].id
}
