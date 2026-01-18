# AKS (Azure Kubernetes Service) Module

Creates a production-ready Azure Kubernetes Service cluster integrated with hub-spoke network topology, routing egress traffic through NVA firewall for centralized inspection.

## Overview

This module provisions an AKS cluster configured to:
- **Network Integration**: Deploy into existing spoke VNet subnet using Azure CNI
- **Managed Identity**: Use system-assigned identity for Azure resource access
- **Egress Routing**: Route all outbound traffic through NVA firewall (10.0.0.10)
- **Service Isolation**: Isolated service CIDR (10.240.0.0/16) separate from VNet ranges
- **Flexible Node Pools**: Configurable system node pool with auto-scaling

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Spoke1 VNet (10.1.0.0/16)                       │
│  ┌────────────────────────────────────────────┐  │
│  │  AKS Subnet (10.1.0.0/24)                  │  │
│  │  ┌──────────────────────────────────────┐  │  │
│  │  │ AKS Cluster: devops-kt-aks           │  │  │
│  │  │ - Network Plugin: Azure CNI          │  │  │
│  │  │ - Pod CIDR: Uses VNet IPs            │  │  │
│  │  │ - Service CIDR: 10.240.0.0/16        │  │  │
│  │  │ - DNS: 10.240.0.10                   │  │  │
│  │  │                                      │  │  │
│  │  │ System Node Pool:                    │  │  │
│  │  │ - VM Size: Standard_D4s_v3           │  │  │
│  │  │ - Nodes: 2 (min: 1, max: 5)         │  │  │
│  │  │ - OS Disk: 128GB                     │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────────┘
                   │ 0.0.0.0/0 → 10.0.0.10 (via Route Table)
                   ▼
        ┌────────────────────┐
        │  NVA Firewall      │
        │  (10.0.0.10)       │
        │  iptables SNAT     │
        └──────────┬─────────┘
                   │
                   ▼
              [Internet]
```

## Resources Created

### AKS Cluster
- **Cluster**: Managed Kubernetes with Azure CNI networking
- **Identity**: System-assigned managed identity for Azure API access
- **Network Profile**:
  - Network plugin: azure (Azure CNI)
  - Pod subnet: Uses nodes subnet IPs
  - Service CIDR: 10.240.0.0/16 (isolated from VNet)
  - DNS service IP: 10.240.0.10

### Node Pools
- **System Node Pool**: 
  - Dedicated to Kubernetes system components (CoreDNS, metrics-server, etc.)
  - Auto-scaling enabled (configurable min/max nodes)
  - VM size configurable (default: Standard_D4s_v3)
  - Managed OS disk (default: 128GB)

### Networking
- **Integration**: Deployed into existing spoke VNet subnet
- **Egress**: All traffic (internet, Azure services) routes through NVA firewall
- **Service Network**: Isolated CIDR for ClusterIP services
- **Load Balancer**: Standard SKU for ingress (optional)

## Key Features

- **Azure CNI Networking**: Each pod gets VNet IP for direct communication
- **System-Assigned Managed Identity**: No credential management required
- **Firewall Egress**: Centralized traffic inspection via NVA
- **Service CIDR Isolation**: Service IPs isolated from VNet (10.240.0.0/16)
- **Auto-Scaling**: Configurable node count with automatic scaling
- **Configurable VM Sizes**: Choose appropriate node compute resources
- **YAML-Driven Config**: Cluster settings defined in aks.yaml

## Configuration

### config/aks.yaml

```yaml
aks_cluster:
  cluster_name_suffix: aks
  kubernetes_version: "1.28"
  
  network:
    network_plugin: azure
    service_cidr: 10.240.0.0/16
    dns_service_ip: 10.240.0.10
    
  default_node_pool:
    name: system
    vm_size: Standard_D4s_v3
    node_count: 2
    min_count: 1
    max_count: 5
    os_disk_size_gb: 128
    enable_auto_scaling: true
```

### Subnet Configuration (vnets.yaml)

```yaml
spoke1-aks-vnet:
  address_space:
    - 10.1.0.0/16
  subnets:
    spoke1-aks-snet: 10.1.0.0/24  # AKS nodes deployed here
```

### Route Table (Applied by hub_spoke module)

```hcl
# All AKS egress traffic routes through firewall
route {
  name                   = "to-nva-firewall"
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = "10.0.0.10"
}
```

## Usage

```hcl
module "aks" {
  source = "./modules/aks"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = local.azure_resource_group_name
  
  # Cluster Configuration
  cluster_name        = "${local.project_name}-${local.aks.aks_cluster.cluster_name_suffix}"
  kubernetes_version  = local.aks.aks_cluster.kubernetes_version
  
  # Network Integration
  subnet_id           = module.hub_spoke.subnet_ids["spoke1-aks-vnet/spoke1-aks-snet"]
  network_plugin      = local.aks.aks_cluster.network.network_plugin
  service_cidr        = local.aks.aks_cluster.network.service_cidr
  dns_service_ip      = local.aks.aks_cluster.network.dns_service_ip
  
