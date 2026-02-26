# Kubernetes Basics
## DevOps Knowledge Transfer – Session 7

**Author:** [REDACTED]  
**Date:** February 2026  
**Audience:** Infrastructure Engineers  
**Duration:** ~2 hours  
**Level:** Beginner to Intermediate  
**Pre-requisites:** Docker Fundamentals (Session 6), Azure Portal (Session 2), Terraform (Session 3)

---

## Agenda

| # | Topic | Time | Style |
|---|-------|------|-------|
| 1 | Recap & Context: From Containers to Orchestration | 10 min | Discussion |
| 2 | Kubernetes Theory – Why K8s? Pros & Cons | 10 min | Slides |
| 3 | K8s Infrastructure – Control Plane, Workers, etcd | 15 min | Slides + Diagrams |
| 4 | Kubernetes Internal Resources | 15 min | Slides + Diagrams |
| 5 | K8s Offerings – Cloud, On-Prem, OpenShift | 5 min | Slides |
| — | **Break** | **5 min** | |
| 6 | kubectl – Installation & Basic Commands | 15 min | Live Demo |
| 7 | Kubernetes Manifests – Writing YAML | 15 min | Live Demo |
| 8 | kubectl Troubleshooting | 10 min | Live Demo |
| 9 | KubeLens – Visual Cluster Management | 5 min | Live Demo |
| 10 | AKS in Azure – Architecture & Components | 10 min | Screen Share |
| 11 | Q&A + Next Session Preview | 5 min | Discussion |

---

## Recap: Previous Sessions

| Session | Topics Covered |
|---------|----------------|
| Session 1 | DevOps Theory, Culture, Principles |
| Session 2 | Azure Portal GUI, Resource Management |
| Session 3 | IaC – Terraform |
| Session 4 | Git & CI/CD Pipelines |
| Session 5 | Ansible – Configuration Management |
| Session 6 | Docker Fundamentals, ACR |
| **Session 7** | **Kubernetes Basics** ← _Today_ |
| Session 8+ | _Helm, Flux, GitOps (coming next)_ |

---

## What We Built So Far

```
Session 2-3: Azure Infrastructure (Portal + Terraform)
  └── Hub-Spoke Network, VMs, NSGs, Subnets

Session 4: Git & Pipelines
  └── Code versioned, CI/CD automated

Session 5: Ansible
  └── Configuration management on VMs

Session 6: Docker
  └── Containerised our vacation-tracker app, pushed to ACR

Session 7 (Today): Kubernetes
  └── Orchestrate containers at scale on AKS
```

> _Last session we learned how to build and ship containers. Today we learn how to **run them in production**._

---

# PART 1: WHY KUBERNETES?

---

## The Problem: Running Containers at Scale

With Docker, you can run containers on a single host. But in production:

```
Single Docker Host                    Production Reality
┌──────────────────┐                 ┌──────────────────────────────────┐
│  ┌────┐ ┌────┐   │                 │  • 50+ containers                │
│  │App │ │ DB │   │                 │  • Multiple hosts                │
│  └────┘ └────┘   │                 │  • Auto-restart on failure       │
│                   │                 │  • Scale up/down dynamically     │
│  docker run ...   │                 │  • Load balancing                │
│                   │                 │  • Rolling updates, zero downtime│
│  Works for dev ✅ │                 │  • Secret management             │
│  Works for prod ❌│                 │  • Networking between containers │
└──────────────────┘                 └──────────────────────────────────┘
```

**Questions Docker alone can't answer:**
- What happens when a container crashes at 3 AM?
- How do I run 10 instances of my app across 5 servers?
- How do I update my app without downtime?
- How do containers on different hosts talk to each other?
- How do I manage secrets and configs across environments?

---

## The Solution: Container Orchestration

```
                    ┌──────────────────────────┐
                    │   Container Orchestrator   │
                    │   (Kubernetes)             │
                    └─────────┬────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
        │  Node 1    │  │  Node 2    │  │  Node 3    │
        │ ┌──┐ ┌──┐  │  │ ┌──┐ ┌──┐  │  │ ┌──┐ ┌──┐  │
        │ │C1│ │C2│  │  │ │C3│ │C4│  │  │ │C5│ │C6│  │
        │ └──┘ └──┘  │  │ └──┘ └──┘  │  │ └──┘ └──┘  │
        └───────────┘  └───────────┘  └───────────┘
```

A **container orchestrator** automates:
- **Scheduling:** Which container runs on which node
- **Scaling:** Add/remove container instances based on demand
- **Healing:** Restart failed containers automatically
- **Networking:** Service discovery and load balancing
- **Updates:** Rolling deployments with zero downtime
- **Configuration:** Centralized config and secrets management

---

## What Is Kubernetes?

- **Open-source container orchestration platform**
- Originally designed by **Google** (based on internal system called "Borg")
- Donated to **CNCF** (Cloud Native Computing Foundation) in 2015
- Written in **Go**
- Name means **"helmsman"** or **"pilot"** in Greek (κυβερνήτης)
- **K8s** = K + 8 letters + s (like i18n for internationalization)
- Current version: **1.32** (as of Feb 2026)

> _"Kubernetes is the operating system for the cloud."_

---

## Kubernetes: Pros & Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| **Self-healing** – auto-restarts failed containers | **Steep learning curve** – many concepts to learn |
| **Auto-scaling** – horizontal pod & cluster autoscaler | **Complexity** – overkill for simple applications |
| **Declarative** – describe desired state, K8s maintains it | **Resource overhead** – control plane uses compute/memory |
| **Portable** – runs on any cloud or on-prem | **Networking complexity** – CNI plugins, service mesh |
| **Ecosystem** – massive community, tooling, and integrations | **Security surface** – RBAC, network policies, pod security |
| **Rolling updates** – zero-downtime deployments | **Debugging** – distributed systems are harder to troubleshoot |
| **Service discovery** – built-in DNS and load balancing | **Cost** – managed K8s services come with management fees |
| **Secret management** – native handling of sensitive data | **Stateful workloads** – databases in K8s require extra care |

### When to Use Kubernetes

| ✅ Good Fit | ❌ Not the Best Fit |
|-------------|---------------------|
| Microservices architecture | Single monolithic app |
| Teams deploying frequently | Small projects with 1-2 services |
| Need for auto-scaling | Static workloads with no scaling needs |
| Multi-cloud / hybrid-cloud strategy | Budget-constrained simple deployments |
| Containerized CI/CD workflows | Legacy apps that can't be containerized |

