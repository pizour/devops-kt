variable "project_name" {
  description = "Project name"
  type        = string
}

variable "location" {
  description = "Azure location/region"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
}

variable "vnets" {
  description = "Virtual networks configuration"
  type = map(object({
    address_space = list(string)
    subnets       = map(string)
    hub           = optional(bool, false)
  }))
}

variable "nva_private_ip" {
  description = "NVA firewall private IP address to use as next hop for all routes"
  type        = string
}

variable "subnet_nsgs" {
  description = "Network Security Groups configuration per subnet"
  type = map(object({
    nsg_name = string
    rules = optional(list(object({
      name                       = string
      priority                   = number
      direction                  = string
      access                     = string
      protocol                   = string
      source_port_range          = string
      destination_port_range     = string
      source_address_prefix      = string
      destination_address_prefix = string
    })), [])
  }))
  default = {}
}

variable "default_nsg_rules" {
  description = "Default NSG rules applied to all subnets"
  type = list(object({
    name                       = string
    priority                   = number
    direction                  = string
    access                     = string
    protocol                   = string
    source_port_range          = string
    destination_port_range     = string
    source_address_prefix      = string
    destination_address_prefix = string
  }))
  default = []
}