  # Node Pool Configuration
  default_node_pool = {
    name                = local.aks.aks_cluster.default_node_pool.name
    vm_size             = local.aks.aks_cluster.default_node_pool.vm_size
    node_count          = local.aks.aks_cluster.default_node_pool.node_count
    min_count           = local.aks.aks_cluster.default_node_pool.min_count
    max_count           = local.aks.aks_cluster.default_node_pool.max_count
    os_disk_size_gb     = local.aks.aks_cluster.default_node_pool.os_disk_size_gb
    enable_auto_scaling = local.aks.aks_cluster.default_node_pool.enable_auto_scaling
  }
  
  common_tags = local.common_tags
}
```

## Input Variables

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_name` | string | Yes | Project name for resource naming |
| `location` | string | Yes | Azure region (e.g., westeurope) |
| `resource_group_name` | string | Yes | Resource group name (must exist) |
| `cluster_name` | string | Yes | AKS cluster name (e.g., devops-kt-aks) |
| `kubernetes_version` | string | Yes | Kubernetes version (e.g., "1.28") |
| `subnet_id` | string | Yes | Subnet resource ID for AKS nodes |
| `network_plugin` | string | Yes | Network plugin: "azure" (CNI) or "kubenet" |
| `service_cidr` | string | Yes | CIDR for Kubernetes services (e.g., 10.240.0.0/16) |
| `dns_service_ip` | string | Yes | IP for cluster DNS service (within service_cidr) |
| `default_node_pool` | object | Yes | Node pool configuration (name, vm_size, count, etc.) |
| `common_tags` | map(string) | No | Common tags for all resources |

## Outputs

| Name | Description |
|------|-------------|
| `cluster_id` | AKS cluster resource ID |
| `cluster_name` | AKS cluster name (e.g., devops-kt-aks) |
| `kube_config` | Kubernetes configuration (sensitive) |
| `kube_config_raw` | Raw kubeconfig content (sensitive) |
| `cluster_fqdn` | Cluster FQDN for API server |
| `cluster_identity` | Managed identity details |
| `node_resource_group` | Auto-created resource group for nodes |

## Network Traffic Flow

### Pod to Internet

```
AKS Pod (10.1.0.50)
  ↓ Destination: External API (e.g., api.github.com)
Route Table on spoke1-aks-snet: 0.0.0.0/0 → 10.0.0.10
  ↓
NVA Firewall (10.0.0.10)
  [iptables SNAT: 10.1.0.50 → NVA Public IP]
  ↓
Internet
  [Sees traffic from NVA Public IP]
```

### Service to Service (Within Cluster)

```
Pod A (10.1.0.50) → Service: my-app (10.240.0.100)
  ↓ ClusterIP service
Kube-proxy (iptables/IPVS)
  ↓ Load balances to Pod B
Pod B (10.1.0.60)
  [No route table involved - direct VNet communication]
```

### External to AKS (LoadBalancer Service)

```
Internet → Azure Load Balancer Public IP
  ↓ Load balancer backend pool
AKS Node (10.1.0.10)
  ↓ NodePort → Pod
Pod (10.1.0.50)
  [Return traffic via same path]
```

## Post-Deployment

### Connect to Cluster

```bash
# Get cluster credentials
az aks get-credentials --resource-group devops-kt-rg \
  --name devops-kt-aks

# Verify connection
kubectl get nodes
kubectl get pods -A

# Check cluster info
kubectl cluster-info
```

### Verify Network Configuration

```bash
# Check pod network IPs (should be in 10.1.0.0/24)
kubectl get pods -o wide -A

# Check service IPs (should be in 10.240.0.0/16)
kubectl get svc -A

# Test egress routing
kubectl run test-pod --image=busybox --rm -it -- /bin/sh
# Inside pod:
wget -qO- ifconfig.me  # Should show NVA public IP
```

### Deploy Sample Application

```bash
# Deploy nginx
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Get external IP (from Azure Load Balancer)
kubectl get svc nginx

# Test access
curl http://<external-ip>
```

## Scaling and Management

### Scale Node Pool

```bash
# Manual scaling
az aks nodepool scale --resource-group devops-kt-rg \
  --cluster-name devops-kt-aks \
  --name system \
  --node-count 4

# Auto-scaling already enabled via config
# Nodes will scale between min_count (1) and max_count (5)
```

### Upgrade Kubernetes Version

```bash
# Check available versions
az aks get-upgrades --resource-group devops-kt-rg \
  --name devops-kt-aks

# Upgrade cluster
az aks upgrade --resource-group devops-kt-rg \
  --name devops-kt-aks \
  --kubernetes-version 1.29

# Monitor upgrade
az aks show --resource-group devops-kt-rg \
  --name devops-kt-aks \
  --query "provisioningState"
```

