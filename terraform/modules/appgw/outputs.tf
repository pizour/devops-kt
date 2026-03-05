output "appgw_id" {
  description = "Application Gateway ID"
  value       = azurerm_application_gateway.appgw.id
}

output "appgw_name" {
  description = "Application Gateway name"
  value       = azurerm_application_gateway.appgw.name
}

output "appgw_public_ip" {
  description = "Application Gateway public IP address"
  value       = azurerm_public_ip.appgw_pip.ip_address
}

output "appgw_public_ip_id" {
  description = "Application Gateway public IP ID"
  value       = azurerm_public_ip.appgw_pip.id
}

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = azurerm_log_analytics_workspace.appgw.id
}

output "log_analytics_workspace_name" {
  description = "Log Analytics Workspace name"
  value       = azurerm_log_analytics_workspace.appgw.name
}