> **Key Insight for Infra Engineers:** Kubernetes doesn't replace your infrastructure knowledge — it builds on top of it. Understanding networking, DNS, storage and compute is **essential** to running K8s well.

---

# PART 2: KUBERNETES INFRASTRUCTURE

---

## Cluster Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES CLUSTER                                │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │         CONTROL PLANE            │  │          WORKER NODES            │ │
│  │                                  │  │                                  │ │
│  │  ┌────────────────────────────┐  │  │  ┌────────────┐ ┌────────────┐  │ │
│  │  │      API Server            │  │  │  │  Node 1    │ │  Node 2    │  │ │
│  │  │  (kube-apiserver)          │◄─┼──┼─►│            │ │            │  │ │
│  │  └────────────────────────────┘  │  │  │ ┌────────┐ │ │ ┌────────┐ │  │ │
│  │                                  │  │  │ │kubelet │ │ │ │kubelet │ │  │ │
│  │  ┌────────────────────────────┐  │  │  │ ├────────┤ │ │ ├────────┤ │  │ │
│  │  │      Scheduler             │  │  │  │ │kube-   │ │ │ │kube-   │ │  │ │
│  │  │  (kube-scheduler)          │  │  │  │ │proxy   │ │ │ │proxy   │ │  │ │
│  │  └────────────────────────────┘  │  │  │ ├────────┤ │ │ ├────────┤ │  │ │
│  │                                  │  │  │ │container│ │ │ │container│ │  │ │
│  │  ┌────────────────────────────┐  │  │  │ │runtime │ │ │ │runtime │ │  │ │
│  │  │   Controller Manager       │  │  │  │ └────────┘ │ │ └────────┘ │  │ │
│  │  │  (kube-controller-manager) │  │  │  │            │ │            │  │ │
│  │  └────────────────────────────┘  │  │  │ ┌──┐ ┌──┐  │ │ ┌──┐ ┌──┐  │  │ │
│  │                                  │  │  │ │P1│ │P2│  │ │ │P3│ │P4│  │  │ │
│  │  ┌────────────────────────────┐  │  │  │ └──┘ └──┘  │ │ └──┘ └──┘  │  │ │
│  │  │           etcd             │  │  │  └────────────┘ └────────────┘  │ │
│  │  │  (cluster state store)     │  │  │                                  │ │
│  │  └────────────────────────────┘  │  └──────────────────────────────────┘ │
│  └──────────────────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Control Plane Components

The **control plane** is the brain of the cluster. It makes global decisions (scheduling, detecting and responding to events).

| Component | Role | Analogy |
|-----------|------|---------|
| **kube-apiserver** | Front door to the cluster – all communication goes through it | Reception desk |
| **etcd** | Key-value store – stores ALL cluster state and config | The filing cabinet |
| **kube-scheduler** | Decides which node a new pod runs on (based on resources, constraints) | Dispatcher / traffic controller |
| **kube-controller-manager** | Runs controllers (ReplicaSet, Node, Job, etc.) that watch and reconcile state | Supervisors watching the floor |
| **cloud-controller-manager** | Integrates with cloud provider APIs (load balancers, storage, nodes) | Cloud liaison officer |

### How They Work Together

```
 kubectl apply -f deployment.yaml
         │
         ▼
  ┌──────────────┐     stores desired state     ┌──────────┐
  │  API Server   │ ──────────────────────────►  │   etcd   │
  └──────┬───────┘                               └──────────┘
         │
         │  notifies
         ▼
  ┌──────────────┐     "this pod needs a node"   ┌──────────────┐
  │  Scheduler    │ ────────────────────────────► │   API Server  │
  └──────────────┘     (assigns node)            └──────┬───────┘
                                                        │
                                                        │  instructs
                                                        ▼
                                                 ┌──────────────┐
                                                 │   kubelet     │
                                                 │  (on node)    │
                                                 │  starts pod   │
                                                 └──────────────┘
```

> **For Infra Engineers:** In managed K8s (AKS, EKS, GKE), the control plane is managed **by the cloud provider**. You don't SSH into control plane nodes. You only manage worker nodes.

---

## Worker Node Components

Each **worker node** runs your actual containerized workloads.

| Component | Role | Analogy |
|-----------|------|---------|
| **kubelet** | Agent on each node – receives instructions from API server, manages pods | The on-site foreman |
| **kube-proxy** | Network proxy – handles routing, load balancing for Services | Network switch on the node |
| **Container Runtime** | Actually runs the containers (containerd, CRI-O) | The engine that starts containers |

```
┌───────────────────────────────────────┐
│              Worker Node              │
│                                       │
│  kubelet ◄──── API Server             │
│    │                                  │
│    ├── Pod A (nginx:latest)           │
│    │     └── Container 1              │
│    ├── Pod B (app:v2)                 │
│    │     ├── Container 1 (app)        │
│    │     └── Container 2 (sidecar)    │
│    └── Pod C (redis:7)               │
│          └── Container 1              │
│                                       │
│  kube-proxy ──── iptables/IPVS rules  │
│                                       │
│  containerd ──── actually runs        │
│                  containers (OCI)     │
└───────────────────────────────────────┘
```

---

## Ingress – Exposing Services Externally

```
          Internet
             │
             ▼
    ┌─────────────────┐
    │  Load Balancer   │     (Azure LB, AWS ALB, etc.)
    │  (L4 / L7)       │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Ingress         │     L7 routing (host/path-based)
    │  Controller      │     (NGINX, Traefik, Azure App GW)
    │                  │
    │  Rules:          │
    │  /api → svc-api  │
    │  /web → svc-web  │
    └────────┬────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
  ┌─────────┐ ┌─────────┐
  │ svc-api │ │ svc-web │    (Kubernetes Services)
  │ :8080   │ │ :3000   │
  └────┬────┘ └────┬────┘
       │           │
    ┌──┴──┐     ┌──┴──┐
    │Pods │     │Pods │      (Application Pods)
    └─────┘     └─────┘
```

| Concept | What It Does | Layer |
|---------|-------------|-------|
| **Service (ClusterIP)** | Internal load balancer within the cluster | L4 |
| **Service (NodePort)** | Exposes service on each node's IP at a static port | L4 |
| **Service (LoadBalancer)** | Provisions an external cloud load balancer | L4 |
| **Ingress** | HTTP/HTTPS routing based on host/path rules | L7 |
| **Ingress Controller** | The actual proxy that implements Ingress rules (NGINX, Traefik) | L7 |

