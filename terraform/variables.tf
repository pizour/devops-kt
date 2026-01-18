
variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure service principal client ID"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure service principal client secret"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure tenant ID"
  type        = string
  sensitive   = true
}

variable "nva_admin_password" {
  description = "Admin password for NVA firewall VM"
  type        = string
  sensitive   = true
}

variable "allowed_ssh_ips" {
  description = "List of IP addresses allowed to SSH to the NVA firewall"
  type        = list(string)
  sensitive   = true
}
