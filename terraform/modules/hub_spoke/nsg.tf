# Network Security Groups
resource "azurerm_network_security_group" "nsg" {
  for_each = var.subnet_nsgs

  name                = each.value.nsg_name
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.common_tags
}

# NSG Rules
resource "azurerm_network_security_rule" "nsg_rule" {
  for_each = {
    for rule_key, rule in concat(
      flatten([
        for subnet_key, subnet_nsg in var.subnet_nsgs : [
          for rule in var.default_nsg_rules : {
            key            = "${subnet_key}/default/${rule.name}"
            nsg_key        = subnet_key
            name           = "default-${rule.name}"
            priority       = rule.priority
            direction      = rule.direction
            access         = rule.access
            protocol       = rule.protocol
            source_port    = rule.source_port_range
            dest_port      = rule.destination_port_range
            source_address = rule.source_address_prefix
            dest_address   = rule.destination_address_prefix
          }
        ]
      ]),
      flatten([
        for subnet_key, subnet_nsg in var.subnet_nsgs : [
          for rule in try(subnet_nsg.rules, []) : {
            key            = "${subnet_key}/${rule.name}"
            nsg_key        = subnet_key
            name           = rule.name
            priority       = rule.priority + 1000
            direction      = rule.direction
            access         = rule.access
            protocol       = rule.protocol
            source_port    = rule.source_port_range
            dest_port      = rule.destination_port_range
            source_address = rule.source_address_prefix
            dest_address   = rule.destination_address_prefix
          }
        ]
      ])
    ) : rule_key => rule
  }

  name                        = each.value.name
  priority                    = each.value.priority
  direction                   = each.value.direction
  access                      = each.value.access
  protocol                    = each.value.protocol
  source_port_range           = each.value.source_port
  destination_port_range      = each.value.dest_port
  source_address_prefix       = each.value.source_address
  destination_address_prefix  = each.value.dest_address
  resource_group_name         = var.resource_group_name
  network_security_group_name = azurerm_network_security_group.nsg[each.value.nsg_key].name
}

# NSG Subnet Association
# NOTE: Azure Bastion subnet (AzureBastionSubnet) requires specific NSG rules.
# It is excluded from generic subnet NSG association.
resource "azurerm_subnet_network_security_group_association" "subnet_nsg" {
  for_each = {
    for key, nsg in var.subnet_nsgs :
    key => nsg if !contains(split("/", key), "AzureBastionSubnet")
  }

  subnet_id                 = azurerm_subnet.subnet[each.key].id
  network_security_group_id = azurerm_network_security_group.nsg[each.key].id
}