> **For Infra Engineers:** Think of **Services** as internal VIPs and **Ingress** as your reverse proxy / application gateway. If you've configured NGINX or F5 before, the Ingress concept will feel familiar.

---

# PART 3: KUBERNETES INTERNAL RESOURCES

---

## Resource Hierarchy

```
Cluster
  └── Namespace (logical isolation)
        ├── Pod (smallest deployable unit)
        ├── Deployment (manages ReplicaSets → Pods)
        ├── Service (stable network endpoint)
        ├── ConfigMap (configuration data)
        ├── Secret (sensitive data)
        ├── Ingress (HTTP routing rules)
        ├── PersistentVolumeClaim (storage request)
        ├── Job / CronJob (batch tasks)
        └── NetworkPolicy (firewall rules)
```

---

## Namespaces – Logical Isolation

Namespaces partition a cluster into virtual sub-clusters.

```
┌─────────────────────────────────────────────────────┐
│                   K8s Cluster                        │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  default     │  │ production  │  │  staging    │ │
│  │             │  │             │  │             │ │
│  │ dev-app     │  │ api-deploy  │  │ api-deploy  │ │
│  │ test-pod    │  │ web-deploy  │  │ web-deploy  │ │
│  │             │  │ db-deploy   │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │ kube-system │  │ monitoring  │                   │
│  │             │  │             │                   │
│  │ coredns     │  │ prometheus  │                   │
│  │ kube-proxy  │  │ grafana     │                   │
│  └─────────────┘  └─────────────┘                   │
└─────────────────────────────────────────────────────┘
```

**Default namespaces in every cluster:**

| Namespace | Purpose |
|-----------|---------|
| `default` | Where resources go when no namespace is specified |
| `kube-system` | Kubernetes system components (DNS, proxy, etc.) |
| `kube-public` | Publicly accessible data (rarely used) |
| `kube-node-lease` | Node heartbeat data |

```bash
# List namespaces
kubectl get namespaces

# Create a namespace
kubectl create namespace staging

# Set default namespace for your context
kubectl config set-context --current --namespace=staging
```

> **For Infra Engineers:** Namespaces are like VLANs for your cluster — they provide logical separation. In production, use them to isolate environments, teams, or applications.

---

## Pods – The Smallest Deployable Unit

A **Pod** is one or more containers that share network and storage. It is the atomic unit in Kubernetes.

```
┌──────────────────────────────────┐
│            Pod                   │
│                                  │
│  ┌────────────┐  ┌────────────┐  │
│  │ Container 1│  │ Container 2│  │     ← Sidecar pattern
│  │   (app)    │  │  (logger)  │  │
│  └─────┬──────┘  └─────┬──────┘  │
│        │               │         │
│        └───────┬───────┘         │
│                │                 │
│  Shared: localhost network       │
│  Shared: volumes                 │
│  Shared: IP address              │
│                                  │
│  IP: 10.244.1.5                  │
└──────────────────────────────────┘
```

**Key facts:**
- Pods are **ephemeral** — they can be created and destroyed at any time
- Pods get a **unique IP address** within the cluster
- Containers within a pod communicate via `localhost`
- You rarely create pods directly — you use **Deployments** instead
- When a pod dies, it is NOT restarted — a NEW pod is created

---

## Deployments – Managing Pods at Scale

A **Deployment** manages a set of identical Pods through a **ReplicaSet**.

```
Deployment (desired: 3 replicas)
  │
  └── ReplicaSet (current: 3 replicas)
        ├── Pod 1 (app:v2)  ── Running on Node 1
        ├── Pod 2 (app:v2)  ── Running on Node 2
        └── Pod 3 (app:v2)  ── Running on Node 1
```

**What a Deployment gives you:**
- **Replica management** – ensures N pods are always running
- **Rolling updates** – gradually replace old pods with new ones
- **Rollback** – revert to a previous version
- **Self-healing** – if a pod dies, a new one is created automatically

### Rolling Update (Zero-Downtime)

```
Step 1: Current state (all v1)
  [Pod v1] [Pod v1] [Pod v1]

Step 2: New pod created with v2
  [Pod v1] [Pod v1] [Pod v1] [Pod v2] ← new

Step 3: Old pod terminated
  [Pod v1] [Pod v1] [Pod v2]

Step 4: Repeat...
  [Pod v1] [Pod v2] [Pod v2]

Step 5: Complete
  [Pod v2] [Pod v2] [Pod v2]
```

---

## Services – Stable Network Endpoints

Pods are ephemeral — their IPs change. A **Service** provides a stable DNS name and IP for a group of pods.

```
                                      ┌─────────────────┐
 Internal traffic ──────────────────► │   Service        │
 (api-service.production.svc)         │   ClusterIP:     │
                                      │   10.0.100.50    │
                                      └────────┬────────┘
                                               │
                                    ┌──────────┼──────────┐
                                    │          │          │
                               ┌────┴───┐ ┌───┴────┐ ┌───┴────┐
                               │ Pod 1  │ │ Pod 2  │ │ Pod 3  │
                               │10.244. │ │10.244. │ │10.244. │
                               │1.10    │ │2.15    │ │1.22    │
                               └────────┘ └────────┘ └────────┘
```

**Service Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| **ClusterIP** (default) | Internal cluster IP only | Service-to-service communication |
| **NodePort** | Exposes on each node's IP at a static port (30000-32767) | Development, testing |
| **LoadBalancer** | Provisions an external load balancer (cloud only) | External production traffic |
| **ExternalName** | Maps to a DNS name (CNAME record) | Accessing external services |

```
  ClusterIP           NodePort              LoadBalancer
  (internal)          (dev/test)            (production)

  ┌────────┐      ┌────────────────┐     ┌──────────────────┐
  │Cluster │      │ Node IP:30080  │     │  External LB     │
  │only    │      │   ↓            │     │  (20.10.5.100)   │
  │        │      │ ClusterIP      │     │    ↓              │
  └────────┘      └────────────────┘     │  NodePort         │
                                         │    ↓              │
                                         │  ClusterIP        │
                                         └──────────────────┘
```

> **For Infra Engineers:** Services are like virtual IPs (VIPs) in traditional load balancer setups. `ClusterIP` ≈ internal VIP, `LoadBalancer` ≈ external VIP with a public IP from Azure.

---

## ConfigMaps and Secrets

