terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.57"
    }
  }
}

# Network Interface for NVA (Primary - Firewall subnet)
resource "azurerm_network_interface" "nva_nic" {
  name                  = "${var.project_name}-${var.nva_name}-nic"
  location              = var.location
  resource_group_name   = var.resource_group_name
  ip_forwarding_enabled = var.enable_ip_forwarding

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = var.firewall_subnet_id
    private_ip_address_allocation = "Static"
    private_ip_address            = var.private_ip_address
    public_ip_address_id          = var.enable_public_ip ? azurerm_public_ip.nva_pip[0].id : null
    primary                       = true
  }

  accelerated_networking_enabled = var.enable_accelerated_networking

  tags = var.common_tags
}

# Public IP for NVA (optional)
resource "azurerm_public_ip" "nva_pip" {
  count               = var.enable_public_ip ? 1 : 0
  name                = "${var.project_name}-${var.nva_name}-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.common_tags
}

# Virtual Machine for NVA
resource "azurerm_linux_virtual_machine" "nva_vm" {
  name                = "${var.project_name}-${var.nva_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  admin_username      = var.admin_username

  size = var.vm_size

  network_interface_ids = [
    azurerm_network_interface.nva_nic.id
  ]

  # Use password authentication
  disable_password_authentication = false

  admin_password = var.admin_password

  os_disk {
    name                 = "${var.project_name}-${var.nva_name}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = var.os_disk_type
  }

  source_image_reference {
    publisher = var.image_publisher
    offer     = var.image_offer
    sku       = var.image_sku
    version   = var.image_version
  }

  # Custom data for initial configuration
  user_data = base64encode(templatefile("${path.module}/init-script.sh", {}))

  tags = var.common_tags
}