### Add User Node Pool

```bash
# Add dedicated node pool for applications
az aks nodepool add \
  --resource-group devops-kt-rg \
  --cluster-name devops-kt-aks \
  --name userpool \
  --node-count 2 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10

# List node pools
az aks nodepool list --resource-group devops-kt-rg \
  --cluster-name devops-kt-aks -o table
```

## Security Considerations

### Network Security

- **NSG on AKS Subnet**: Priority 100 allows intra-subnet traffic
- **Egress Control**: All internet traffic inspected by NVA firewall
- **Service Network Isolation**: ClusterIP services use isolated CIDR (10.240.0.0/16)
- **No Direct Internet**: Pods cannot reach internet without routing through firewall

### Managed Identity

- **System-Assigned**: Automatically created and managed by Azure
- **RBAC**: Grant cluster identity only necessary Azure permissions
- **No Secrets**: No need to manage service principal credentials

### Best Practices

1. **Enable Azure Policy**: Enforce security policies on cluster
2. **Use Private Cluster**: Consider private cluster for production
3. **Pod Security**: Implement Pod Security Standards
4. **Network Policies**: Use Calico or Azure Network Policy
5. **Image Scanning**: Scan container images for vulnerabilities
6. **RBAC**: Configure Kubernetes RBAC for user access control

## Monitoring

### Azure Monitor for Containers

```bash
# Enable Container Insights (if not already enabled)
az aks enable-addons --resource-group devops-kt-rg \
  --name devops-kt-aks \
  --addons monitoring
```

### Metrics to Monitor

- **Node CPU/Memory**: Identify resource pressure
- **Pod Restarts**: Detect application issues
- **Network Latency**: Monitor firewall routing overhead
- **Disk Usage**: Track storage consumption
- **API Server Response Time**: Cluster health indicator

## Troubleshooting

### Pods Can't Reach Internet

```bash
# Check pod IP and routing
kubectl run test-pod --image=busybox --rm -it -- /bin/sh
ip addr      # Should show IP in 10.1.0.0/24
ip route     # Should show default route

# Test connectivity
ping 10.0.0.10    # Should reach NVA firewall
wget -qO- ifconfig.me  # Should work and show NVA public IP

# If fails, check:
# 1. Route table on spoke1-aks-snet (0.0.0.0/0 → 10.0.0.10)
# 2. NVA IP forwarding enabled
# 3. iptables SNAT rules on NVA
```

### Node Pool Not Scaling

```bash
# Check cluster autoscaler logs
kubectl logs -n kube-system -l app=cluster-autoscaler

# Verify auto-scaling configuration
az aks nodepool show --resource-group devops-kt-rg \
  --cluster-name devops-kt-aks \
  --name system \
  --query "{name:name, enableAutoScaling:enableAutoScaling, minCount:minCount, maxCount:maxCount}"
```

### High Network Latency

```bash
# Test latency to internet via firewall
kubectl run test-pod --image=busybox --rm -it -- /bin/sh
time wget -qO- https://www.google.com

# If high, check:
# 1. NVA VM size (Standard_D2s_v3 may be bottleneck)
# 2. NVA firewall CPU/memory usage
# 3. Enable accelerated networking on NVA
```

## Cost Optimization

### Current Configuration

- **VM Size**: Standard_D4s_v3 (2 nodes)
- **Auto-Scaling**: 1-5 nodes
- **OS Disk**: 128GB per node
- **Estimated**: ~$300-400/month for 2 nodes

### Optimization Options

1. **Smaller VM Sizes**: Use Standard_D2s_v3 for dev/test ($150-200/month)
2. **Spot Instances**: Use spot VMs for non-critical workloads (up to 90% savings)
3. **Reserved Instances**: 1-year or 3-year commitment (40-60% savings)
4. **Node Pool Scheduling**: Scale down during non-business hours
5. **Efficient Workload Placement**: Use node selectors to pack workloads

## Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Pod scheduling fails** | Pods stuck in Pending | Check node pool has capacity, verify resource requests |
| **No internet from pods** | Timeouts, DNS failures | Verify route table, check NVA firewall config |
| **High egress costs** | Unexpected Azure costs | Review outbound data transfer through NVA |
| **Slow pod startup** | Image pull timeouts | Check NVA firewall latency, consider Azure Container Registry |
| **Service not accessible** | LoadBalancer service timeout | Verify NSG rules, check Azure Load Balancer backend health |

## Related Resources

- [AKS Documentation](https://learn.microsoft.com/en-us/azure/aks/)
- [Azure CNI Networking](https://learn.microsoft.com/en-us/azure/aks/configure-azure-cni)
- [AKS Managed Identity](https://learn.microsoft.com/en-us/azure/aks/use-managed-identity)
- [Cluster Auto scaling](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [AKS Best Practices](https://learn.microsoft.com/en-us/azure/aks/best-practices)