### ConfigMaps – Non-Sensitive Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  DATABASE_HOST: "postgres.production.svc"
  DATABASE_PORT: "5432"
  LOG_LEVEL: "info"
  APP_MODE: "production"
```

### Secrets – Sensitive Data (base64 encoded)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  DATABASE_PASSWORD: cGFzc3dvcmQxMjM=      # base64 of "password123"
  API_KEY: c3VwZXItc2VjcmV0LWtleQ==         # base64 of "super-secret-key"
```

**How to use them in pods:**

```yaml
# As environment variables
env:
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: DATABASE_HOST
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: DATABASE_PASSWORD

# As mounted volumes
volumes:
  - name: config-volume
    configMap:
      name: app-config
```

> **⚠️ Important:** Kubernetes Secrets are only base64, **not encrypted** by default. For production, integrate with external secret stores like **Azure Key Vault**, HashiCorp Vault, or use **Sealed Secrets**. We will use Key Vault in our AKS setup.

---

## Kubernetes Networking Model

```
┌───────────────────────────────────────────────────────────────────┐
│                    Kubernetes Network                             │
│                                                                   │
│  Rule 1: Every pod gets its own unique IP address                │
│  Rule 2: Pods on any node can communicate with any other pod     │
│  Rule 3: No NAT – the IP a pod sees for itself is the same      │
│          IP others use to reach it                               │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐               │
│  │     Node 1        │         │     Node 2        │               │
│  │  ┌────┐  ┌────┐   │  CNI    │  ┌────┐  ┌────┐   │               │
│  │  │Pod │  │Pod │   │ overlay │  │Pod │  │Pod │   │               │
│  │  │.1.5│  │.1.6│   │◄──────►│  │.2.8│  │.2.9│   │               │
│  │  └────┘  └────┘   │  (VXLAN │  └────┘  └────┘   │               │
│  │   10.244.1.0/24   │  or BGP)│   10.244.2.0/24   │               │
│  └──────────────────┘         └──────────────────┘               │
│                                                                   │
│  Service Network: 10.0.0.0/16 (virtual IPs, no real interfaces) │
│  Pod Network:     10.244.0.0/16 (CNI-managed)                   │
│  DNS:             coredns (*.svc.cluster.local)                  │
└───────────────────────────────────────────────────────────────────┘
```

**CNI Plugins** (Container Network Interface) – the networking layer:

| Plugin | Used By | Notes |
|--------|---------|-------|
| **Azure CNI** | AKS | Pods get IPs from Azure VNet subnet |
| **Calico** | Many platforms | Network policies, BGP routing |
| **Flannel** | Simple clusters | VXLAN overlay, easy setup |
| **Cilium** | Advanced setups | eBPF-based, high performance |

> **For Infra Engineers:** In AKS with Azure CNI, pods get real Azure VNet IPs from your subnet. This means pods are directly routable from your hub-spoke network — no overlay magic needed. Plan your IP space accordingly!

---

# PART 4: KUBERNETES OFFERINGS

---

## Where Can You Run Kubernetes?

```
                        Kubernetes
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      Managed          Self-Managed     Platform
      (Cloud)          (On-Prem)        (Opinionated)
           │               │               │
     ┌─────┼─────┐    ┌───┼───┐       ┌───┼───┐
     │     │     │    │   │   │       │   │   │
    AKS   EKS   GKE  kubeadm  k3s  OpenShift Tanzu Rancher
  (Azure)(AWS)(GCP)
```

| Category | Service | Provider | Notes |
|----------|---------|----------|-------|
| **Managed Cloud** | **AKS** | Azure | Free control plane, pay for worker nodes |
| | EKS | AWS | $0.10/hr for control plane + worker nodes |
| | GKE | Google | Autopilot mode available |
| **Self-Managed** | kubeadm | Any | Official K8s installer, full control |
| | k3s | Any | Lightweight K8s (IoT, edge, dev) |
| | minikube | Local | Single-node K8s for local dev |
| | kind | Local | K8s IN Docker (for CI/CD testing) |
| **Platform** | OpenShift | Red Hat | Enterprise K8s + developer tools + security |
| | Tanzu | VMware | K8s on vSphere |
| | Rancher | SUSE | Multi-cluster K8s management |

### Key Differences for Decision Making

| Concern | Managed (AKS) | Self-Managed | OpenShift |
|---------|---------------|-------------|-----------|
| **Control plane management** | Cloud provider | You | You or managed |
| **Upgrades** | Assisted | Manual | Assisted |
| **Cost** | Worker nodes + services | Infrastructure + ops team | License + infrastructure |
| **Customization** | Limited (but sufficient) | Full | Moderate |
| **Support** | Cloud provider SLA | Community / vendor | Red Hat support |
| **Best for** | Cloud-native teams | Hardcore infra teams | Enterprise with compliance needs |

> **For Infra Engineers:** In our project, we use **AKS** (Azure Kubernetes Service). The control plane is free and managed by Microsoft. We only pay for the virtual machine scale sets that run our worker nodes.

---

# PART 5: kubectl – THE K8s COMMAND LINE

---

## What Is kubectl?

- **CLI tool** to interact with Kubernetes clusters
- Communicates with the **API Server** via REST API
- Reads cluster connection info from **kubeconfig** (`~/.kube/config`)
- Pronounced: "kube-control", "kube-cuddle", or "kube-C-T-L" (community debates endlessly)

```
┌──────────┐     HTTPS/REST     ┌──────────────┐      ┌──────────┐
│ kubectl   │ ─────────────────► │  API Server   │ ───► │  Cluster │
│ (your PC) │                    │  (K8s)        │      │  State   │
└──────────┘                    └──────────────┘      └──────────┘
      │
      └── reads ~/.kube/config
            (server URL, certificate, token)
```

---

## Installation

```bash
# Linux (Ubuntu/Debian)
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS (with Homebrew)
brew install kubectl

# Windows (with Chocolatey)
choco install kubernetes-cli

# Verify installation
kubectl version --client

# Azure: Get AKS credentials (merges into kubeconfig)
az aks get-credentials --resource-group myRG --name myAKS
```

---

## Essential kubectl Commands

### Cluster Info & Context

```bash
# View cluster info
kubectl cluster-info

# View the kubeconfig
kubectl config view

# List available contexts (clusters you can connect to)
kubectl config get-contexts

# Switch context (if you have multiple clusters)
kubectl config use-context myAKS

# Set default namespace
kubectl config set-context --current --namespace=production
```

### GET – Viewing Resources

