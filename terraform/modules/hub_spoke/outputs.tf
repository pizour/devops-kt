output "vnets" {
  description = "Virtual networks"
  value = {
    for name, vnet in azurerm_virtual_network.vnet :
    name => {
      id   = vnet.id
      name = vnet.name
    }
  }
}

output "subnets" {
  description = "All subnets"
  value = {
    for key, subnet in azurerm_subnet.subnet :
    key => {
      id   = subnet.id
      name = subnet.name
    }
  }
}

output "vnet_ids" {
  description = "Map of VNet names to IDs"
  value = {
    for name, vnet in azurerm_virtual_network.vnet :
    name => vnet.id
  }
}

output "subnet_ids" {
  description = "Flat map of all subnet IDs keyed by vnet/subnet"
  value = {
    for key, subnet in azurerm_subnet.subnet :
    key => subnet.id
  }
}
output "route_tables" {
  description = "All route tables"
  value = {
    for key, rt in azurerm_route_table.route_table :
    key => {
      id   = rt.id
      name = rt.name
    }
  }
}

output "route_table_ids" {
  description = "Map of route table IDs keyed by vnet/subnet"
  value = {
    for key, rt in azurerm_route_table.route_table :
    key => rt.id
  }
}

output "nsgs" {
  description = "All network security groups"
  value = {
    for key, nsg in azurerm_network_security_group.nsg :
    key => {
      id   = nsg.id
      name = nsg.name
    }
  }
}

output "nsg_ids" {
  description = "Map of NSG IDs keyed by subnet"
  value = {
    for key, nsg in azurerm_network_security_group.nsg :
    key => nsg.id
  }
}