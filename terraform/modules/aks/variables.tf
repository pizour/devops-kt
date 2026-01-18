variable "cluster_name" {
  description = "AKS cluster name"
  type        = string

  validation {
    condition     = length(var.cluster_name) >= 1 && length(var.cluster_name) <= 63
    error_message = "Cluster name must be between 1 and 63 characters."
  }
}

variable "location" {
  description = "Azure region for AKS cluster"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "resource_group_id" {
  description = "ID of the resource group"
  type        = string
}

variable "dns_prefix" {
  description = "DNS prefix for the AKS cluster"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9-]{1,54}$", var.dns_prefix))
    error_message = "DNS prefix must be alphanumeric and hyphens, between 1 and 54 characters."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = null # null uses latest version
}

variable "subnet_id" {
  description = "Subnet ID for AKS cluster nodes"
  type        = string
}

variable "default_node_pool_name" {
  description = "Name of the default node pool"
  type        = string
  default     = "agentpool"

  validation {
    condition     = length(var.default_node_pool_name) >= 1 && length(var.default_node_pool_name) <= 12
    error_message = "Node pool name must be between 1 and 12 characters."
  }
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 2

  validation {
    condition     = var.node_count >= 1 && var.node_count <= 1000
    error_message = "Node count must be between 1 and 1000."
  }
}

variable "vm_size" {
  description = "VM size for the nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "service_cidr" {
  description = "CIDR range for Kubernetes services"
  type        = string
  default     = "10.240.0.0/16"

  validation {
    condition     = can(cidrhost(var.service_cidr, 0))
    error_message = "Service CIDR must be a valid CIDR block."
  }
}

variable "dns_service_ip" {
  description = "IP address for DNS service"
  type        = string
  default     = "10.240.0.10"

  validation {
    condition     = can(regex("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$", var.dns_service_ip))
    error_message = "DNS service IP must be a valid IP address."
  }
}

variable "enable_http_application_routing" {
  description = "Enable HTTP application routing"
  type        = bool
  default     = false
}

variable "enable_azure_policy" {
  description = "Enable Azure Policy for AKS"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