```bash
# List all pods in current namespace
kubectl get pods

# List all pods in all namespaces
kubectl get pods -A

# List pods with more details
kubectl get pods -o wide

# List other resource types
kubectl get deployments
kubectl get services
kubectl get nodes
kubectl get namespaces
kubectl get configmaps
kubectl get secrets
kubectl get ingress

# List everything in a namespace
kubectl get all -n production

# Output as YAML (great for learning what K8s stores)
kubectl get deployment my-app -o yaml

# Output as JSON
kubectl get pod my-pod -o json
```

### DESCRIBE – Detailed Information

```bash
# Detailed info about a pod (events, conditions, volumes)
kubectl describe pod my-pod

# Detailed info about a node
kubectl describe node aks-nodepool1-12345678-vmss000000

# Detailed info about a service
kubectl describe service my-service
```

### CREATE & APPLY – Creating Resources

```bash
# Apply resources from a YAML file (declarative – recommended)
kubectl apply -f deployment.yaml

# Apply all YAML files in a directory
kubectl apply -f ./manifests/

# Create resources imperatively (quick, but not reproducible)
kubectl create namespace staging
kubectl create deployment nginx --image=nginx:latest --replicas=3
```

### DELETE – Removing Resources

```bash
# Delete a specific resource
kubectl delete pod my-pod
kubectl delete deployment my-app

# Delete resources defined in a YAML
kubectl delete -f deployment.yaml

# Delete all pods in a namespace (careful!)
kubectl delete pods --all -n staging

# Force delete a stuck pod
kubectl delete pod my-pod --grace-period=0 --force
```

### LOGS – Viewing Container Output

```bash
# View logs from a pod
kubectl logs my-pod

# Follow logs in real-time (like tail -f)
kubectl logs my-pod -f

# View logs from a specific container in a multi-container pod
kubectl logs my-pod -c sidecar

# View logs from the previous instance of a pod (if it crashed)
kubectl logs my-pod --previous

# View the last 50 lines
kubectl logs my-pod --tail=50
```

### EXEC – Running Commands in Containers

```bash
# Open a shell inside a running container
kubectl exec -it my-pod -- /bin/bash

# Run a single command
kubectl exec my-pod -- cat /etc/hostname

# Exec into a specific container in a multi-container pod
kubectl exec -it my-pod -c app-container -- /bin/sh
```

### SCALE – Adjusting Replicas

```bash
# Scale a deployment to 5 replicas
kubectl scale deployment my-app --replicas=5

# Scale to zero (stop all pods but keep the deployment)
kubectl scale deployment my-app --replicas=0
```

---

## kubectl Cheat Sheet

| Task | Command |
|------|---------|
| View pods | `kubectl get pods` |
| View pod details | `kubectl describe pod <name>` |
| View logs | `kubectl logs <pod>` |
| Follow logs | `kubectl logs <pod> -f` |
| Enter a pod | `kubectl exec -it <pod> -- /bin/bash` |
| Apply manifest | `kubectl apply -f file.yaml` |
| Delete resource | `kubectl delete -f file.yaml` |
| Scale deployment | `kubectl scale deployment <name> --replicas=N` |
| View all resources | `kubectl get all -A` |
| Port forward | `kubectl port-forward svc/my-svc 8080:80` |
| Copy file to pod | `kubectl cp file.txt my-pod:/tmp/file.txt` |
| View events | `kubectl get events --sort-by='.lastTimestamp'` |
| Dry-run test | `kubectl apply -f file.yaml --dry-run=client` |
| Diff before apply | `kubectl diff -f file.yaml` |
| View resource usage | `kubectl top pods` / `kubectl top nodes` |

---

# PART 6: KUBERNETES MANIFESTS

---

## What Is a Manifest?

A Kubernetes manifest is a **YAML file** that declares the desired state of a resource. K8s will then work to make reality match that declaration.

### Structure of Every Manifest

```yaml
apiVersion: <API group/version>    # Which API to use
kind: <Resource type>              # What resource to create
metadata:                          # Identity information
  name: <resource-name>
  namespace: <namespace>
  labels:                          # Key-value pairs for grouping/selection
    app: my-app
    environment: production
spec:                              # The desired state (resource-specific)
  ...
```

> **For Infra Engineers:** Think of manifests like Terraform `.tf` files — you declare what you want, and the system makes it happen. The difference: Terraform talks to cloud APIs, K8s manifests talk to the K8s API Server.

---

## Manifest Example: Full Application Stack

### 1. Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vacation-tracker
  labels:
    app: vacation-tracker
    environment: production
```

### 2. ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: vacation-tracker
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
```

### 3. Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: vacation-tracker
type: Opaque
data:
  DATABASE_PASSWORD: cGFzc3dvcmQxMjM=
  SESSION_KEY: bXktc2VjcmV0LXNlc3Npb24ta2V5
```

### 4. Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vacation-tracker
  namespace: vacation-tracker
  labels:
    app: vacation-tracker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vacation-tracker
  template:
    metadata:
      labels:
        app: vacation-tracker
    spec:
      containers:
        - name: app
          image: myacr.azurecr.io/vacation-tracker:v1.0
          ports:
            - containerPort: 5000
          envFrom:
            - configMapRef:
                name: app-config
          env:
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: DATABASE_PASSWORD
          resources:
            requests:
              cpu: "100m"          # 0.1 CPU cores
              memory: "128Mi"      # 128 MB RAM
            limits:
              cpu: "500m"          # 0.5 CPU cores max
              memory: "256Mi"      # 256 MB RAM max
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 15
            periodSeconds: 20
```

### 5. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: vacation-tracker-service
  namespace: vacation-tracker
spec:
  type: LoadBalancer
  selector:
    app: vacation-tracker          # ← matches pod labels
  ports:
    - protocol: TCP
      port: 80                     # ← external port
      targetPort: 5000             # ← container port
```

### 6. Applying the Full Stack

```bash
# Apply all manifests at once
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Or put them all in a directory and apply at once
kubectl apply -f ./manifests/

# Or combine in a single file (separated by ---)
kubectl apply -f full-stack.yaml
```

---

## Labels and Selectors – The Glue

Labels connect resources together. This is how Services know which Pods to route to.

```
Deployment
  selector:
    matchLabels:
      app: vacation-tracker  ──────┐
                                    │  must match
  template:                         │
    metadata:                       │
      labels:                       │
        app: vacation-tracker  ◄───┘
                                    │
