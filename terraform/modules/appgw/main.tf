terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.57"
    }
  }
}

# Public IP for Application Gateway
resource "azurerm_public_ip" "appgw_pip" {
  name                = "${var.appgw_name}-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.common_tags
}

# Application Gateway with WAF
resource "azurerm_application_gateway" "appgw" {
  name                = var.appgw_name
  location            = var.location
  resource_group_name = var.resource_group_name

  sku {
    name     = var.sku_name
    tier     = var.sku_tier
    capacity = var.capacity
  }

  # WAF Configuration
  waf_configuration {
    enabled          = var.waf_enabled
    firewall_mode    = var.waf_firewall_mode
    rule_set_type    = var.waf_rule_set_type
    rule_set_version = var.waf_rule_set_version
  }

  # Gateway IP Configuration (subnet)
  gateway_ip_configuration {
    name      = "appgw-ip-configuration"
    subnet_id = var.subnet_id
  }

  # Frontend IP Configuration (public)
  frontend_ip_configuration {
    name                 = "appgw-frontend-ip"
    public_ip_address_id = azurerm_public_ip.appgw_pip.id
  }

  # Frontend Port - HTTP only
  frontend_port {
    name = "http-port"
    port = var.frontend_port
  }

  # HTTP Listener
  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "appgw-frontend-ip"
    frontend_port_name             = "http-port"
    protocol                       = "Http"
  }

  # Backend Address Pool - NVA Firewall VM
  backend_address_pool {
    name         = "nva-backend-pool"
    ip_addresses = [var.backend_ip_address]
  }

  # Backend HTTP Settings - API1 (port 5000)
  backend_http_settings {
    name                  = "api1-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = var.backend_api1_port
    protocol              = "Http"
    request_timeout       = var.backend_request_timeout
    probe_name            = "health-probe-api1"
  }

  # Backend HTTP Settings - API2 (port 5001)
  backend_http_settings {
    name                  = "api2-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = var.backend_api2_port
    protocol              = "Http"
    request_timeout       = var.backend_request_timeout
    probe_name            = "health-probe-api2"
  }

  # Health Probe - API1 (port 5000)
  probe {
    name                = "health-probe-api1"
    protocol            = "Http"
    path                = var.health_probe_path
    host                = var.backend_ip_address
    interval            = var.health_probe_interval
    timeout             = var.health_probe_timeout
    unhealthy_threshold = var.health_probe_unhealthy_threshold
    port                = var.backend_api1_port
  }

  # Health Probe - API2 (port 5001)
  probe {
    name                = "health-probe-api2"
    protocol            = "Http"
    path                = var.health_probe_path
    host                = var.backend_ip_address
    interval            = var.health_probe_interval
    timeout             = var.health_probe_timeout
    unhealthy_threshold = var.health_probe_unhealthy_threshold
    port                = var.backend_api2_port
  }

  # URL Path Map for path-based routing
  url_path_map {
    name                               = "path-based-routing"
    default_backend_address_pool_name  = "nva-backend-pool"
    default_backend_http_settings_name = "api1-http-settings"

    path_rule {
      name                       = "api1-rule"
      paths                      = ["/api1/*"]
      backend_address_pool_name  = "nva-backend-pool"
      backend_http_settings_name = "api1-http-settings"
    }

    path_rule {
      name                       = "api2-rule"
      paths                      = ["/api2/*"]
      backend_address_pool_name  = "nva-backend-pool"
      backend_http_settings_name = "api2-http-settings"
    }
  }

  # Request Routing Rule - Path-based
  request_routing_rule {
    name                       = "path-based-rule"
    priority                   = 100
    rule_type                  = "PathBasedRouting"
    http_listener_name         = "http-listener"
    url_path_map_name          = "path-based-routing"
  }

  tags = var.common_tags
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "appgw" {
  name                = "${var.appgw_name}-law"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_analytics_retention_days

  tags = var.common_tags
}

# Diagnostic Settings - Send AGW and WAF logs to Log Analytics
resource "azurerm_monitor_diagnostic_setting" "appgw" {
  name                       = "${var.appgw_name}-diagnostics"
  target_resource_id         = azurerm_application_gateway.appgw.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.appgw.id

  # Application Gateway Access Log
  enabled_log {
    category = "ApplicationGatewayAccessLog"
  }

  # Application Gateway Performance Log
  enabled_log {
    category = "ApplicationGatewayPerformanceLog"
  }

  # Application Gateway Firewall (WAF) Log
  enabled_log {
    category = "ApplicationGatewayFirewallLog"
  }
}
