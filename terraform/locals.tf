# Load configuration from YAML files
locals {
  # Load YAML configurations
  project_config      = yamldecode(file("${path.module}/config/project.yaml"))
  vnets_config        = yamldecode(file("${path.module}/config/vnets.yaml"))
  nsgs_config         = yamldecode(file("${path.module}/config/nsgs.yaml"))
  nva_firewall_config = yamldecode(file("${path.module}/config/nva_firewall.yaml"))
  aks_config          = yamldecode(file("${path.module}/config/aks.yaml"))

  # Dynamic values
  project_name   = local.project_config.project_name
  azure_location = local.project_config.azure_location

  common_tags = merge(
    local.project_config.common_tags,
    {
      Environment = local.environment
      Project     = local.project_name
    }
  )

  # Configuration values from YAML files
  environment               = local.project_config.environment
  azure_resource_group_name = local.project_config.azure_resource_group_name
  nva_private_ip            = local.nva_firewall_config.nva_firewall.private_ip_address
  default_nsg_rules         = local.nsgs_config.default_rules
  vnets                     = local.vnets_config

  # Process NSG rules: replace ALLOWED_SSH_IPS placeholder with actual IPs from tfvars
  subnet_nsgs = {
    for subnet_key, nsg_config in local.nsgs_config.subnet_nsgs : subnet_key => {
      nsg_name = nsg_config.nsg_name
      rules = [
        for rule in nsg_config.rules : merge(rule, {
          # Replace ALLOWED_SSH_IPS placeholder with comma-separated list of allowed IPs
          source_address_prefix = rule.source_address_prefix == "ALLOWED_SSH_IPS" ? join(",", var.allowed_ssh_ips) : rule.source_address_prefix
        })
      ]
    }
  }

  # NVA Firewall configuration
  nva_firewall = local.nva_firewall_config.nva_firewall

  # AKS configuration
  aks = local.aks_config
}