Service                             │
  selector:                         │
    app: vacation-tracker  ────────┘
```

> **Key concept:** If labels don't match, Services won't find Pods and Deployments won't manage them. This is the #1 source of "my app is deployed but nothing works" issues.

---

## Resource Requests and Limits

```yaml
resources:
  requests:                        # Guaranteed minimum
    cpu: "100m"                    # 100 millicores = 0.1 CPU
    memory: "128Mi"                # 128 MiB
  limits:                          # Maximum allowed
    cpu: "500m"                    # 500 millicores = 0.5 CPU
    memory: "256Mi"                # 256 MiB
```

```
CPU units:
  1 CPU = 1000m (millicores)
  100m = 10% of one CPU core
  "500m" = half a CPU core

Memory units:
  Mi = Mebibytes (1 Mi = 1,048,576 bytes)
  Gi = Gibibytes
  "128Mi" = 128 MiB ≈ 134 MB
```

**What happens when limits are exceeded:**
- **CPU:** Pod is throttled (slowed down) — not killed
- **Memory:** Pod is OOMKilled (Out Of Memory) and restarted

> **For Infra Engineers:** Think of `requests` as your reservation (guaranteed capacity) and `limits` as the burst ceiling. This is similar to Azure VM sizing — but per-container.

---

# PART 7: kubectl TROUBLESHOOTING

---

## Troubleshooting Flowchart

```
App not working?
      │
      ▼
  kubectl get pods ─── Is the pod running?
      │                      │
      │ No                   │ Yes
      ▼                      ▼
  kubectl describe pod   kubectl logs <pod>
      │                      │
      │                      └── Check application errors
      ▼
  Check Events at bottom of output
      │
      ├── ImagePullBackOff    → Wrong image name / registry auth
      ├── CrashLoopBackOff    → App crashing → check logs
      ├── Pending             → No node has enough resources
      ├── ErrImagePull        → Private registry, no imagePullSecrets
      ├── OOMKilled           → Memory limit too low
      └── CreateContainerConfigError → Missing ConfigMap/Secret
```

---

## Common Issues and Fixes

### 1. Pod stuck in Pending

```bash
# Check why it's pending
kubectl describe pod my-pod

# Look for events like:
#   "0/3 nodes are available: 3 Insufficient cpu"
#   "0/3 nodes are available: 3 Insufficient memory"

# Fix: Scale node pool, reduce resource requests, or check node taints
kubectl get nodes
kubectl describe node <node-name>
kubectl top nodes
```

### 2. Pod in CrashLoopBackOff

```bash
# The container starts, crashes, restarts, crashes...
kubectl logs my-pod              # Current attempt
kubectl logs my-pod --previous   # Previous crash

# Common causes:
#   - Application error (missing env vars, wrong config)
#   - Command/entrypoint not found
#   - Database not reachable
#   - Missing dependencies
```

### 3. ImagePullBackOff

```bash
# Can't pull the container image
kubectl describe pod my-pod

# Common causes:
#   - Wrong image name or tag
#   - Private registry without imagePullSecrets
#   - ACR has no access from AKS (missing AcrPull role)

# Fix for ACR + AKS:
az aks update -n myAKS -g myRG --attach-acr myACR
```

### 4. Service Not Reaching Pods

```bash
# Check the service has endpoints
kubectl get endpoints my-service

# If endpoints is <none>:
#   → Labels on pods don't match selector on service
kubectl get pods --show-labels
kubectl describe service my-service    # Check selector

# Test from within the cluster
kubectl run debug --image=busybox --rm -it -- /bin/sh
  wget -qO- http://my-service:80     # Test internal connectivity
```

### 5. Useful Debugging Commands

```bash
# Events sorted by time (great for seeing what just happened)
kubectl get events --sort-by='.lastTimestamp' -n <namespace>

# Port-forward to test a service locally
kubectl port-forward svc/my-service 8080:80

# Run a debug pod
kubectl run debug --image=busybox:latest --rm -it --restart=Never -- /bin/sh

# Check resource usage
kubectl top pods -n <namespace>
kubectl top nodes

# View YAML of a running resource (see effective config)
kubectl get deployment my-app -o yaml

# Check cluster DNS resolution from inside a pod
kubectl exec -it my-pod -- nslookup my-service.production.svc.cluster.local

# Verify network policy isn't blocking traffic
kubectl get networkpolicies -n <namespace>
```

---

# PART 8: KUBELENS

---

## What Is KubeLens?

- **Open-source** desktop application for Kubernetes (formerly Lens IDE)
- **Visual cluster management** — see pods, deployments, services, logs, etc. in a GUI
- Supports **multiple clusters** and **contexts**
- Built-in **terminal**, **log viewer**, and **resource editor**
- Free and cross-platform (Windows, macOS, Linux)
- **OpenLens** = open-source core (community fork)

```
┌─────────────────────────────────────────────────────────────────┐
│  KubeLens / OpenLens                                             │
│                                                                  │
│  ┌────────┐  ┌──────────────────────────────────────────────┐   │
│  │Clusters│  │  Workloads > Pods                             │   │
│  │        │  │                                               │   │
│  │ myAKS ◄│  │  NAME              STATUS    RESTARTS   NODE  │   │
│  │ devK8s │  │  api-7d8f6-abc     Running   0          n1    │   │
│  │        │  │  api-7d8f6-def     Running   0          n2    │   │
│  │────────│  │  web-5c4b9-ghi     Running   2          n1    │   │
│  │Workload│  │  redis-0           Running   0          n2    │   │
│  │Network │  │                                               │   │
│  │Config  │  │  [Logs] [Shell] [Edit] [Delete]               │   │
│  │Storage │  │                                               │   │
│  │RBAC    │  └──────────────────────────────────────────────┘   │
│  └────────┘                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Why Use It

| Task | kubectl | KubeLens |
|------|---------|----------|
| View pod status | `kubectl get pods` | Visual table with status colors |
| Read logs | `kubectl logs <pod> -f` | Built-in log viewer with search |
| Shell into pod | `kubectl exec -it <pod> -- /bin/sh` | One-click terminal button |
| Edit resource | `kubectl edit deployment` | Visual YAML editor |
| View events | `kubectl get events` | Timeline view |
| Multi-cluster | Switch contexts manually | Sidebar with all clusters |

> **Recommendation:** Use `kubectl` for scripting, automation, and CI/CD. Use KubeLens for day-to-day cluster exploration and debugging. Learn kubectl first — it's the foundation.

### Installation

