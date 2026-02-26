# Terraform Guide: Theory and Real-World Implementation

## Table of Contents
1. [Fundamentals](#fundamentals)
   - [Programming Concepts](#programming-concepts)
   - [Infrastructure as Code](#infrastructure-as-code)
   - [Data Serialization Formats](#data-serialization-formats)
2. [Introduction to Terraform](#introduction-to-terraform)
3. [Core Concepts](#core-concepts)
4. [Project Structure](#project-structure)
5. [Real-World Implementation](#real-world-implementation)
6. [Best Practices](#best-practices)
7. [Common Workflows](#common-workflows)

---

## Fundamentals

### Programming Concepts

Before diving into Terraform, it's essential to understand some fundamental programming concepts that apply to Infrastructure as Code.

#### Declarative vs. Imperative Programming

**Imperative Programming** tells the computer *how* to do something step-by-step:
```bash
# Imperative example (Bash script)
az group create --name my-rg --location westeurope
az network vnet create --name my-vnet --resource-group my-rg --address-prefix 10.0.0.0/16
az network vnet subnet create --name my-subnet --resource-group my-rg --vnet-name my-vnet --address-prefix 10.0.1.0/24
```

**Declarative Programming** tells the computer *what* you want, and it figures out how to achieve it:
```hcl
# Declarative example (Terraform)
resource "azurerm_resource_group" "main" {
  name     = "my-rg"
  location = "westeurope"
}

resource "azurerm_virtual_network" "main" {
  name                = "my-vnet"
  address_space       = ["10.0.0.0/16"]
  resource_group_name = azurerm_resource_group.main.name
}
```

**Key Differences:**
| Aspect | Imperative | Declarative |
|--------|-----------|-------------|
| **Focus** | How to achieve goal | What the goal is |
| **Order** | Explicit sequencing | Automatic dependency resolution |
| **Idempotency** | Must handle manually | Built-in |
| **State** | Managed by scripts | Managed by tool |
| **Examples** | Bash, Python scripts | Terraform, Ansible, Kubernetes |

#### Variables and Data Types

Modern programming languages use typed variables to store and manipulate data:

```hcl
# String
variable "location" {
  type    = string
  default = "westeurope"
}

# Number
variable "vm_count" {
  type    = number
  default = 3
}

# Boolean
variable "enable_backup" {
  type    = bool
  default = true
}

# List
variable "allowed_ips" {
  type    = list(string)
  default = ["10.0.0.0/8", "192.168.0.0/16"]
}

# Map (Dictionary/Object)
variable "tags" {
  type = map(string)
  default = {
    Environment = "Production"
    Owner       = "DevOps Team"
  }
}

# Complex object
variable "vm_config" {
  type = object({
    name = string
    size = string
    os   = string
  })
  default = {
    name = "web-vm"
    size = "Standard_D2s_v3"
    os   = "Ubuntu"
  }
}
```

---

### Infrastructure as Code

#### What is Infrastructure as Code (IaC)?

**Infrastructure as Code** is the practice of managing and provisioning infrastructure through machine-readable definition files rather than manual processes or interactive configuration tools.

**Traditional Infrastructure Management:**
```
Manual Process:
1. Log into Azure Portal
2. Click "Create Resource"
3. Fill out forms
4. Click buttons
5. Wait...
6. Repeat for each resource
7. Document manually (maybe)
8. Hope you remember the settings
```

**Infrastructure as Code:**
```
Automated Process:
1. Write infrastructure definition in code
2. Run: terraform apply
3. Infrastructure created automatically
4. Code is the documentation
5. Version controlled in Git
6. Repeatable and consistent
```

#### Benefits of IaC

**1. Version Control**
```bash
git log --oneline terraform/
# f8a3c2d Add production AKS cluster
# e1b4a6c Update network security rules
# c7d9f2e Initial hub-spoke topology
```

**2. Consistency**
- Same code always creates same infrastructure
- No manual configuration drift
- Eliminates "works on my machine" problems

**3. Automation**
```yaml
# CI/CD Pipeline
- name: Deploy Infrastructure
  run: |
    terraform init
    terraform plan
    terraform apply -auto-approve
```

**4. Documentation**
- Code serves as living documentation
- Always up-to-date (unlike wikis)
- Self-documenting through variable descriptions

**5. Collaboration**
```
Multiple team members can:
- Review changes via Pull Requests
- Suggest improvements
- Understand infrastructure design
- Contribute safely
```

**6. Disaster Recovery**
```bash
# Infrastructure destroyed? Rebuild from code:
git clone <repo>
terraform apply
# Everything restored
```

#### IaC Tools Comparison

| Tool | Approach | Primary Use | Language | Provider |
|------|----------|-------------|----------|----------|
| **Terraform** | Declarative | Multi-cloud provisioning | HCL | HashiCorp |
| **Ansible** | Declarative | Configuration management | YAML | Red Hat |
| **Pulumi** | Imperative | Multi-cloud provisioning | Python/JS/Go | Pulumi |
| **CloudFormation** | Declarative | AWS provisioning | JSON/YAML | AWS |
| **ARM Templates** | Declarative | Azure provisioning | JSON | Microsoft |
| **Kubernetes** | Declarative | Container orchestration | YAML | CNCF |

#### IaC Best Practices

✅ **DO:**
- Store IaC in version control (Git)
- Use modules for reusability
- Keep secrets out of code
- Document your infrastructure
- Test changes in non-production first
- Use CI/CD for deployments
- Review changes before applying

❌ **DON'T:**
- Manually modify managed resources
- Commit secrets to Git
- Skip code reviews
- Work directly in production
- Ignore plan output
- Mix manual and automated changes

---

### Data Serialization Formats

Data serialization is the process of converting data structures into a format that can be stored or transmitted and reconstructed later. In IaC, we use serialization formats to define infrastructure configurations.

#### YAML (YAML Ain't Markup Language)

**Characteristics:**
- Human-readable and writable
- Uses indentation for structure (Python-like)
- Supports comments
- Common in DevOps tools (Kubernetes, Ansible, Docker Compose)

**Syntax:**
```yaml
# Project Configuration (config/project.yaml)
project_name: devops-kt
azure_location: westeurope
environment: dev

# Lists
availability_zones:
  - 1
  - 2
  - 3

# Nested structures
common_tags:
  CreatedBy: Terraform
  Topology: HubSpoke
  Author: pizour

# Multiple documents (separated by ---)
---
virtual_networks:
  hub-vnet:
    hub: true
    address_space:
      - 10.0.0.0/16
    subnets:
      hub-fw-snet: 10.0.0.0/24
      AzureBastionSubnet: 10.0.1.0/24
  
  spoke1-aks-vnet:
    address_space:
      - 10.1.0.0/16
    subnets:
      spoke1-aks-snet: 10.1.0.0/24
```

**In This Project:**
```hcl
# Terraform loading YAML
locals {
  project_config = yamldecode(file("${path.module}/config/project.yaml"))
  vnets_config   = yamldecode(file("${path.module}/config/vnets.yaml"))
  
  project_name = local.project_config.project_name
  vnets        = local.vnets_config
}
```

**Pros:**
- ✅ Most human-readable
- ✅ Supports comments
- ✅ Less verbose than JSON
- ✅ Multi-line strings easy

**Cons:**
- ❌ Indentation-sensitive (can cause errors)
- ❌ No native validation
- ❌ Ambiguous parsing rules

---

#### JSON (JavaScript Object Notation)

**Characteristics:**
- Machine-readable format
- Strict syntax rules
- No comments allowed
- Native JavaScript data format
- Universal parser support

**Syntax:**
```json
{
  "project_name": "devops-kt",
  "azure_location": "westeurope",
  "environment": "dev",
  "availability_zones": [1, 2, 3],
  "common_tags": {
    "CreatedBy": "Terraform",
    "Topology": "HubSpoke",
    "Author": "pizour"
  },
  "virtual_networks": {
    "hub-vnet": {
      "hub": true,
      "address_space": ["10.0.0.0/16"],
      "subnets": {
        "hub-fw-snet": "10.0.0.0/24",
        "AzureBastionSubnet": "10.0.1.0/24"
      }
    },
    "spoke1-aks-vnet": {
      "address_space": ["10.1.0.0/16"],
      "subnets": {
        "spoke1-aks-snet": "10.1.0.0/24"
      }
    }
  }
}
```

**In Terraform:**
```hcl
# JSON output
output "network_config" {
  value = jsonencode({
    hub_vnet_id = module.hub_spoke.hub_vnet_id
    subnets     = module.hub_spoke.subnet_ids
  })
}

# Reading JSON
locals {
  config = jsondecode(file("config.json"))
}
```

**Pros:**
- ✅ Universal support
- ✅ Strict parsing (catches errors)
- ✅ Native web/API format
- ✅ Schema validation (JSON Schema)

**Cons:**
- ❌ No comments
- ❌ Verbose (quotes, commas, braces)
- ❌ Less human-readable
- ❌ No multi-line strings

---

#### HCL (HashiCorp Configuration Language)

**Characteristics:**
- Designed specifically for Terraform
- Hybrid declarative/imperative syntax
- Native support for interpolation and functions
- Balance between human and machine readability

**Syntax:**
```hcl
# Resource definition
resource "azurerm_resource_group" "main" {
  name     = "devops-kt-rg"
  location = "westeurope"
  
  tags = {
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# Variables with validation
variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westeurope"
  
  validation {
    condition     = contains(["westeurope", "northeurope"], var.location)
    error_message = "Location must be westeurope or northeurope"
  }
}

# Complex data structures
locals {
  vnets = {
    hub = {
      address_space = ["10.0.0.0/16"]
      subnets = {
        firewall = "10.0.0.0/24"
        bastion  = "10.0.1.0/24"
      }
    }
    spoke1 = {
      address_space = ["10.1.0.0/16"]
      subnets = {
        aks = "10.1.0.0/24"
      }
    }
  }
}

# Dynamic blocks
dynamic "subnet" {
  for_each = local.vnets.hub.subnets
  
  content {
    name             = subnet.key
    address_prefixes = [subnet.value]
  }
}

# Functions and interpolation
locals {
  # String interpolation
  resource_name = "${var.project}-${var.environment}-rg"
  
  # Function calls
  tags = merge(
    var.common_tags,
    {
      CreatedAt = timestamp()
    }
  )
  
  # Conditional expressions
  vm_size = var.environment == "prod" ? "Standard_D4s_v3" : "Standard_D2s_v3"
  
  # List comprehension
  subnet_ids = [for subnet in azurerm_subnet.main : subnet.id]
}

# Heredoc strings
resource "azurerm_virtual_machine_extension" "init" {
  settings = <<-SETTINGS
    {
      "commandToExecute": "apt-get update && apt-get install -y docker.io"
    }
  SETTINGS
}
```

**Pros:**
- ✅ Designed for infrastructure
- ✅ Comments supported
- ✅ Built-in functions
- ✅ String interpolation
- ✅ Conditional logic
- ✅ Type validation

**Cons:**
- ❌ Terraform-specific
- ❌ Steeper learning curve
- ❌ Not as universal as JSON

---

#### Format Comparison

| Feature | YAML | JSON | HCL |
|---------|------|------|-----|
| **Readability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Comments** | ✅ Yes | ❌ No | ✅ Yes |
| **Strict Parsing** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Functions** | ❌ No | ❌ No | ✅ Yes |
| **Interpolation** | ❌ No | ❌ No | ✅ Yes |
| **Universal Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Use Case** | Config files | APIs, data | IaC (Terraform) |

#### When to Use Each Format

**Use YAML when:**
- Human readability is priority #1
- Configuration files for users to edit
- Kubernetes manifests
- CI/CD pipeline definitions
- Ansible playbooks

**Use JSON when:**
- API communication
- Strict schema validation required
- Machine-generated configs
- Web applications
- No comments needed

**Use HCL when:**
- Writing Terraform configurations
- Need conditional logic
- Functions and interpolation required
- Infrastructure as Code

#### This Project's Approach

This project uses a **hybrid approach** combining the strengths of multiple formats:

```
┌─────────────────────────────────────────────────────┐
│ YAML Files (config/*.yaml)                          │
│ - User-friendly configuration                       │
│ - Network topology, NSG rules, AKS settings         │
│ - Easy to review and modify                         │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ yamldecode()
                    ▼
┌─────────────────────────────────────────────────────┐
│ HCL Files (*.tf)                                    │
│ - Infrastructure logic                              │
│ - Resource definitions                              │
│ - Module orchestration                              │
│ - Variable processing                               │
└─────────────────────────────────────────────────────┘
```

**Example:**
```yaml
# config/vnets.yaml (YAML for data)
hub-vnet:
  address_space: ["10.0.0.0/16"]
  subnets:
    firewall: "10.0.0.0/24"
```

```hcl
# locals.tf (HCL for logic)
locals {
  vnets_config = yamldecode(file("${path.module}/config/vnets.yaml"))
}

# main.tf (HCL for resources)
module "hub_spoke" {
  source = "./modules/hub_spoke"
  vnets  = local.vnets_config
}
```

**Benefits of this approach:**
- 📝 YAML for human-editable configuration (non-Terraform users can contribute)
- 🔧 HCL for infrastructure logic (Terraform developers handle complexity)
- 🔄 Separation of concerns (data vs. code)
- 👥 Team collaboration (different skill levels can contribute)

---

## Introduction to Terraform

### What is Terraform?

Terraform is an **Infrastructure as Code (IaC)** tool developed by HashiCorp that allows you to define, provision, and manage cloud infrastructure using declarative configuration files. Instead of manually creating resources through cloud provider consoles or APIs, you write code that describes your desired infrastructure state.

### Why Terraform?

- **Declarative Syntax**: Describe *what* you want, not *how* to create it
- **Cloud-Agnostic**: Works with multiple cloud providers (Azure, AWS, GCP, etc.)
- **State Management**: Tracks actual vs. desired infrastructure state
- **Plan Before Apply**: Preview changes before execution
- **Reusable Modules**: Create reusable infrastructure components
- **Version Control**: Infrastructure code can be versioned in Git
- **Collaboration**: Teams can work together on infrastructure

### How Terraform Works

Terraform follows a workflow with distinct phases:

```
┌─────────────┐
│ Write Code  │  .tf files describing desired infrastructure
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  terraform  │  Download providers, initialize backend
│    init     │  Prepare working directory
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  terraform  │  Parse configuration and create execution plan
│    plan     │  Show what will change
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  terraform  │  Create/update/delete resources via provider APIs
│    apply    │  Execute the plan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  State File │  Track actual infrastructure (terraform.tfstate)
└─────────────┘
```

**Workflow Phases:**

1. **terraform init**
   - Downloads provider plugins (Azure, AWS, etc.)
   - Initializes backend for state storage
   - Downloads referenced modules
   - Prepares the working directory
   - *Run once* when starting a new project or after adding new providers

2. **terraform plan**
   - Reads current state
   - Compares desired configuration with actual state
   - Creates execution plan showing changes
   - No changes are made to infrastructure
   - Review output: `+` create, `~` modify, `-` destroy

3. **terraform apply**
   - Executes the plan (or creates a new one)
   - Makes API calls to create/update/delete resources
   - Updates state file with current infrastructure
   - Requires confirmation (unless `-auto-approve` flag)

4. **terraform destroy** (optional)
   - Removes all resources managed by Terraform
   - Useful for cleanup or testing

**Example Workflow:**
```bash
# 1. Initialize - download providers and modules
$ terraform init
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/azurerm v4.57.0...
Terraform has been successfully initialized!

# 2. Plan - preview changes
$ terraform plan
Terraform will perform the following actions:
  # azurerm_resource_group.main will be created
  + resource "azurerm_resource_group" "main" {
      + name     = "devops-kt-rg"
      + location = "westeurope"
    }
Plan: 1 to add, 0 to change, 0 to destroy.

# 3. Apply - create infrastructure
$ terraform apply
Do you want to perform these actions? yes
azurerm_resource_group.main: Creating...
azurerm_resource_group.main: Creation complete!
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

## Core Concepts

### 1. Providers

Providers are plugins that interact with cloud platforms, SaaS providers, and APIs. Each provider adds a set of resource types and data sources.

**Theory:**
```hcl
provider "azurerm" {
  features {}
  subscription_id = "xxx"
}
```

**This Project:**
```hcl
# backend.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.57"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
  client_id       = var.azure_client_id
  client_secret   = var.azure_client_secret
  tenant_id       = var.azure_tenant_id
}
```

### 2. Resources

Resources are the fundamental building blocks. They represent infrastructure objects like virtual machines, networks, storage, etc.

**Theory:**
```hcl
resource "resource_type" "logical_name" {
  argument1 = "value1"
  argument2 = "value2"
}
```

**This Project:**
```hcl
# main.tf
resource "azurerm_resource_group" "main" {
  name     = local.azure_resource_group_name
  location = local.azure_location
  tags     = local.common_tags
}
```

### 3. Variables

Variables allow you to parameterize your configurations, making them reusable and flexible.

**Theory:**
```hcl
variable "name" {
  description = "Description of the variable"
  type        = string
  default     = "default-value"
  sensitive   = false
}
```

**This Project:**
```hcl
# variables.tf
variable "azure_subscription_id" {
  description = "Azure subscription ID"
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
```

### 4. Outputs

Outputs expose information about your infrastructure to be used by other configurations or displayed to users.

**Theory:**
```hcl
output "name" {
  description = "Description of output"
  value       = resource.type.name.attribute
  sensitive   = false
}
```

**This Project:**
```hcl
# outputs.tf
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "hub_vnet_id" {
  description = "ID of the hub VNet"
  value       = module.hub_spoke.hub_vnet_id
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}
```

### 5. Locals

Locals are named values that can be used throughout your configuration. They're useful for computed values and reducing repetition.

**Theory:**
```hcl
locals {
  common_name = "${var.project}-${var.environment}"
  common_tags = {
    Project = var.project
    Env     = var.environment
  }
}
```

**This Project:**
```hcl
# locals.tf
locals {
  # Load YAML configurations
  project_config      = yamldecode(file("${path.module}/config/project.yaml"))
  vnets_config        = yamldecode(file("${path.module}/config/vnets.yaml"))
  
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
}
```

### 6. Modules

Modules are containers for multiple resources that are used together. They enable code reuse and organization.

**Theory:**
```hcl
module "network" {
  source = "./modules/network"
  
  name     = var.network_name
  location = var.location
}
```

**This Project:**
```hcl
# main.tf
module "hub_spoke" {
  source = "./modules/hub_spoke"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  common_tags         = local.common_tags

  vnets             = local.vnets
  nva_private_ip    = local.nva_private_ip
  subnet_nsgs       = local.subnet_nsgs
  default_nsg_rules = local.default_nsg_rules
}
```

### 7. Data Sources

Data sources allow you to fetch information from providers or other Terraform configurations.

**Theory:**
```hcl
data "azurerm_resource_group" "existing" {
  name = "existing-rg"
}

resource "azurerm_virtual_network" "vnet" {
  resource_group_name = data.azurerm_resource_group.existing.name
}
```

### 8. State Management

Terraform maintains a state file (`terraform.tfstate`) that maps your configuration to real-world resources.

**Key Concepts:**
- **State File**: JSON file tracking current infrastructure state
- **State Lock**: Prevents concurrent modifications
- **Remote State**: Store state in cloud storage for team collaboration
- **State Refresh**: Sync state with actual infrastructure

### 9. Built-in Functions

Terraform provides built-in functions for data manipulation and transformation.

**String Functions:**
```hcl
locals {
  # String manipulation
  uppercase_name = upper("devops-kt")           # "DEVOPS-KT"
  lowercase_name = lower("DEVOPS-KT")           # "devops-kt"
  trimmed        = trim("  hello  ")            # "hello"
  replaced       = replace("hub-vnet", "-", "_") # "hub_vnet"
}
```

**List Functions:**
```hcl
locals {
  # List operations
  first_ip    = element(var.allowed_ips, 0)
  joined_ips  = join(",", var.allowed_ips)
  flattened   = flatten([[1, 2], [3, 4]])      # [1, 2, 3, 4]
  sorted_list = sort(["c", "a", "b"])          # ["a", "b", "c"]
}
```

**File Functions:**
```hcl
locals {
  # File operations
  yaml_config = yamldecode(file("${path.module}/config/project.yaml"))
  json_config = jsondecode(file("${path.module}/config.json"))
  template    = templatefile("init.tpl", { name = "server" })
}
```

**Type Conversion:**
```hcl
locals {
  # Type conversions
  string_to_number = tonumber("42")
  number_to_string = tostring(42)
  to_list          = tolist(["a", "b"])
  to_map           = tomap({ key = "value" })
}
```

**Collection Functions:**
```hcl
locals {
  # Merge maps
  merged_tags = merge(
    var.common_tags,
    { Environment = "prod" }
  )
  
  # Lookup values
  region = lookup(var.regions, "primary", "westeurope")
  
  # Check contains
  has_prod = contains(["dev", "staging", "prod"], var.environment)
}
```

**This Project:**
```hcl
# locals.tf
locals {
  # File loading with yamldecode
  project_config = yamldecode(file("${path.module}/config/project.yaml"))
  
  # String replacement
  dns_prefix = replace(local.azure_resource_group_name, "-", "")
  
  # Merge for tags
  common_tags = merge(
    local.project_config.common_tags,
    {
      Environment = local.environment
      Project     = local.project_name
    }
  )
  
  # Join for IP list
  source_address_prefix = rule.source_address_prefix == "ALLOWED_SSH_IPS" ? 
    join(",", var.allowed_ssh_ips) : rule.source_address_prefix
}
```

### 10. Dynamic Blocks and Loops

Terraform provides control structures for dynamic resource creation.

**for_each** - Create multiple similar resources:
```hcl
variable "subnets" {
  type = map(string)
  default = {
    web = "10.0.1.0/24"
    app = "10.0.2.0/24"
    db  = "10.0.3.0/24"
  }
}

resource "azurerm_subnet" "subnets" {
  for_each = var.subnets
  
  name                 = each.key
  address_prefixes     = [each.value]
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
}
```

**count** - Create N identical resources:
```hcl
resource "azurerm_virtual_machine" "web" {
  count = 3
  
  name = "web-vm-${count.index}"
  # ... other configuration
}
```

**dynamic blocks** - Conditionally create nested blocks:
```hcl
resource "azurerm_network_security_group" "nsg" {
  name = "my-nsg"
  
  dynamic "security_rule" {
    for_each = var.security_rules
    
    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
    }
  }
}
```

**Conditional expressions**:
```hcl
resource "azurerm_public_ip" "vm_ip" {
  count = var.enable_public_ip ? 1 : 0
  
  name = "vm-public-ip"
  # ... other configuration
}

locals {
  # Ternary operator
  vm_size = var.environment == "prod" ? "Standard_D4s_v3" : "Standard_D2s_v3"
}
```

**for expressions** - Transform collections:
```hcl
locals {
  # Create list from map
  subnet_ids = [for subnet in azurerm_subnet.main : subnet.id]
  
  # Create map from list
  subnet_map = { for subnet in azurerm_subnet.main : subnet.name => subnet.id }
  
  # Filter and transform
  prod_vnets = [for vnet_name, vnet in var.vnets : vnet_name if vnet.environment == "prod"]
}
```

**This Project:**
```hcl
# locals.tf - Processing NSG rules with for loop
locals {
  subnet_nsgs = {
    for subnet_key, nsg_config in local.nsgs_config.subnet_nsgs : subnet_key => {
      nsg_name = nsg_config.nsg_name
      rules = [
        for rule in nsg_config.rules : merge(rule, {
          source_address_prefix = rule.source_address_prefix == "ALLOWED_SSH_IPS" ? 
            join(",", var.allowed_ssh_ips) : rule.source_address_prefix
        })
      ]
    }
  }
}
```

```hcl
# modules/hub_spoke/nsg.tf - for_each to create multiple NSGs
resource "azurerm_network_security_group" "subnet_nsgs" {
  for_each = var.subnet_nsgs

  name                = each.value.nsg_name
  location            = var.location
  resource_group_name = var.resource_group_name

  dynamic "security_rule" {
    for_each = each.value.rules
    
    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
    }
  }

  tags = var.common_tags
}
```

---

## Project Structure

This project follows Terraform best practices with a modular architecture:

```
terraform/
├── backend.tf              # Provider and backend configuration
├── main.tf                 # Root module - main resource definitions
├── variables.tf            # Input variable declarations
├── locals.tf              # Local values and YAML config loading
├── outputs.tf             # Output value definitions
├── terraform.tfvars       # Variable values (gitignored - contains secrets)
├── terraform.tfstate      # State file (auto-generated)
│
├── config/                # YAML configuration files
│   ├── project.yaml       # Project metadata and common settings
│   ├── vnets.yaml        # Virtual network topology
│   ├── nsgs.yaml         # Network security group rules
│   ├── aks.yaml          # AKS cluster configuration
│   └── nva_firewall.yaml # NVA firewall settings
│
└── modules/               # Reusable Terraform modules
    ├── hub_spoke/         # Hub-spoke network topology
    │   ├── networking.tf
    │   ├── nsg.tf
    │   ├── routetables.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── README.md
    │
    ├── aks/               # Azure Kubernetes Service
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── README.md
    │
    └── ubuntu_nva_firewall/ # Network Virtual Appliance
        ├── main.tf
        ├── init-script.sh
        ├── variables.tf
        ├── outputs.tf
        └── README.md
```

### File Purposes

| File | Purpose |
|------|---------|
| `backend.tf` | Provider configuration, version constraints |
| `main.tf` | Root module orchestrating all resources |
| `variables.tf` | Input parameter definitions |
| `locals.tf` | Computed values, YAML config loading |
| `outputs.tf` | Exposed values after deployment |
| `terraform.tfvars` | Actual variable values (secrets) |
| `config/*.yaml` | Declarative infrastructure configuration |
| `modules/*/` | Reusable infrastructure components |

---

## Real-World Implementation

### Architecture Overview

This project implements a **Hub-Spoke network topology** on Azure with:

```
┌──────────────────────────────────────────────────────────┐
│                    Hub VNet (10.0.0.0/16)                │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Firewall Subnet│  │   Bastion    │  │    Shared    │ │
│  │  (10.0.0.0/24) │  │ (10.0.1.0/24)│  │ (10.0.3.0/24)│ │
│  │                │  │              │  │              │ │
│  │  NVA Firewall  │  │  Management  │  │  Services    │ │
│  │   10.0.0.10    │  │    Access    │  │              │ │
│  └────────┬───────┘  └──────────────┘  └──────────────┘ │
└───────────┼──────────────────────────────────────────────┘
            │ VNet Peering
     ┌──────┴──────┬──────────────────┐
     │             │                  │
     ▼             ▼                  ▼
┌─────────┐  ┌──────────┐      ┌──────────┐
│ Spoke 1 │  │ Spoke 2  │      │ Spoke N  │
│   AKS   │  │  VMs     │ ...  │  Future  │
└─────────┘  └──────────┘      └──────────┘
```

### 1. YAML-Driven Configuration

**Innovation**: Instead of hardcoding values in `.tf` files, this project uses YAML configuration files for data-driven infrastructure.

**Benefits:**
- ✅ Non-technical teams can modify network topology
- ✅ Easy to review changes in Git diffs
- ✅ Separation of configuration from code
- ✅ Reusable across environments (dev, staging, prod)

**Example - Network Topology Definition:**

```yaml
# config/vnets.yaml
hub-vnet:
  hub: true
  address_space:
    - 10.0.0.0/16
  subnets:
    hub-fw-snet: 10.0.0.0/24
    AzureBastionSubnet: 10.0.1.0/24

spoke1-aks-vnet:
  address_space:
    - 10.1.0.0/16
  subnets:
    spoke1-aks-snet: 10.1.0.0/24

spoke2-mgmt-vnet:
  address_space:
    - 10.2.0.0/16
  subnets:
    spoke2-vms-snet: 10.2.0.0/24
```

**How it's loaded in Terraform:**

```hcl
# locals.tf
locals {
  vnets_config = yamldecode(file("${path.module}/config/vnets.yaml"))
  vnets        = local.vnets_config
}

# main.tf
module "hub_spoke" {
  source = "./modules/hub_spoke"
  vnets  = local.vnets  # Pass YAML data to module
}
```

### 2. Dynamic NSG Rule Processing

**Problem**: SSH access needs to be restricted to specific admin IP addresses, but we don't want IPs hardcoded in YAML files (version control security).

**Solution**: Use a placeholder in YAML, replace with actual IPs from `terraform.tfvars` (gitignored):

```yaml
# config/nsgs.yaml
subnet_nsgs:
  hub-vnet/hub-fw-snet:
    nsg_name: devops-kt-hub-fw-snet-nsg
    rules:
      - name: AllowSSHFromDesktop
        priority: 105
        direction: Inbound
        access: Allow
        protocol: Tcp
        source_port_range: "*"
        destination_port_range: "22"
        source_address_prefix: ALLOWED_SSH_IPS  # Placeholder
        destination_address_prefix: "*"
```

```hcl
# locals.tf - Dynamic replacement
locals {
  subnet_nsgs = {
    for subnet_key, nsg_config in local.nsgs_config.subnet_nsgs : subnet_key => {
      nsg_name = nsg_config.nsg_name
      rules = [
        for rule in nsg_config.rules : merge(rule, {
          # Replace placeholder with actual IPs from terraform.tfvars
          source_address_prefix = rule.source_address_prefix == "ALLOWED_SSH_IPS" ? 
            join(",", var.allowed_ssh_ips) : rule.source_address_prefix
        })
      ]
    }
  }
}
```

```hcl
# terraform.tfvars (gitignored)
allowed_ssh_ips = ["203.0.113.50", "198.51.100.42"]
```

### 3. Hub-Spoke Module

**Purpose**: Create a complete hub-spoke network topology with VNet peering, routing, and security.

**Key Features:**
- Automatic VNet peering between hub and all spokes
- Centralized routing through NVA firewall (10.0.0.10)
- Per-subnet Network Security Groups
- Dynamic route table creation

**Module Usage:**

```hcl
# main.tf
module "hub_spoke" {
  source = "./modules/hub_spoke"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  
  vnets             = local.vnets              # From vnets.yaml
  nva_private_ip    = local.nva_private_ip     # From nva_firewall.yaml
  subnet_nsgs       = local.subnet_nsgs        # From nsgs.yaml (processed)
  default_nsg_rules = local.default_nsg_rules  # From nsgs.yaml
  
  common_tags = local.common_tags
}
```

**What it creates:**
1. **Virtual Networks**: Hub + multiple spokes
2. **Subnets**: Segmented by function (firewall, bastion, AKS, VMs)
3. **VNet Peering**: Hub ↔ Spoke connectivity
4. **Route Tables**: 
   - Spoke subnets: `0.0.0.0/0 → 10.0.0.10` (NVA)
   - Firewall subnet: `10.0.0.0/8 → VnetLocal`, `0.0.0.0/0 → Internet`
5. **Network Security Groups**: Per-subnet firewall rules

### 4. Ubuntu NVA Firewall Module

**Purpose**: Deploy a Linux-based Network Virtual Appliance for centralized traffic inspection and SNAT.

**Key Capabilities:**
- IP forwarding enabled
- Iptables-based SNAT for spoke egress
- SSH access restricted to admin IPs
- Optional public IP for management

**Module Usage:**

```hcl
# main.tf
module "ubuntu_nva_firewall" {
  source = "./modules/ubuntu_nva_firewall"

  project_name        = local.project_name
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  nva_name            = local.nva_firewall.nva_name
  firewall_subnet_id  = module.hub_spoke.subnet_ids["hub-vnet/hub-fw-snet"]
  private_ip_address  = local.nva_firewall.private_ip_address

  vm_size              = local.nva_firewall.vm_size
  enable_public_ip     = local.nva_firewall.enable_public_ip
  enable_ip_forwarding = local.nva_firewall.enable_ip_forwarding

  admin_username = "azureuser"
  admin_password = var.nva_admin_password

  common_tags = local.common_tags

  depends_on = [module.hub_spoke]
}
```

**init-script.sh (Cloud-init):**
```bash
#!/bin/bash
# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Configure iptables SNAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables-save > /etc/iptables/rules.v4
```

### 5. AKS Module

**Purpose**: Deploy Azure Kubernetes Service cluster integrated with hub-spoke topology.

**Key Features:**
- Deploys into spoke VNet subnet (10.1.0.0/24)
- All egress traffic routes through NVA firewall
- Azure CNI networking (pods get VNet IPs)
- Isolated service CIDR (10.240.0.0/16)
- System-assigned managed identity

**Module Usage:**

```hcl
# main.tf
module "aks" {
  source = "./modules/aks"

  cluster_name        = "${local.azure_resource_group_name}-aks"
  dns_prefix          = replace(local.azure_resource_group_name, "-", "")
  location            = local.azure_location
  resource_group_name = azurerm_resource_group.main.name
  resource_group_id   = azurerm_resource_group.main.id

  subnet_id = module.hub_spoke.subnet_ids["spoke1-aks-vnet/spoke1-aks-snet"]

  node_count         = local.aks.aks_node_count
  vm_size            = local.aks.aks_vm_size
  kubernetes_version = local.aks.kubernetes_version

  service_cidr   = "10.240.0.0/16"
  dns_service_ip = "10.240.0.10"

  enable_http_application_routing = local.aks.aks_enable_http_routing
  enable_azure_policy             = local.aks.aks_enable_azure_policy

  common_tags = local.common_tags

  depends_on = [module.hub_spoke]
}
```

**Traffic Flow:**
```
AKS Pod → Spoke Subnet → Route Table (0.0.0.0/0 → 10.0.0.10) → 
NVA Firewall → Internet
```

### 6. Resource Dependencies

**Explicit Dependencies:**
```hcl
# main.tf
module "ubuntu_nva_firewall" {
  # ... configuration ...
  
  depends_on = [
    azurerm_resource_group.main,
    module.hub_spoke
  ]
}
```

**Implicit Dependencies** (via resource references):
```hcl
resource_group_name = azurerm_resource_group.main.name  # Waits for RG
subnet_id = module.hub_spoke.subnet_ids["..."]          # Waits for VNet
```

### 7. Sensitive Variable Handling

**Variables Definition:**
```hcl
# variables.tf
variable "azure_client_secret" {
  description = "Azure service principal client secret"
  type        = string
  sensitive   = true  # Prevents logging in plan/apply output
}
```

**Usage:**
```hcl
# terraform.tfvars (gitignored)
azure_subscription_id = "12345678-1234-1234-1234-123456789abc"
azure_client_id       = "abcd1234-ab12-cd34-ef56-1234567890ab"
azure_client_secret   = "super-secret-password-here"
azure_tenant_id       = "87654321-4321-4321-4321-ba9876543210"
nva_admin_password    = "ComplexP@ssw0rd!"
allowed_ssh_ips       = ["203.0.113.50", "198.51.100.42"]
```

**Security Best Practices:**
```gitignore
# .gitignore
*.tfvars
*.tfstate
*.tfstate.backup
.terraform/
```

---

## Best Practices

### 1. Module Organization

✅ **DO:**
- One module per logical infrastructure component
- Include `README.md` in each module
- Define clear input variables and outputs
- Keep modules focused and reusable

❌ **DON'T:**
- Create monolithic modules doing everything
- Hardcode values inside modules
- Forget to document module usage

### 2. State Management

✅ **DO:**
- Use remote state (Azure Storage, S3, Terraform Cloud)
- Enable state locking
- Keep sensitive data out of state (when possible)
- Backup state files regularly

❌ **DON'T:**
- Commit `terraform.tfstate` to Git
- Manually edit state files
- Share state files via email/chat

### 3. Variable Management

✅ **DO:**
- Use `sensitive = true` for secrets
- Provide descriptions for all variables
- Use `.tfvars` files for environment-specific values
- Validate variable types

❌ **DON'T:**
- Hardcode secrets in `.tf` files
- Commit `.tfvars` with secrets to Git
- Use default values for environment-specific settings

### 4. Resource Naming

✅ **DO:**
```hcl
locals {
  resource_prefix = "${var.project}-${var.environment}"
  
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.common_tags
}
```

❌ **DON'T:**
```hcl
resource "azurerm_resource_group" "main" {
  name     = "my-rg"  # Not descriptive
  location = "westeurope"  # Hardcoded
}
```

### 5. Code Formatting

✅ **DO:**
```bash
# Format all .tf files
terraform fmt -recursive

# Validate configuration
terraform validate
```

### 6. Version Constraints

✅ **DO:**
```hcl
terraform {
  required_version = ">= 1.0"  # Terraform CLI version
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.57"  # Allow minor updates (4.57.x)
    }
  }
}
```

### 7. Documentation

✅ **DO:**
- Document module purpose and usage
- Provide example configurations
- Explain complex logic with comments
- Keep architecture diagrams updated

---

## Common Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd devops-kt/terraform

# 2. Copy example tfvars and fill in your values
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit with your secrets

# 3. Initialize Terraform (downloads providers)
terraform init

# 4. Validate configuration
terraform validate

# 5. Format code
terraform fmt -recursive
```

### Deploying Infrastructure

```bash
# 1. Preview changes
terraform plan

# 2. Review the plan output carefully
#    - Resources to be created (+)
#    - Resources to be modified (~)
#    - Resources to be destroyed (-)

# 3. Apply changes
terraform apply

# 4. Confirm with 'yes' when prompted

# 5. View outputs
terraform output
```

### Updating Infrastructure

```bash
# 1. Modify configuration files
nano config/aks.yaml  # Change node count, for example

# 2. Preview changes
terraform plan

# 3. Apply changes
terraform apply
```

### Destroying Infrastructure

```bash
# Preview destruction
terraform plan -destroy

# Destroy everything
terraform destroy

# Destroy specific resource
terraform destroy -target=module.aks
```

### Inspecting State

```bash
# List all resources in state
terraform state list

# Show details of specific resource
terraform state show azurerm_resource_group.main

# View outputs
terraform output

# View specific output
terraform output aks_cluster_name
```

### Troubleshooting

```bash
# Enable detailed logging
export TF_LOG=DEBUG
terraform plan

# Validate configuration
terraform validate

# Check formatting
terraform fmt -check -recursive

# Refresh state (sync with real infrastructure)
terraform refresh

# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/.../resourceGroups/my-rg
```

### Working with Modules

```bash
# Initialize/update modules
terraform init -upgrade

# View module registry
terraform providers

# Format module code
cd modules/hub_spoke
terraform fmt
```

### Managing Workspaces (Environments)

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new staging

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show
```

---

## Key Takeaways

### This Project Demonstrates:

1. **Modular Architecture**: Reusable modules for networking, compute, and security
2. **YAML-Driven Configuration**: Data separation from code for easier management
3. **Security Best Practices**: Sensitive variable handling, NSG rules, private networking
4. **Hub-Spoke Topology**: Centralized security and routing through NVA firewall
5. **Dynamic Configuration**: Runtime processing of YAML data with Terraform functions
6. **Production Readiness**: Dependencies, tags, outputs, documentation

### Terraform Advantages in This Project:

- 🚀 **Fast deployment**: Entire hub-spoke + AKS in ~15 minutes
- 📝 **Declarative**: Describe desired state, Terraform handles the rest
- 🔄 **Idempotent**: Run multiple times safely, only changes what's needed
- 👥 **Collaborative**: YAML configs allow non-Terraform users to contribute
- 🔍 **Auditable**: All changes tracked in Git history
- 🧩 **Modular**: Add new spokes/services easily by extending YAML configs

### Next Steps

1. **Add CI/CD Pipeline**: Automate `terraform plan/apply` in GitHub Actions or Azure DevOps
2. **Remote State**: Move state to Azure Storage Account with locking
3. **Multiple Environments**: Use workspaces or separate directories (dev, staging, prod)
4. **Monitoring**: Add Log Analytics, Application Insights resources
5. **Security**: Implement Azure Key Vault for secret management
6. **Testing**: Use `terraform test` or tools like Terratest

---

## Additional Resources

- **Terraform Documentation**: https://www.terraform.io/docs
- **Azure Provider**: https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs
- **Best Practices**: https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html
- **Module Registry**: https://registry.terraform.io/
- **This Project's README**: [terraform/README.md](../terraform/README.md)

---

**Last Updated**: January 2026  
**Project**: devops-kt  
**Author**: pizour
