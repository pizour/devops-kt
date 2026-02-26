# Hub-Spoke Network Architecture on Azure
## DevOps Knowledge Transfer Guide

**Author:** [REDACTED]  
**Date:** January 2026  
**Audience:** Infrastructure Engineers  
**Level:** Intermediate to Advanced


## Table of Contents

1. [Networking Fundamentals](#networking-fundamentals)
   - Network Topology Patterns
   - Azure Networking Basics
   - Hub-Spoke Design Pattern
2. [Architecture Deep Dive](#architecture-deep-dive)
   - Network Topology & IP Planning
   - Security Model (NSGs, UDRs, Firewall)
   - Traffic Flow & Routing
   - Components Overview
3. [Optional Components](#optional-components)
   - Azure Bastion
   - Azure Container Registry
   - Azure Key Vault
   - Private DNS Zones & DNS Resolver
   - Azure Policy
4. [Hands-On Guide](#hands-on-guide)
   - Azure Portal Walkthrough
   - Cost Analysis
   - Troubleshooting Tips


## Overview

This guide covers enterprise-grade network design on Azure using the hub-spoke topology pattern. You'll learn:

- **Network Architecture:** Why hub-spoke topology vs flat networks, Azure VNet peering concepts, IP address planning, network segmentation best practices
- **Security:** Defense-in-depth networking principles, Network Virtual Appliance (NVA) design patterns, NSG vs Firewall comparison, User-Defined Routes (UDR) and forced tunneling
- **Azure Services:** AKS networking and deployment, cost optimization strategies, optional components for enhanced functionality


## Networking Fundamentals

### Network Topology Patterns
**Common Enterprise Network Designs**

### 1. Flat Network (Simple)
```
[Internet] ←→ [Single VNet] ←→ [All Resources]
```
**Pros:** Simple, easy to set up  
**Cons:** No isolation, hard to secure, doesn't scale

### 2. Multi-VNet Isolated (Disconnected)
```
[VNet1] [VNet2] [VNet3] - No connectivity
```
**Pros:** Strong isolation  
**Cons:** No resource sharing, complex connectivity

### 3. Hub-Spoke (Recommended)
```
        [Hub VNet]
       /     |     \
  [Spoke1] [Spoke2] [Spoke3]
```
**Pros:** Centralized management, scalable, cost-effective  
**Cons:** More complex initial setup

**We're implementing #3 today!**


### Azure Networking Basics
**Core Concepts Every Infrastructure Engineer Should Know**

### Virtual Network (VNet)
- Isolated network in Azure cloud
- Defined by CIDR block (e.g., 10.0.0.0/16)
- Resources in same VNet can communicate by default
- Multiple subnets for segmentation

### Subnets
- Subdivision of VNet address space
- Used to organize and secure resources
- Each subnet gets its own route table and NSG
- Cannot span VNets

### VNet Peering
- Connects two VNets (same or different regions)
- Low latency, high bandwidth (Azure backbone)
- Non-transitive by default (A ↔ B, B ↔ C ≠ A ↔ C)
- No downtime to create

### Network Security Group (NSG)
- Stateful firewall rules
- Applied to subnet or NIC level
- 5-tuple matching: Source IP, Source Port, Dest IP, Dest Port, Protocol
- Priority-based rule evaluation (100-4096)


### Hub-Spoke Pattern Theory

**Why This Pattern Emerged**

#### The Problem

Large enterprises have:
- Multiple applications/teams
- Different security requirements
- Need for shared services (DNS, monitoring, firewall)
- Cost constraints (can't duplicate everything)

#### The Solution: Hub-Spoke

**Hub VNet:**
- Central point of connectivity
- Shared services (firewall, VPN gateway, DNS)
- Single point for internet egress
- Connects to on-premises (VPN/ExpressRoute)

**Spoke VNets:**
- Isolated workloads (dev/test/prod)
- Different teams or applications
- Specific security policies
- Only connect to hub (not to each other directly)

**Key Principle:** *"Centralize what's common, isolate what's different"*

### Hub-Spoke Benefits

**Why Infrastructure Engineers Love This Pattern**

#### Security Benefits
- **Centralized inspection:** All traffic through single firewall
- **Network isolation:** Spokes can't talk directly
- **Blast radius containment:** Compromise in one spoke doesn't spread
- **Compliance:** Easier to audit and control egress

#### Operational Benefits
- **Shared services:** One firewall, one VPN, one DNS server
- **Cost optimization:** No duplication of expensive resources
- **Simplified management:** Central policies, easier troubleshooting
- **Clear ownership:** Hub = network team, Spokes = app teams

#### Scalability Benefits
- **Easy to add spokes:** Just peer and configure
- **No mesh complexity:** N spokes = N peerings (not N²)
- **Team autonomy:** Spokes managed independently
- **Growth ready:** Plan for future expansion

### Business Challenge

**Why Hub-Spoke Architecture?**

**Problems We're Solving:**
- ❌ Flat network topology = security risks
- ❌ Each workload managing its own internet egress
- ❌ No centralized traffic inspection
- ❌ Difficult to enforce network policies
- ❌ Costly to replicate shared services

**Our Solution:**
- ✅ Centralized security & traffic inspection
- ✅ Shared services in hub (firewall, monitoring)
- ✅ Isolated workloads in spokes
- ✅ Cost-effective and scalable
- ✅ Compliance-ready architecture

## Architecture Deep Dive

### Our Architecture Overview
**Hub-Spoke Topology**

![Architecture Diagram - See architecture.md]

**Key Components:**
- **Hub VNet (10.0.0.0/16)** - Central connectivity hub
- **Spoke1 VNet (10.1.0.0/16)** - Azure Kubernetes Service
- **Spoke2 VNet (10.2.0.0/16)** - Management & DevOps tools
- **VNet Peering** - High-speed, low-latency connections
- **Ubuntu NVA Firewall** - Central traffic inspection point


### IP Address Planning Theory

**Critical Foundation for Any Network**

#### RFC 1918 Private Address Ranges
```
10.0.0.0/8        (16.7M addresses) - Large enterprises
172.16.0.0/12     (1M addresses)    - Medium orgs
192.168.0.0/16    (65K addresses)   - Small networks/home
```

#### Our Design Principles
1. **Non-overlapping ranges:** Each VNet unique CIDR
2. **Room for growth:** Don't use all space immediately
3. **Logical segmentation:** Hub = 10.0.x, Spokes = 10.1.x, 10.2.x, etc.
4. **Document everything:** IP plan in version control

#### Subnet Sizing Formula
```
/24 = 256 IPs (251 usable - Azure reserves 5)
/25 = 128 IPs (123 usable)
/26 = 64 IPs  (59 usable)
/27 = 32 IPs  (27 usable)
```

**Pro Tip:** Always plan 2x larger than immediate needs!


### Network Topology
**IP Address Design**

| Network | CIDR | Purpose | Subnets |
|---------|------|---------|---------|
| **Hub VNet** | 10.0.0.0/16 | Central hub | Firewall, Bastion, Shared |
| **Spoke1 VNet** | 10.1.0.0/16 | Container workloads | AKS nodes |
| **Spoke2 VNet** | 10.2.0.0/16 | Management | VMs, DevOps tools |
| **AKS Services** | 10.240.0.0/16 | K8s internal | Kubernetes services |

**Design Principles:**
- Non-overlapping IP ranges
- Room for growth (10.3.x, 10.4.x available)
- Clear network segmentation
- RFC 1918 private addressing


### Hub VNet Details
**Central Network Hub (10.0.0.0/16)**

**Subnets:**
- **hub-fw-snet** (10.0.0.0/24)
  - Ubuntu NVA Firewall (10.0.0.4)
  - Public IP for external SSH
  - IP forwarding enabled
  
- **AzureBastionSubnet** (10.0.1.0/24)
  - Secure RDP/SSH gateway
  - No public IPs needed on VMs
  
- **hub-shared-snet** (10.0.3.0/24)
  - Monitoring services
  - Log Analytics
  - Shared tools


### Spoke1 - AKS VNet
**Kubernetes Workload Network (10.1.0.0/16)**

**Subnets:**
- **spoke1-aks-snet** (10.1.0.0/24)
  - AKS cluster nodes
  - System node pool
  - Auto-scaling enabled

**AKS Configuration:**
- **Service CIDR:** 10.240.0.0/16
- **DNS Service IP:** 10.240.0.10
- **Network Plugin:** Azure CNI
- **Egress:** All traffic via NVA firewall

**Use Cases:**
- Microservices applications
- Container workloads
- CI/CD pipelines
- Web applications


### Spoke2 - Management VNet
**DevOps & Management Network (10.2.0.0/16)**

**Subnets:**
- **spoke2-vms-snet** (10.2.0.0/24)
  - Jump boxes
  - DevOps agents
  - Build servers
  - Monitoring tools

**Purpose:**
- Administrative access
- CI/CD infrastructure
- Build/test environments
- Operations tooling


### Network Security Theory
**Defense-in-Depth Principles**

### What is Defense-in-Depth?
**Multiple layers of security controls** - if one fails, others still protect

### OSI Model Security Layers:
```
Layer 7 (Application)  → Web Application Firewall (WAF)
Layer 4-7 (Session+)   → Application Gateway
Layer 3-4 (Network)    → Firewall / NVA
Layer 2-3 (Data Link)  → Network Security Groups (NSG)
Layer 1 (Physical)     → Azure Datacenter Security
```

### Our Implementation:
1. **Perimeter:** NSG on firewall subnet (only allowed IPs)
2. **Network:** Ubuntu NVA with iptables inspection
3. **Subnet:** NSGs on every subnet with default deny
4. **Identity:** Azure AD + RBAC for management
5. **Application:** (Customer responsibility - web app security)

### Security Principle:
**"Trust nothing, verify everything, assume breach"**


### NSG Theory & Best Practices
**Stateful Packet Filtering**

### How NSGs Work:
1. **5-Tuple Matching:**
   - Source IP address
   - Source port
   - Destination IP address
   - Destination port
   - Protocol (TCP/UDP/ICMP/Any)

2. **Priority Evaluation:**
   - Rules evaluated in priority order (100-4096)
   - Lower number = higher priority
   - First match wins, processing stops
   - Default rules at 65000 (can't be deleted)

3. **Stateful Behavior:**
   - Return traffic automatically allowed
   - Connection tracking built-in
   - No need for explicit "allow response" rules

### NSG Best Practices:
- ✅ Use service tags (Internet, VirtualNetwork, AzureLoadBalancer)
- ✅ Start with priority 100, increment by 10
- ✅ Document rule purpose in name/description
- ✅ Default deny at end (priority 4096)
- ✅ Apply to subnets (not NICs) for consistency
- ❌ Avoid overlapping rules
- ❌ Don't allow 0.0.0.0/0 inbound unless necessary


### User-Defined Routes Theory
**Taking Control of Traffic Flow**

### System Routes vs UDRs
**Azure automatically creates system routes:**
- VNet local: 10.0.0.0/16 → VirtualNetwork
- Internet: 0.0.0.0/0 → Internet
- Peered VNets: 10.1.0.0/16 → VNetPeering

**UDRs override system routes** (more specific = wins)

### Next Hop Types:
```
Virtual Appliance   → Custom VM/NVA (our firewall)
Virtual Network Gateway → VPN/ExpressRoute
VNet Peering        → Peered VNet
Internet            → Azure edge
None                → Drop traffic (blackhole)
```

### Our UDR Strategy:
```
Route: 0.0.0.0/0 → Virtual Appliance (10.0.0.4)
Effect: ALL traffic forced through firewall
Why: Centralized inspection & control
```

### Common Pitfall:
❌ **Asymmetric routing** - traffic goes out one path, returns different path  
✅ **Solution:** Ensure UDRs are symmetric, firewall sees both directions


### VNet Peering Deep Dive
**How Spokes Connect to Hub**

### Peering Characteristics:
- **Non-transitive:** A↔B + B↔C ≠ A↔C (by design!)
- **Bidirectional:** Create peering in both directions
- **Low latency:** Azure backbone network (not internet)
- **No bandwidth limit:** Full datacenter speeds
- **No downtime:** Create peering while VNets are in use
- **Cross-region:** Global VNet Peering available

### Peering Configuration Options:

**1. Allow Forwarded Traffic:**
- Receive traffic from OTHER peered networks
- Required for hub-spoke (spokes accept hub-forwarded traffic)
- Our config: ENABLED on all spokes

**2. Allow Gateway Transit:**
- Hub shares its VPN/ExpressRoute gateway
- Spoke VMs use hub's on-premises connectivity
- Our config: Can enable when adding VPN

**3. Use Remote Gateways:**
- Spoke uses hub's gateway
- Cannot have own gateway if enabled
- Our config: Optional for hybrid scenarios

### Why No Direct Spoke-to-Spoke Peering?
- ✅ Forces traffic through hub firewall
- ✅ Centralized security enforcement
- ✅ Easier to audit and log
- ✅ Scales better (N peerings vs N² mesh)


### Security Model - Defense in Depth
**Multi-Layer Security Approach**

**Layer 1: Network Security Groups (NSGs)**
- Subnet-level firewall rules
- Stateful packet filtering
- Allow/Deny rules per subnet

**Layer 2: Ubuntu NVA Firewall**
- Central inspection point
- iptables packet filtering
- NAT for internet access
- Traffic logging

**Layer 3: Access Control**
- IP allowlist for SSH access
- Azure Bastion for secure RDP/SSH
- No direct internet exposure

**Layer 4: Identity & RBAC**
- Azure AD integration
- Service principals
- Managed identities


### Network Security Groups Implementation
**Subnet-Specific NSG Rules**

**Hub Firewall Subnet:**
```
✅ Allow SSH from allowed IPs (configured)
✅ Allow Azure Load Balancer probes
✅ Allow traffic from spoke VNets
❌ Deny all other inbound (priority 4096)
```

**AKS Subnet:**
```
✅ Allow intra-subnet communication
✅ Allow from NVA firewall
✅ Allow Azure health probes
❌ Deny all other inbound
```

**Management Subnet:**
```
✅ Allow intra-subnet communication
✅ Allow from NVA firewall
❌ Deny all other inbound
```


### Ubuntu NVA Firewall - Theory
**Network Virtual Appliance Design Patterns**

### What is an NVA?
**Network Virtual Appliance** = VM performing network function
- Routing, firewalling, VPN, load balancing, IDS/IPS, etc.
- Runs in your VNet like any other VM
- YOU manage it (unlike Azure Firewall/PaaS)

### NVA Options in Azure:
1. **Commercial:** Palo Alto, Fortinet, Check Point ($$$)
2. **Open Source:** pfSense, OPNsense, VyOS
3. **DIY:** Ubuntu/Linux with iptables ← **We're doing this!**

### Why Ubuntu + iptables?
- ✅ **Cost:** ~$30/month vs $1200+ for Azure Firewall
- ✅ **Learning:** Understand Linux networking deeply
- ✅ **Flexibility:** Full control, customize anything
- ✅ **Skills:** Transferable to any Linux environment
- ❌ **Cons:** YOU manage patches, HA, monitoring

### When to Use What?
- **Dev/Test:** Ubuntu NVA (cost-effective)
- **Small Production:** Ubuntu NVA with HA setup
- **Enterprise Production:** Azure Firewall or commercial NVA
- **Compliance-heavy:** Commercial NVA (certified)


### IP Forwarding & Routing Explained
**How the NVA Routes Traffic**

### Normal VM vs NVA:
**Normal VM:**
```
Receives packet → Is it for me? 
  Yes → Process it
  No  → DROP (default behavior)
```

**NVA with IP Forwarding:**
```
Receives packet → Is it for me?
  Yes → Process it
  No  → Forward to destination (act as router)
```

### Linux IP Forwarding:
```bash
# Enable at OS level
echo 1 > /proc/sys/net/ipv4/ip_forward

# Make permanent
sysctl -w net.ipv4.ip_forward=1
```

### Azure IP Forwarding:
- Must be enabled on VM's Network Interface
- Tells Azure: "This VM will forward packets"
- Without this: Azure drops forwarded packets (security)

### Our Traffic Flow:
```
Spoke1 Pod (10.1.0.50)
     ↓ (UDR: 0.0.0.0/0 → 10.0.0.4)
NVA receives (10.0.0.4) - not destined for NVA!
     ↓ (IP Forwarding enabled)
iptables rules process
     ↓ (NAT or FORWARD)
Destination reached
```


### iptables Fundamentals
**Linux Firewall & NAT Engine**

### iptables Tables & Chains:
```
Table: FILTER (default - packet filtering)
  Chains: INPUT, OUTPUT, FORWARD
  
Table: NAT (address translation)
  Chains: PREROUTING, POSTROUTING, OUTPUT
  
Table: MANGLE (packet alteration)
  Chains: All chains
```

### Packet Flow Through iptables:
```
Packet arrives
     ↓
PREROUTING (NAT) - DNAT happens here
     ↓
Routing decision
     ↓
Is it for me?
  Yes → INPUT chain → Local process
  No  → FORWARD chain → POSTROUTING → OUT
```

### Our NVA iptables Rules:
```bash
# 1. Allow established connections (stateful)
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 2. Allow from spokes to internet
iptables -A FORWARD -s 10.1.0.0/16 -j ACCEPT
iptables -A FORWARD -s 10.2.0.0/16 -j ACCEPT

# 3. NAT outbound traffic (SNAT)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 4. Log dropped packets (troubleshooting)
iptables -A FORWARD -j LOG --log-prefix "NVA-DROP: "
iptables -A FORWARD -j DROP
```

### iptables Best Practices:
- ✅ Use stateful rules (ESTABLISHED,RELATED)
- ✅ Log before drop (troubleshooting)
- ✅ Specific rules before general
- ✅ Document with comments
- ✅ Test rules before making permanent


### Ubuntu NVA Firewall Implementation
**Central Security & Routing**

**Features:**
- **IP Forwarding:** Routes traffic between spokes
- **iptables Firewall:** Packet filtering & NAT
- **Public IP:** External SSH access (restricted)
- **High Availability:** Can add load balancer & redundancy

**Responsibilities:**
- Inspect all spoke-to-spoke traffic
- NAT for internet egress
- Traffic logging & monitoring
- Apply security policies

**Why Ubuntu NVA?**
- Cost-effective alternative to Azure Firewall
- Full control over firewall rules
- Customizable (can add IDS/IPS)
- Learning opportunity for Linux networking


### User-Defined Routes Implementation
**Forced Tunneling to Firewall**

**Spoke Route Tables:**
```
Destination: 0.0.0.0/0
Next Hop Type: Virtual Appliance
Next Hop IP: 10.0.0.4 (NVA Firewall)
```

**What This Means:**
- ALL traffic from spokes goes through NVA
- Spoke-to-Internet → via NVA
- Spoke-to-Spoke → via NVA
- Complete visibility & control

**Benefits:**
- Centralized traffic inspection
- Consistent security policies
- Easy to add DLP, IDS/IPS
- Audit trail for compliance


### Traffic Flow Theory
**Understanding Packet Paths**

### Three Traffic Patterns:

**1. Spoke → Internet**
```
Pod in AKS (10.1.0.50) wants to reach google.com
     ↓
1. Routing lookup: google.com = Internet
2. UDR check: 0.0.0.0/0 → 10.0.0.4 (NVA)
3. Packet sent to 10.0.0.4
4. NVA FORWARD chain processes
5. NVA POSTROUTING NAT (MASQUERADE)
6. Packet exits with NVA's public IP
7. Response returns to NVA
8. NVA de-NATs and forwards back
```

**2. Spoke1 → Spoke2**
```
AKS Pod (10.1.0.50) → Mgmt VM (10.2.0.10)
     ↓
1. Routing: 10.2.0.10 not in local VNet
2. UDR: 0.0.0.0/0 → 10.0.0.4 (NVA)
3. Packet to NVA via peering
4. NVA inspects in FORWARD chain
5. NVA forwards to 10.2.0.10
6. Packet uses hub→spoke2 peering
7. Mgmt VM receives packet
8. Response follows same path back
```

**3. Internet → NVA SSH**
```
Admin laptop (allowed IP) → NVA port 22
     ↓
1. Reaches NVA public IP
2. NSG check: Source IP in allowed list?
3. If yes: Packet delivered to NVA
4. NVA INPUT chain processes
5. SSH daemon responds
```

### Key Concept: Asymmetric Routing
**Problem:** Traffic goes one path, returns different path  
**Solution:** Ensure UDRs are symmetric, use same firewall for both directions


### Traffic Flow - Inbound
**External → Azure**

**1. SSH to NVA Firewall:**
```
User (allowed IP) → Internet → Azure Public IP → NVA (10.0.0.4)
         ↓
    NSG Check: Is source IP allowed?
         ↓
    ✅ Allowed → SSH session established
    ❌ Denied → Connection dropped
```

**2. Bastion Access (Optional):**
```
User → HTTPS (443) → Azure Bastion → RDP/SSH → Management VM
         ↓
    No public IPs needed on VMs
    Fully managed by Azure
```


### Traffic Flow - Outbound
**Azure → Internet**

**Spoke VM/Pod accessing Internet:**
```
Spoke VM/Pod (10.1.0.x or 10.2.0.x)
         ↓
    UDR forces to NVA (10.0.0.4)
         ↓
    NVA Firewall inspects packet
         ↓
    NAT to NVA public IP
         ↓
    Internet destination
```

**Benefits:**
- Single egress point for monitoring
- Apply web filtering rules
- Virus scanning possible
- Traffic logging


### Traffic Flow - Inter-Spoke
**Spoke1 ↔ Spoke2**

**AKS Pod → Management VM:**
```
AKS Pod (10.1.0.50) wants to reach Management VM (10.2.0.10)
         ↓
    UDR: 0.0.0.0/0 → 10.0.0.4
         ↓
    Packet sent to NVA Firewall
         ↓
    NVA inspects: Source, Destination, Ports
         ↓
    NVA forwards to Spoke2 via VNet peering
         ↓
    Management VM receives packet
```

**Key Point:** No direct spoke-to-spoke connectivity!


### Azure Kubernetes Service Theory
**Container Orchestration Fundamentals**

### What is Kubernetes?
- **Container orchestrator** = manages containerized applications
- **Google-born, CNCF project** - industry standard
- **Declarative** - you describe desired state, K8s maintains it

### Core K8s Concepts:
```
Pod          → Smallest unit, 1+ containers
Node         → VM running pods (worker machine)
Deployment   → Manages pod replicas
Service      → Stable endpoint for pods
Namespace    → Virtual cluster for isolation
Ingress      → HTTP(S) routing to services
```

### AKS Value Proposition:
**Without AKS (DIY Kubernetes):**
- ❌ Manually provision VMs
- ❌ Install & configure control plane
- ❌ Manage certificates, etcd, API server
- ❌ Upgrade Kubernetes versions yourself
- ❌ Setup monitoring, logging
- ❌ Configure networking (CNI)

**With AKS:**
- ✅ Control plane FREE (Microsoft manages)
- ✅ Automated upgrades available
- ✅ Azure-integrated networking (CNI)
- ✅ Built-in monitoring (Azure Monitor)
- ✅ RBAC with Azure AD
- ✅ Auto-scaling (nodes & pods)

### AKS Cost Model:
- Control plane: FREE
- Worker nodes: Pay for VMs only
- Storage: Pay for disks
- Networking: Peering data transfer


### AKS Networking Models
**CNI vs Kubenet**

### Kubenet (Basic Networking):
```
Pods get IPs from separate CIDR (10.244.0.0/16)
Not routable in Azure VNet
NAT on node for external communication
```
**Pros:** IP address efficient, simple  
**Cons:** Poor Azure integration, limited features

### Azure CNI (Advanced Networking) ← **We use this!**
```
Pods get IPs from VNet subnet (10.1.0.0/24)
Pods are first-class VNet citizens
Direct connectivity without NAT
```
**Pros:**
- ✅ Pods routable in VNet (no NAT)
- ✅ NSG rules can target pods
- ✅ UDRs apply to pod traffic
- ✅ VNet integration features
- ✅ Better performance

**Cons:**
- ❌ Consumes more IPs (plan subnet size!)
- ❌ Max pods/node limited by IPs

### Our Configuration:
- **Node subnet:** 10.1.0.0/24 (251 IPs)
- **Service CIDR:** 10.240.0.0/16 (separate, overlay)
- **DNS IP:** 10.240.0.10 (first in service CIDR)
- **Network plugin:** Azure CNI
- **Network policy:** Azure or Calico (pod-to-pod rules)

### Planning Formula:
```
IPs needed = nodes + (nodes × max_pods_per_node) + overhead
Example: 3 nodes × 30 pods = 90 + 3 + 10 = ~103 IPs
Recommendation: /24 (251 IPs) for small clusters
```


### Azure Kubernetes Service Implementation
**Container Orchestration Platform**

**Configuration:**
- **Kubernetes Version:** Latest stable
- **Node Pool:** System nodes (auto-scaling)
- **Networking:** Azure CNI
- **Integration:** Azure AD, Azure Monitor

**Security Features:**
- Private cluster option available
- Network policies for pod segmentation
- Azure Policy for governance
- All egress via NVA firewall

**Use Cases:**
- Microservices architecture
- Containerized applications
- CI/CD deployments
- Scalable web services

## Optional Components

These components can be added to enhance the hub-spoke architecture with additional security, governance, and operational capabilities.

### Azure Bastion

**Secure RDP/SSH Without Public IPs**

#### What is Azure Bastion?

A fully managed PaaS service that provides secure and seamless RDP/SSH connectivity to VMs directly through the Azure Portal over TLS.

#### Traditional VM Access Problems
- ❌ Public IPs on VMs (attack surface)
- ❌ Manage NSG rules for RDP/SSH
- ❌ Jump boxes require maintenance
- ❌ VPN complexity for admin access
- ❌ Exposed management ports (3389, 22)

#### Azure Bastion Solution
```
User (Browser) → Azure Portal → Bastion Host → VM (Private IP)
             HTTPS/TLS          RDP/SSH
```

### Key Features:
- ✅ **No Public IP needed on VMs** - Connect via private IP only
- ✅ **TLS over port 443** - Uses Azure Portal for connectivity
- ✅ **Fully managed** - No VM to patch/maintain
- ✅ **NSG hardening** - Only Bastion subnet needs specific rules
- ✅ **Session recording** - Audit logs for compliance
- ✅ **HTML5-based** - No client software needed

### Architecture Requirements:
```
VNet
├── AzureBastionSubnet (/26 minimum)
│   └── Bastion Host (Standard SKU)
│       └── Public IP (Static, Standard)
└── VM Subnets
    └── VMs (Private IPs only)
```

### Subnet Requirements:
- **Name:** MUST be "AzureBastionSubnet" (exact match)
- **Size:** Minimum /26 (64 IPs)
- **NSG:** Optional but recommended

### Cost Model:
- **Basic SKU:** ~$0.19/hour (~$140/month) + data transfer
- **Standard SKU:** ~$0.19/hour + additional features
- **Data transfer:** Outbound data charges apply

### When to Use:
- ✅ Production environments (security compliance)
- ✅ PCI-DSS, HIPAA, SOC2 requirements
- ✅ Zero-trust architecture
- ✅ Centralized access control

### When NOT to Use:
- ❌ Dev/test with tight budgets (use JIT VM access instead)
- ❌ Temporary environments
- ❌ Environments with existing VPN


### Azure Container Registry (ACR)
**Private Docker Image Storage**

### What is ACR?
Azure Container Registry is a managed Docker registry service for storing and managing private container images and artifacts.

### Why Private Registry?
**Docker Hub Problems:**
- ❌ Rate limiting (100 pulls/6h unauthenticated)
- ❌ Public exposure of images
- ❌ No private endpoints
- ❌ No geo-replication
- ❌ Limited scanning/compliance

**ACR Advantages:**
- ✅ Unlimited pulls within Azure
- ✅ Private images with RBAC
- ✅ VNet integration (private endpoints)
- ✅ Geo-replication for HA/DR
- ✅ Image scanning (Defender for Containers)
- ✅ Content trust & signing

### Architecture:
```
Developer → ACR (Private Endpoint) ← AKS Cluster
            │                          │
            └──── Private DNS Zone ────┘
                  privatelink.azurecr.io
```

### SKU Comparison:
| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Storage | 10 GB | 100 GB | 500 GB |
| Webhooks | 2 | 10 | 500 |
| Geo-replication | ❌ | ❌ | ✅ |
| Private endpoints | ❌ | ❌ | ✅ |
| Customer-managed keys | ❌ | ❌ | ✅ |
| Pricing/month | ~$5 | ~$20 | ~$50 |

### Private Endpoint Integration:
**Without Private Endpoint:**
```
AKS → Internet → ACR (public endpoint)
```
**With Private Endpoint:**
```
AKS → VNet (10.1.0.0/16) → Private Endpoint → ACR
         │
         └── Private DNS: myacr.azurecr.io → 10.2.x.x
```

### Security Features:
- **Network isolation** - ACR accessible only from VNet
- **No public access** - Disable public endpoint completely
- **Firewall rules** - IP restrictions for admin access
- **Azure AD authentication** - RBAC for push/pull
- **Image scanning** - Vulnerability detection
- **Content trust** - Sign images with Notary

### Common Use Cases:
- ✅ **AKS integration** - Pull images from private network
- ✅ **CI/CD pipelines** - Build, scan, and deploy
- ✅ **Multi-region deployments** - Geo-replication
- ✅ **Artifact storage** - Helm charts, OCI artifacts

### Integration with AKS:
```bash
# AKS pulls from ACR using Managed Identity
Kubelet → queries ACR → Private Endpoint (10.2.x.x)
          ↓
          Uses AKS managed identity (RBAC: AcrPull)
```

**Benefits:**
- No image pull secrets needed
- Automatic authentication via managed identity
- All traffic stays in Azure backbone


### Azure Key Vault
**Centralized Secrets Management**

### What is Key Vault?
Managed service to securely store and access secrets, encryption keys, and certificates.

### Problems it Solves:
**Before Key Vault:**
- ❌ Secrets in code/config files
- ❌ Hardcoded passwords
- ❌ Keys in version control (Git leaks)
- ❌ No rotation policy
- ❌ No audit trail
- ❌ Manual certificate renewal

**With Key Vault:**
- ✅ Centralized secret storage
- ✅ Automatic secret rotation
- ✅ Access logging & monitoring
- ✅ RBAC & access policies
- ✅ HSM-backed keys (Premium SKU)
- ✅ Certificate lifecycle management

### Three Main Capabilities:
**1. Secrets Management**
```
API keys, passwords, connection strings
Max size: 25 KB
Versioning: Multiple versions per secret
```

**2. Key Management**
```
Encryption keys for Azure services
RSA, EC keys
HSM-protected (Premium SKU)
```

**3. Certificate Management**
```
TLS/SSL certificates
Auto-renewal integration
Import or generate in Key Vault
```

### Access Methods:
**1. Access Policies (Legacy):**
```
Principal: User/App/Managed Identity
Permissions: Get, List, Set, Delete
Scope: Entire Key Vault
```

**2. RBAC (Modern - Recommended):**
```yaml
Role: Key Vault Secrets Officer
Scope: Key Vault or specific secrets
Principal: Managed Identity
```

### Private Endpoint Integration:
**Public Access:**
```
VM → Internet → Key Vault (*.vault.azure.net)
```

**Private Endpoint:**
```
VM → VNet → Private Endpoint → Key Vault
      │
      └── Private DNS: mykv.vault.azure.net → 10.2.x.x
```

### Security Features:
- **Soft delete** - Recoverable deletion (7-90 days)
- **Purge protection** - Prevent permanent deletion
- **Network isolation** - Private endpoints + firewall
- **Logging** - Azure Monitor integration
- **Defender for Cloud** - Security recommendations

### Common Use Cases:
**1. VM SSH Keys:**
```
Store SSH public/private keys
VMs retrieve during deployment
No keys in version control
```

**2. Application Secrets:**
```
Database connection strings
API keys for external services
Retrieved via managed identity
```

**3. Certificate Management:**
```
TLS certificates for applications
Auto-renewal before expiration
Integration with App Gateway, App Services
```

### Integration Patterns:
**AKS + Key Vault:**
```
AKS Pod → CSI Driver → Key Vault (Private Endpoint)
          ↓
          Mount secrets as volumes
          or
          Environment variables
```

**VM + Key Vault:**
```
VM Managed Identity → RBAC Role → Key Vault
                      ↓
                      Retrieve secrets at runtime
```

### Cost Model:
- **Standard:** ~$0.03 per 10k operations
- **Premium:** ~$1.00/month per HSM-protected key
- **Secrets/Certificates:** $0.03 per 10k operations
- Very cost-effective for most workloads


### Private DNS Zones
**Name Resolution in Private Networks**

### What are Private DNS Zones?
Azure-managed DNS service providing name resolution within VNets without exposing DNS queries to the internet.

### Public vs Private DNS:
**Public DNS:**
```
vm.example.com → 20.1.2.3 (Public IP)
Anyone can resolve this
```

**Private DNS:**
```
vm.internal.local → 10.1.0.4 (Private IP)
Only VNets linked to zone can resolve
```

### Key Concepts:
**DNS Zone:**
- Container for DNS records
- Example: `contoso.internal`, `privatelink.azurecr.io`

**VNet Link:**
- Connects VNet to Private DNS Zone
- Auto-registration: Automatically create A records for VMs
- Resolution: VMs can query the zone

**Record Types:**
- **A Record:** Hostname → IPv4 (vm01 → 10.1.0.4)
- **CNAME:** Alias (www → webserver.contoso.internal)
- **PTR:** Reverse lookup (10.1.0.4 → vm01)

### Private Link DNS Integration:
When using Private Endpoints, Azure creates special DNS zones:

```
Service              Private DNS Zone
─────────────────────────────────────────────────
Storage (Blob)       privatelink.blob.core.windows.net
Key Vault            privatelink.vaultcore.azure.net
ACR                  privatelink.azurecr.io
SQL Database         privatelink.database.windows.net
Cosmos DB            privatelink.documents.azure.com
```

**DNS Resolution Flow:**
```
VM queries: myacr.azurecr.io
     ↓
Azure DNS (168.63.129.16)
     ↓
CNAME → myacr.privatelink.azurecr.io
     ↓
Private DNS Zone lookup
     ↓
A Record → 10.2.0.5 (Private Endpoint IP)
```

### Auto-Registration:
```yaml
Private DNS Zone: contoso.internal
VNet Link: spoke2-vnet
  - Auto-registration: ENABLED
  
Result:
  When VM created: A record auto-created
  When VM deleted: A record auto-removed
```

**Benefits:**
- ✅ No manual DNS record management
- ✅ Always up-to-date
- ✅ Works with VMSS (scale sets)


### DNS Resolver & Hybrid DNS
**Connecting On-Premises and Azure DNS**

### The Hybrid DNS Challenge:
**Scenario:**
- On-premises DNS: 192.168.1.10
- Azure Private DNS: contoso.internal
- Need bidirectional resolution

**Problem:**
- Azure VMs can't forward to on-prem DNS
- On-prem can't resolve Azure Private DNS zones
- VPN/ExpressRoute connects networks, but not DNS

### Azure Private DNS Resolver:
**Purpose:** Enable DNS resolution between Azure and on-premises networks

**Architecture:**
```
On-Premises                  Azure Hub VNet
─────────────────────────────────────────────────
DNS Server          →    Inbound Endpoint
(192.168.1.10)           (10.0.2.4)
                         │
                         DNS Resolver
                         │
Conditional Forwarder ← Outbound Endpoint
                         (10.0.3.4)
```

### Two Components:
**1. Inbound Endpoint:**
- **Purpose:** On-prem queries Azure Private DNS
- **Subnet:** Dedicated /28 minimum
- **IP Address:** Static, within subnet
- **Configuration:**
  ```
  On-prem DNS: Add conditional forwarder
  contoso.internal → 10.0.2.4
  ```

**2. Outbound Endpoint:**
- **Purpose:** Azure VMs query on-prem DNS
- **Subnet:** Dedicated /28 minimum
- **Ruleset:** Define forwarding rules
- **Configuration:**
  ```yaml
  Ruleset:
    - Domain: corp.local
      Target: 192.168.1.10 (on-prem DNS)
    - Domain: dev.corp.local
      Target: 192.168.1.11
  ```

### DNS Resolution Flow (Inbound):
```
On-Prem Client needs: vm01.contoso.internal
     ↓
On-Prem DNS Server (192.168.1.10)
     ↓
Conditional Forwarder → 10.0.2.4 (Inbound Endpoint)
     ↓
DNS Resolver queries Private DNS Zone
     ↓
Returns: 10.1.0.4
```

### DNS Resolution Flow (Outbound):
```
Azure VM needs: fileserver.corp.local
     ↓
Azure DNS (168.63.129.16)
     ↓
DNS Resolver Outbound Endpoint
     ↓
Forwarding Rule matches "corp.local"
     ↓
Forwards to: 192.168.1.10 (on-prem)
     ↓
Returns: 192.168.10.5
```

### Subnet Requirements:
- **Inbound Subnet:** /28 minimum (dedicated)
- **Outbound Subnet:** /28 minimum (dedicated)
- **Separate from other workloads**
- **NSG:** Recommended but optional

### Cost Model:
- **DNS Resolver:** ~$0.45/hour (~$325/month)
- **Inbound Endpoint:** Included
- **Outbound Endpoint:** Included
- **Queries:** $0.40 per million queries

### When to Use:
- ✅ Hybrid cloud with VPN/ExpressRoute
- ✅ Need DNS resolution both directions
- ✅ Multiple on-prem DNS servers
- ✅ Complex DNS hierarchies

### Alternative (Cheaper for Simple Scenarios):
**Custom DNS VMs:**
- Deploy BIND/Windows DNS in Azure
- Manually configure forwarders
- Cost: ~$50/month (VM + storage)
- Cons: Manual management, no HA


### Azure Policy
**Governance and Compliance Automation**

### What is Azure Policy?
Service to enforce organizational standards and compliance requirements through policy definitions and assignments.

### Why Azure Policy?
**Without Policy:**
- ❌ Manual compliance checks
- ❌ Inconsistent configurations
- ❌ Resources created without tags
- ❌ Wrong SKUs deployed (cost overruns)
- ❌ Security misconfigurations

**With Azure Policy:**
- ✅ Automatic compliance evaluation
- ✅ Prevent non-compliant deployments
- ✅ Auto-remediation of resources
- ✅ Compliance dashboards
- ✅ Audit trail for violations

### Key Concepts:
**Policy Definition:**
- What to evaluate (JSON rule)
- Effect: Audit, Deny, Modify, DeployIfNotExists

**Policy Assignment:**
- Where to apply (subscription, resource group, resource)
- Parameters (customizable values)

**Initiative (Policy Set):**
- Bundle of related policies
- Example: "CIS Azure Benchmark"

### Effects (Actions):
**1. Audit**
```yaml
Effect: Audit
Action: Log non-compliance, allow deployment
Use case: Visibility without enforcement
```

**2. Deny**
```yaml
Effect: Deny
Action: Block non-compliant deployment
Use case: Prevent violations (e.g., no public IPs)
```

**3. Modify**
```yaml
Effect: Modify
Action: Add/modify tags during deployment
Use case: Ensure all resources tagged
```

**4. DeployIfNotExists**
```yaml
Effect: DeployIfNotExists
Action: Auto-deploy missing resources
Use case: Ensure diagnostic settings exist
```

**5. AuditIfNotExists**
```yaml
Effect: AuditIfNotExists
Action: Check for existence, log if missing
Use case: Verify backup configured
```

### Common Policy Examples:
**1. Require Tags:**
```json
Policy: Require "Environment" tag on all resources
Effect: Deny
Result: Deployment fails without tag
```

**2. Allowed Locations:**
```json
Policy: Only allow "eastus" and "westus"
Effect: Deny
Result: Prevent deployment in other regions
```

**3. Allowed VM SKUs:**
```json
Policy: Only Standard_D2s_v3, Standard_D4s_v3
Effect: Deny
Result: Prevent expensive VM sizes
```

**4. Require Encryption:**
```json
Policy: Storage accounts must use HTTPS only
Effect: Deny
Result: Block storage without HTTPS
```

**5. Network Security:**
```json
Policy: Deny public IPs on VMs
Effect: Deny
Result: All VMs must use private IPs
```

### Policy Lifecycle:
```
1. Define → Create or use built-in policy
2. Assign → Apply to scope (subscription/RG)
3. Evaluate → Check existing resources
4. Remediate → Fix non-compliant resources
5. Monitor → Compliance dashboard
```

### Compliance Evaluation:
- **On-demand:** Manual scan
- **Automatic:** Every 24 hours
- **On deployment:** Real-time during create/update

### Remediation Tasks:
**For existing non-compliant resources:**
```yaml
Policy: Add "CostCenter" tag
Effect: Modify
Remediation: 
  - Create remediation task
  - Azure applies tag to existing resources
  - Uses managed identity
```

### Built-in Policies:
Azure provides 500+ built-in policies:
- **Security:** CIS benchmarks, Azure Security Benchmark
- **Cost:** Restrict VM/storage SKUs
- **Networking:** NSG rules, allowed protocols
- **Monitoring:** Diagnostic settings required
- **Backup:** Ensure backup configured

### Policy Hierarchy:
```
Management Group (Policy: Require tags)
     ├── Subscription A (Inherits + adds allowed locations)
     │    ├── RG Prod (Inherits all)
     │    └── RG Dev (Inherits all)
     └── Subscription B (Inherits only MG policies)
```

**Inheritance:**
- Policies assigned at higher scope apply to all children
- Cannot override parent policies (only add more)

### Cost Model:
- **Free** for first 20 policies
- No additional cost for built-in policies
- Cost applies for advanced scenarios (rare)

### When to Use:
- ✅ **Multi-team environments** - Enforce standards
- ✅ **Compliance requirements** - SOC2, PCI-DSS, HIPAA
- ✅ **Cost control** - Prevent expensive resources
- ✅ **Security baseline** - Ensure encryption, HTTPS
- ✅ **Tagging strategy** - Automated tag enforcement

### Integration with DevOps:
```yaml
Pipeline:
  - terraform plan
  - Policy evaluation (pre-deployment)
  - If compliant: deploy
  - If non-compliant: fail build
```


## Hands-On Guide


### Live Demo - Azure Portal
**What We'll Show**

1. **Resource Group** - All resources overview
2. **Virtual Networks** - Hub + Spoke topology
3. **VNet Peering** - Connectivity between VNets
4. **Network Security Groups** - Security rules
5. **Route Tables** - UDRs forcing to firewall
6. **Ubuntu NVA** - Firewall VM configuration
7. **AKS Cluster** - Kubernetes setup
8. **Monitoring** - Topology visualization

*[Switch to Azure Portal]*


### Cost Considerations
**Estimated Monthly Costs (Pay-as-you-go)**

| Resource | Size/SKU | Est. Cost |
|----------|----------|-----------|
| Virtual Networks | Hub + 2 Spokes | Free |
| VNet Peering | Data transfer | ~$10-50 |
| Ubuntu NVA | Standard_B2s | ~$30 |
| AKS Nodes | 3x Standard_D2s_v3 | ~$210 |
| Azure Bastion | Standard | ~$140 (optional) |
| Load Balancer | Standard | ~$20 |
| **Total** | | **~$270-410/month** |

**Cost Optimization Tips:**
- Use B-series VMs for dev/test
- Auto-shutdown for non-prod
- Reserved instances for production
- Spot instances for AKS (non-critical)


### Troubleshooting Tips
**Common Issues and Solutions**

### Deployment Failures:

**1. Authentication Error:**
```
Error: building account: getting authenticated object ID
```
**Solution:**
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

**2. Insufficient Quota:**
```
Error: exceeds the quota limit for VM cores
```
**Solution:** Request quota increase or use smaller VM size

**3. Subnet Too Small:**
```
Error: insufficient IP addresses in subnet
```
**Solution:** Plan larger subnet (/24 instead of /26)

### Network Connectivity Issues:

**4. Can't Reach Spoke from Another Spoke:**
```bash
# Check UDR is applied
az network route-table show -g devops-kt-rg -n spoke1-rt

# Check NVA IP forwarding enabled
az vm show -g devops-kt-rg -n nva-firewall --query "networkProfile.networkInterfaces[0].enableIpForwarding"

# SSH to NVA and check iptables
sudo iptables -L -v -n
```

**5. NSG Blocking Traffic:**
```bash
# Check NSG flow logs
az network watcher flow-log show -g NetworkWatcherRG -n nsg-flow-log

# Test connectivity
az network watcher test-connectivity -g RG --source-resource VM1 --dest-address 10.1.0.4 --dest-port 22
```

### Terraform Issues:

**6. State Lock:**
```
Error: acquiring the state lock
```
**Solution:**
```bash
terraform force-unlock LOCK_ID
# Or wait for lock to expire
```

**7. State Drift:**
```
Error: resource exists but not in state
```
**Solution:**
```bash
terraform import azurerm_virtual_network.hub /subscriptions/.../hub-vnet
```

### Debugging Tools:
```bash
# Azure Network Watcher
az network watcher test-connectivity
az network watcher packet-capture

# On NVA firewall
sudo tcpdump -i any -n icmp
sudo iptables -L -v -n  # List rules with counters
sudo tail -f /var/log/syslog  # Watch firewall logs

# Terraform debugging
export TF_LOG=DEBUG
terraform apply
```


### Next Steps & Roadmap
**Future Enhancements**

**Short Term:**
1. Add Azure Monitor & Log Analytics
2. Implement Azure Policy for governance
3. Add Application Gateway for web apps
4. Configure backup & disaster recovery

**Medium Term:**
1. High availability NVA (active-passive)
2. Azure Firewall option for comparison
3. VPN Gateway for hybrid connectivity
4. ExpressRoute for private connections

**Long Term:**
1. Multi-region deployment
2. Azure Front Door for global load balancing
3. Advanced threat protection
4. Full GitOps implementation


### Best Practices Learned
**Key Takeaways**

✅ **Always use Infrastructure as Code**
- Version control everything
- Repeatable, testable deployments

✅ **Security from Day One**
- Never commit secrets to Git
- Implement least-privilege access
- Use NSGs on every subnet

✅ **Plan IP addressing carefully**
- Non-overlapping ranges
- Room for growth
- Document everything

✅ **Test before production**
- Use `terraform plan` religiously
- Validate in dev environment first


### Hands-On Lab Ideas
**Practice Exercises**

### Beginner Level:
1. **Add Spoke3 VNet**
   - Define in vnets.yaml
   - CIDR: 10.3.0.0/16
   - Deploy with terraform apply

2. **Update NSG Rule**
   - Add your home IP to allowed_ssh_ips
   - Verify access from new IP

3. **Scale AKS**
   - Change node count in aks.yaml
   - Apply and observe scaling

### Intermediate Level:
4. **Deploy Management VM**
   - Copy examples/mgmt-vm.tf
   - Deploy in Spoke2
   - Access via Bastion

5. **Custom iptables Rules**
   - SSH to NVA firewall
   - Add custom FORWARD rule
   - Test traffic blocking

6. **Network Troubleshooting**
   - Simulate connectivity issue
   - Use Network Watcher
   - Fix and validate

### Advanced Level:
7. **Implement HA Firewall**
   - Deploy second NVA
   - Add load balancer
   - Test failover

8. **Multi-Region Deployment**
   - Replicate to second region
   - Setup VNet peering between regions
   - Global routing

9. **CI/CD Pipeline**
   - GitHub Actions for terraform
   - Automated plan on PR
   - Auto-apply on merge


### Resources & Documentation
**Where to Learn More**

**Project Documentation:**
- `README.md` - Getting started guide
- `diagrams/architecture.md` - Full architecture details
- Module READMEs - Component-specific docs

**Microsoft Azure:**
- Azure Architecture Center
- Well-Architected Framework
- Hub-Spoke reference architecture

**Terraform:**
- AzureRM Provider documentation
- Terraform Registry (modules)
- Best practices guide

**This Repository:**
- GitHub: [your-repo-url]
- Issues & contributions welcome!


### Q&A
**Questions?**

**Common Questions:**
- Why Ubuntu NVA instead of Azure Firewall?
- Can we add more spokes?
- How to handle multi-region?
- What about disaster recovery?
- Integration with on-premises?

**Contact:**
- Email: [REDACTED]
- GitHub: [your-github]

---

## Appendix: Presentation Guide

This document can be used as both a standalone technical guide and as presentation material.

### Timing Recommendations

**Full Session (~95 minutes):**
- Networking Fundamentals: 15 minutes
- Architecture Deep Dive: 35 minutes
- Optional Components: 25 minutes
- Hands-On & Demo: 20 minutes

**Condensed Version (~70 minutes):**
- Skip Optional Components section
- Focus on Networking Fundamentals, Architecture Deep Dive, and Hands-On Guide

**Quick Overview (~45 minutes):**
- Skip deep theory subsections
- Skip Optional Components entirely
- Abbreviated demo (10 minutes)

### Audience Adaptation

**For Infrastructure Engineers:**
- Emphasize networking theory, routing, NSGs
- Deep dive into UDRs and traffic flows
- Focus on operational aspects

**For DevOps Engineers:**
- Highlight automation and IaC patterns
- Emphasize CI/CD integration points
- Focus on AKS deployment and management

**For Security Teams:**
- Emphasize defense-in-depth principles
- Detail NSG rules and firewall configuration
- Focus on compliance and audit capabilities

### Key Concepts to Emphasize

1. Hub-spoke provides centralized control with isolated workloads
2. UDRs force all traffic through inspection point (NVA)
3. Defense-in-depth requires multiple security layers
4. Infrastructure as Code makes systems reproducible
5. Proper IP planning is critical for scalability

### Additional Resources

- [Azure Portal Walkthrough](azure-portal-walkthrough.md) - Step-by-step demo guide
- [Architecture Diagram](architecture.md) - Visual reference with Mermaid diagrams
- Terraform code in `../terraform/` directory
- Configuration files in `../terraform/config/` directory