```bash
# Download from: https://github.com/MuhammedKalworworked/lens
# Or install OpenLens (community fork):
# https://github.com/lensapp/lens

# On Ubuntu/Debian:
sudo snap install kontena-lens --classic

# On macOS:
brew install --cask lens
```

### Demo Walkthrough (Screen Share)

1. Open KubeLens and add AKS cluster context
2. Navigate the sidebar: Namespaces, Workloads, Network
3. Click a Pod → view logs, open shell, see events
4. View Deployment → check rolling update status
5. View Services → see endpoints and external IPs

---

# PART 9: AKS – AZURE KUBERNETES SERVICE

---

## AKS Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AZURE                                          │
│                                                                             │
│  ┌──────────────────────────────────┐                                       │
│  │     AKS Control Plane            │  ← Managed by Microsoft (FREE)       │
│  │   (API Server, Scheduler,        │                                       │
│  │    Controller Manager, etcd)     │                                       │
│  └──────────────┬───────────────────┘                                       │
│                 │                                                            │
│  ┌──────────────┴───────────────────────────────────────────────────────┐   │
│  │                    AKS Node Pool (VMSS)                               │   │
│  │              ← You pay for these VMs                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                      │   │
│  │  │  Node 1     │  │  Node 2     │  │  Node 3     │                      │   │
│  │  │  (D2s_v3)   │  │  (D2s_v3)   │  │  (D2s_v3)   │                      │   │
│  │  │  ┌──┐ ┌──┐  │  │  ┌──┐ ┌──┐  │  │  ┌──┐ ┌──┐  │                      │   │
│  │  │  │P │ │P │  │  │  │P │ │P │  │  │  │P │ │P │  │                      │   │
│  │  │  └──┘ └──┘  │  │  └──┘ └──┘  │  │  └──┘ └──┘  │                      │   │
│  │  └────────────┘  └────────────┘  └────────────┘                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Supporting Azure Services                        │  │
│  │                                                                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │   ACR    │  │ Key Vault│  │ Azure    │  │ Managed  │             │  │
│  │  │ (images) │  │ (secrets)│  │ Disks    │  │ Identity │             │  │
│  │  └──────────┘  └──────────┘  │(storage) │  │  (auth)  │             │  │
│  │                              └──────────┘  └──────────┘             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                           │  │
│  │  │ Azure    │  │ Log      │  │ Azure    │                           │  │
│  │  │ Monitor  │  │ Analytics│  │ Policy   │                           │  │
│  │  └──────────┘  └──────────┘  └──────────┘                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## AKS Key Components

### Node Pools

```
AKS Cluster
  ├── System Node Pool (required)
  │     └── Runs K8s system pods (coredns, metrics-server, etc.)
  │     └── Recommended: at least 2 nodes, D2s_v3 or similar
  │
  └── User Node Pool(s) (optional, but recommended)
        └── Runs your application workloads
        └── Can have multiple pools with different VM sizes
        └── Example: "gpu-pool" with GPU VMs for ML workloads
```

| Feature | System Pool | User Pool |
|---------|------------|-----------|
| **Purpose** | K8s infrastructure | Application workloads |
| **Required** | Yes (at least 1) | No (but recommended) |
| **Tainted** | `CriticalAddonsOnly` | No (by default) |
| **VM Size** | Standard_D2s_v3 (min) | Any (based on workload) |
| **Autoscale** | Optional | Recommended |
| **Count** | 2+ (for HA) | Based on workload |

### Azure Container Registry (ACR) Integration

```
┌───────────┐     docker push      ┌──────────┐      AcrPull      ┌──────────┐
│ Developer │ ──────────────────►  │   ACR    │ ◄───────────────── │   AKS    │
│ / CI/CD   │                      │ (images) │   (managed        │ (pulls   │
└───────────┘                      └──────────┘    identity)       │  images) │
                                                                   └──────────┘
```

```bash
# Create ACR
az acr create --name myACR --resource-group myRG --sku Basic

# Attach ACR to AKS (grants AcrPull role automatically)
az aks update --name myAKS --resource-group myRG --attach-acr myACR

# Push an image
az acr login --name myACR
docker tag vacation-tracker:v1.0 myacr.azurecr.io/vacation-tracker:v1.0
docker push myacr.azurecr.io/vacation-tracker:v1.0
```

### Azure Key Vault Integration

```
┌─────────────┐                    ┌──────────────────┐
│  Key Vault  │  ────────────────► │  AKS Pod          │
│             │   CSI Secret Store │                    │
│  Secrets:   │   Driver           │  env:              │
│  DB_PASS    │                    │    DB_PASS=***     │
│  API_KEY    │                    │    API_KEY=***     │
└─────────────┘                    └──────────────────┘
```

- **Azure Key Vault Provider for Secrets Store CSI Driver**
- Mounts Key Vault secrets as files or environment variables in pods
- No more base64 secrets in YAML manifests!
- Secrets rotate automatically when updated in Key Vault

### Persistent Volumes

```
┌──────────────────────────────────────────────────────────────┐
│                      Storage in AKS                          │
│                                                              │
│  Pod                                                         │
│  ┌─────────────────┐                                         │
│  │  Container       │                                         │
│  │    /data ────────┼──► PersistentVolumeClaim (PVC)          │
│  └─────────────────┘       │                                  │
│                            ▼                                  │
│                    PersistentVolume (PV)                      │
│                            │                                  │
│                            ▼                                  │
│              ┌─────────────────────────┐                      │
│              │   Azure Storage Backend  │                      │
│              │                         │                      │
│              │  • Azure Disk (block)   │  ← ReadWriteOnce     │
│              │  • Azure Files (NFS)    │  ← ReadWriteMany     │
│              │  • Azure Blob (object)  │  ← ReadWriteMany     │
│              └─────────────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

| Storage Type | Access Mode | Use Case | Speed |
|-------------|-------------|----------|-------|
| **Azure Disk** | ReadWriteOnce (single pod) | Databases, single-pod state | Fast (SSD/Premium) |
| **Azure Files** | ReadWriteMany (multiple pods) | Shared config, uploaded files | Medium |
| **Azure Blob** | ReadWriteMany | Large data sets, backups | Varies |

```yaml
# PersistentVolumeClaim example
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-storage
  namespace: vacation-tracker
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: managed-premium    # Azure Premium SSD
  resources:
    requests:
      storage: 10Gi
