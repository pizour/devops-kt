variable "appgw_name" {
  description = "Name of the Application Gateway"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the Application Gateway"
  type        = string
}

variable "sku_name" {
  description = "SKU name for the Application Gateway"
  type        = string
  default     = "WAF_v2"
}

variable "sku_tier" {
  description = "SKU tier for the Application Gateway"
  type        = string
  default     = "WAF_v2"
}

variable "capacity" {
  description = "Number of Application Gateway instances"
  type        = number
  default     = 2
}

# WAF Configuration
variable "waf_enabled" {
  description = "Enable WAF on Application Gateway"
  type        = bool
  default     = true
}

variable "waf_firewall_mode" {
  description = "WAF firewall mode (Detection or Prevention)"
  type        = string
  default     = "Prevention"

  validation {
    condition     = contains(["Detection", "Prevention"], var.waf_firewall_mode)
    error_message = "WAF firewall mode must be 'Detection' or 'Prevention'."
  }
}

variable "waf_rule_set_type" {
  description = "WAF rule set type"
  type        = string
  default     = "OWASP"
}

variable "waf_rule_set_version" {
  description = "WAF rule set version"
  type        = string
  default     = "3.2"
}

# Frontend
variable "frontend_port" {
  description = "Frontend listener port"
  type        = number
  default     = 80
}

# Backend
variable "backend_ip_address" {
  description = "Backend IP address (NVA firewall private IP)"
  type        = string
}

variable "backend_api1_port" {
  description = "Backend port for API1"
  type        = number
  default     = 5000
}

variable "backend_api2_port" {
  description = "Backend port for API2"
  type        = number
  default     = 5001
}

variable "backend_request_timeout" {
  description = "Backend request timeout in seconds"
  type        = number
  default     = 30
}

# Health Probe
variable "health_probe_path" {
  description = "Health probe path"
  type        = string
  default     = "/health"
}

variable "health_probe_interval" {
  description = "Health probe interval in seconds"
  type        = number
  default     = 30
}

variable "health_probe_timeout" {
  description = "Health probe timeout in seconds"
  type        = number
  default     = 30
}

variable "health_probe_unhealthy_threshold" {
  description = "Number of failed probes before marking unhealthy"
  type        = number
  default     = 3
}

# Log Analytics
variable "log_analytics_sku" {
  description = "SKU for Log Analytics Workspace"
  type        = string
  default     = "PerGB2018"
}

variable "log_analytics_retention_days" {
  description = "Log retention in days"
  type        = number
  default     = 30
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
