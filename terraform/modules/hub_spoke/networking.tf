# Virtual Networks
resource "azurerm_virtual_network" "vnet" {
  for_each = var.vnets

  name                = "${var.project_name}-${each.key}-vnet"
  address_space       = each.value.address_space
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

# Subnets
resource "azurerm_subnet" "subnet" {
  for_each = merge([
    for vnet_name, vnet_config in var.vnets : {
      for subnet_name, subnet_cidr in vnet_config.subnets :
      "${vnet_name}/${subnet_name}" => {
        vnet_name   = vnet_name
        subnet_name = subnet_name
        subnet_cidr = subnet_cidr
      }
    }
  ]...)

  name                 = each.value.subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet[each.value.vnet_name].name
  address_prefixes     = [each.value.subnet_cidr]

  default_outbound_access_enabled = false
}

# VNet Peerings
locals {
  hub_vnet_key = [for hub_key, hub_config in var.vnets : hub_key if try(hub_config.hub, false) == true][0]
}

resource "azurerm_virtual_network_peering" "peering" {
  for_each = {
    for idx, peering in flatten([
      for spoke_key, spoke_config in var.vnets : try(spoke_config.hub, false) != true ? [
        {
          from                  = local.hub_vnet_key
          to                    = spoke_key
          allow_gateway_transit = false
          use_remote_gateways   = false
        },
        {
          from                  = spoke_key
          to                    = local.hub_vnet_key
          allow_gateway_transit = false
          use_remote_gateways   = false
        }
      ] : []
    ]) :
    "${peering.from}-to-${peering.to}" => peering
  }

  name                         = "${each.value.from}-to-${each.value.to}"
  resource_group_name          = var.resource_group_name
  virtual_network_name         = azurerm_virtual_network.vnet[each.value.from].name
  remote_virtual_network_id    = azurerm_virtual_network.vnet[each.value.to].id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
  allow_gateway_transit        = each.value.allow_gateway_transit
  use_remote_gateways          = each.value.use_remote_gateways
}