```

---

## AKS in Our Terraform Project

Our project already provisions AKS via Terraform. Here's how the pieces connect:

```
terraform/
  ├── config/aks.yaml          ← AKS parameters (node count, VM size)
  ├── modules/aks/main.tf      ← AKS module (cluster definition)
  └── main.tf                  ← Root module (wires everything together)

Key settings from our config:
  • Node count:       2 (Standard_D2s_v3)
  • Network plugin:   Azure CNI (pods get VNet IPs)
  • Load balancer:    Standard SKU
  • Azure Policy:     Enabled
  • Identity:         User-assigned managed identity
```

```bash
# Connect to the AKS cluster we provisioned with Terraform
az aks get-credentials --resource-group devops-kt-rg --name devops-kt-aks

# Verify connectivity
kubectl get nodes
kubectl get pods -A
```

---

## AKS Networking with Hub-Spoke

```
┌──────────────────────────────────────────────────────────────────┐
│                    Hub-Spoke + AKS                                │
│                                                                   │
│  ┌─────────────────┐          ┌──────────────────────────────┐   │
│  │    Hub VNet      │          │      Spoke VNet (AKS)        │   │
│  │   10.0.0.0/16    │ peering  │      10.1.0.0/16             │   │
│  │                  │◄────────►│                              │   │
│  │  ┌────────────┐  │          │  ┌──────────────────────┐   │   │
│  │  │  Firewall / │  │          │  │  AKS Subnet           │   │   │
│  │  │  NVA        │  │          │  │  10.1.0.0/22          │   │   │
│  │  └────────────┘  │          │  │  (nodes + pods)       │   │   │
│  │                  │          │  └──────────────────────┘   │   │
│  │  ┌────────────┐  │          │                              │   │
│  │  │  Bastion    │  │          │  Service CIDR: 10.2.0.0/16 │   │
│  │  └────────────┘  │          │  DNS Service:  10.2.0.10    │   │
│  └─────────────────┘          └──────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

> **For Infra Engineers:** With Azure CNI, each pod gets an IP from the AKS subnet. Plan the subnet size carefully — a /22 gives you ~1000 IPs for nodes + pods. Use `/21` or larger for production clusters.

---

# SUMMARY

---

## Key Takeaways

| Concept | One-Liner |
|---------|-----------|
| **Kubernetes** | Container orchestrator that automates deployment, scaling, and management |
| **Control Plane** | The brain — API Server, Scheduler, Controllers, etcd |
| **Worker Nodes** | The muscle — run your actual containers (kubelet, kube-proxy, runtime) |
| **Pod** | Smallest unit — one or more containers sharing network/storage |
| **Deployment** | Manages pods — handles replicas, rolling updates, rollback |
| **Service** | Stable endpoint — routes traffic to pods by label selector |
| **ConfigMap / Secret** | Configuration and sensitive data, injected into pods |
| **Ingress** | L7 HTTP/HTTPS routing into the cluster |
| **Namespace** | Logical isolation within a cluster (like VLANs) |
| **kubectl** | CLI tool — your primary interface to any K8s cluster |
| **AKS** | Azure-managed K8s — free control plane, pay for worker nodes |
| **ACR** | Image registry — stores your container images close to AKS |

---

## What's Next

| Session | Topic | Preview |
|---------|-------|---------|
| **Session 8** | Kubernetes Deployments | Helm charts, Flux, GitOps |
| **Session 9** | Kubernetes Hands-On | Build a blockchain ecosystem on AKS |

> **Homework:** 
> 1. Install `kubectl` and KubeLens on your workstation
> 2. Connect to the shared AKS cluster: `az aks get-credentials --resource-group devops-kt-rg --name devops-kt-aks`
> 3. Run: `kubectl get nodes`, `kubectl get pods -A`, `kubectl get namespaces`
> 4. Try creating a namespace and deploying nginx: `kubectl create namespace myname && kubectl create deployment nginx --image=nginx -n myname`
> 5. Explore the cluster in KubeLens

---

## Useful Resources

| Resource | URL |
|----------|-----|
| Kubernetes Official Docs | https://kubernetes.io/docs/ |
| kubectl Cheat Sheet | https://kubernetes.io/docs/reference/kubectl/cheatsheet/ |
| AKS Documentation | https://learn.microsoft.com/en-us/azure/aks/ |
| KubeLens / OpenLens | https://github.com/lensapp/lens |
| K8s the Hard Way | https://github.com/kelseyhightower/kubernetes-the-hard-way |
| CNCF Landscape | https://landscape.cncf.io/ |
| Our project repo | `devops-kt/kubernetes/manifest/` |

---

## Practice Test

Test your understanding — try to answer before revealing the answer.

**Q1: What is the smallest deployable unit in Kubernetes?**
<details><summary>Answer</summary>A Pod</details>

**Q2: Which control plane component stores all cluster state?**
<details><summary>Answer</summary>etcd</details>

**Q3: What happens when a pod exceeds its memory limit?**
<details><summary>Answer</summary>It gets OOMKilled (Out Of Memory Killed) and restarted</details>

**Q4: Which `kubectl` command shows detailed information about why a pod isn't starting?**
<details><summary>Answer</summary>kubectl describe pod &lt;pod-name&gt;</details>

**Q5: What's the difference between a ConfigMap and a Secret?**
<details><summary>Answer</summary>ConfigMaps store non-sensitive configuration data. Secrets store sensitive data (base64 encoded). Both can be injected as env vars or volumes.</details>

**Q6: In AKS, who manages the control plane?**
<details><summary>Answer</summary>Microsoft / Azure — the control plane is free and fully managed</details>

**Q7: You deploy a Service but it has no endpoints. What's the most likely cause?**
<details><summary>Answer</summary>The Service selector labels don't match the Pod labels</details>

**Q8: What's the `kubectl` command to view container logs from a crashed pod?**
<details><summary>Answer</summary>kubectl logs &lt;pod-name&gt; --previous</details>

**Q9: How does AKS pull images from ACR without storing credentials?**
<details><summary>Answer</summary>Via Managed Identity with AcrPull role assignment</details>

**Q10: Name three differences between ClusterIP, NodePort, and LoadBalancer service types.**
<details><summary>Answer</summary>ClusterIP: internal only. NodePort: exposes on each node's IP at a static port. LoadBalancer: provisions an external cloud load balancer with a public IP.</details>

---

_"Containers are the new processes. Kubernetes is the new operating system. YAML is the new XML — and equally enjoyable."_

_See you next session — where we'll break things, but with Helm this time._
