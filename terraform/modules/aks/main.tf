# Managed Identity for AKS
resource "azurerm_user_assigned_identity" "aks" {
  name                = "${var.cluster_name}-identity"
  resource_group_name = var.resource_group_name
  location            = var.location

  tags = var.common_tags
}

# Role assignment for AKS to manage its resources
# NOTE: Requires service principal to have "User Access Administrator" or "Owner" role
# To enable: Uncomment this block after granting appropriate RBAC permissions to the service principal
# resource "azurerm_role_assignment" "aks_network_contributor" {
#   scope                = var.resource_group_id
#   role_definition_name = "Network Contributor"
#   principal_id         = azurerm_user_assigned_identity.aks.principal_id
# }

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix

  kubernetes_version = var.kubernetes_version
  default_node_pool {
    name           = var.default_node_pool_name
    node_count     = var.node_count
    vm_size        = var.vm_size
    vnet_subnet_id = var.subnet_id

    tags = var.common_tags
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aks.id]
  }

  network_profile {
    network_plugin    = "azure"
    service_cidr      = var.service_cidr
    dns_service_ip    = var.dns_service_ip
    load_balancer_sku = "standard"
  }

  http_application_routing_enabled = var.enable_http_application_routing
  azure_policy_enabled             = var.enable_azure_policy

  depends_on = [
    # azurerm_role_assignment.aks_network_contributor,  # Requires elevated RBAC permissions
  ]

  tags = var.common_tags
}

# Kubelet Identity Role Assignment
# Kubelet managed identity operator role assignment
# NOTE: Requires service principal to have "User Access Administrator" or "Owner" role
# To enable: Uncomment this block after granting appropriate RBAC permissions to the service principal
# resource "azurerm_role_assignment" "kubelet_managed_identity_operator" {
#   scope                = azurerm_user_assigned_identity.aks.id
#   role_definition_name = "Managed Identity Operator"
#   principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
# }
