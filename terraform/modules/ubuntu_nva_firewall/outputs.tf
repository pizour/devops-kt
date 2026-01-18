output "nva_id" {
  description = "NVA VM ID"
  value       = azurerm_linux_virtual_machine.nva_vm.id
}

output "nva_name" {
  description = "NVA VM name"
  value       = azurerm_linux_virtual_machine.nva_vm.name
}

output "nva_private_ip" {
  description = "NVA private IP address"
  value       = azurerm_network_interface.nva_nic.private_ip_address
}

output "nva_public_ip" {
  description = "NVA public IP address"
  value       = var.enable_public_ip ? azurerm_public_ip.nva_pip[0].ip_address : null
}

output "nva_public_ip_id" {
  description = "NVA public IP ID"
  value       = var.enable_public_ip ? azurerm_public_ip.nva_pip[0].id : null
}

output "nva_nic_id" {
  description = "NVA network interface ID"
  value       = azurerm_network_interface.nva_nic.id
}
