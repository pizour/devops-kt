# Ansible Project 2 - Multi-Environment Infrastructure

This is a comprehensive Ansible training project demonstrating **multi-environment management** with separate development and production configurations. The project showcases bastion host security and Fossology application deployment.

## 📁 Project Structure

```
ansible_project_2/
├── ansible.cfg                  # Ansible configuration
├── dev/                        # Development environment
│   ├── hosts                   # Dev inventory file
│   ├── group_vars/            # Dev group variables
│   │   ├── all.yml
│   │   ├── bastion.yml
│   │   └── fossology.yml
│   └── host_vars/             # Dev host-specific vars
│       ├── bastion_private
│       ├── bastion_public
│       └── fossology-app
├── prod/                       # Production environment
│   ├── hosts                   # Prod inventory file
│   ├── group_vars/            # Prod group variables
│   │   ├── all.yml
│   │   ├── bastion.yml
│   │   └── fossology.yml
│   └── host_vars/             # Prod host-specific vars
│       ├── bastion_private
│       ├── bastion_public
│       └── fossology-app
├── roles/                      # Reusable roles
│   ├── common/                # Base configuration
│   ├── security/              # Security hardening
│   ├── bastion/               # Bastion/jump host
│   └── fossology/             # Fossology application
└── playbooks/                  # Ansible playbooks
    ├── site.yml               # Complete infrastructure
    ├── pb_update_linux_packages.yml
    ├── gather-system-info.yml
    ├── security-hardening.yml
    └── test-deployment.yml
```

## 🎯 Key Features

### Multi-Environment Support
- **Separate inventories** for dev and prod
- **Environment-specific variables** (resource allocation, security settings)
- **Flexible deployment** - choose environment with `-i` flag

### Infrastructure Components
1. **Bastion Hosts** (Jump/Gateway servers)
   - Private bastion (internal access)
   - Public bastion (external access with enhanced security)
   - Session logging and auditing
   - SSH hardening and fail2ban

2. **Fossology Application Servers**
   - Open source license compliance system
   - Apache web server
   - PostgreSQL database
   - Automated backups

### Roles Overview

#### 1. **common** - Base Configuration
- Hostname configuration
- Package management
- Directory structure
- Time synchronization
- Health monitoring

#### 2. **security** - Security Hardening
- SSH hardening
- Firewall configuration (UFW)
- Fail2ban setup
- Automatic security updates
- System auditing

#### 3. **bastion** - Jump Host Configuration
- Session logging
- TCP/Agent forwarding control
- Connection monitoring
- Bastion-specific tools
- Enhanced SSH configuration

#### 4. **fossology** - Application Deployment
- Apache web server
- PostgreSQL database
- PHP configuration
- Application directory structure
- Backup scripts
- Virtual host configuration

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ansible
pip install ansible

# Install required collections
ansible-galaxy collection install community.general
ansible-galaxy collection install community.postgresql
ansible-galaxy collection install ansible.posix
```

### Deploying to Development

```bash
# Deploy complete infrastructure to dev
ansible-playbook -i dev/hosts site.yml

# Deploy to specific host
ansible-playbook -i dev/hosts site.yml --limit bastion_private

# Deploy specific role
ansible-playbook -i dev/hosts site.yml --tags bastion

# Check mode (dry run)
ansible-playbook -i dev/hosts site.yml --check
```

### Deploying to Production

```bash
# ALWAYS use check mode first in production!
ansible-playbook -i prod/hosts site.yml --check

# Deploy to production
ansible-playbook -i prod/hosts site.yml

# Deploy with extra caution (one host at a time)
ansible-playbook -i prod/hosts site.yml --serial 1
```

### Common Operations

```bash
# Update packages on all hosts
ansible-playbook -i dev/hosts pb_update_linux_packages.yml

# Gather system information
ansible-playbook -i dev/hosts gather-system-info.yml

# Apply security hardening
ansible-playbook -i prod/hosts security-hardening.yml

# Test and validate deployment
ansible-playbook -i dev/hosts test-deployment.yml

# Ad-hoc commands
ansible -i dev/hosts all -m ping
ansible -i dev/hosts bastion -m command -a "uptime"
```

## 📚 Key Ansible Concepts Demonstrated

### 1. **Multi-Environment Management**
```bash
# Development deployment
ansible-playbook -i dev/hosts site.yml

# Production deployment  
ansible-playbook -i prod/hosts site.yml
```

### 2. **Variable Precedence**
- `group_vars/all.yml` - All hosts in environment
- `group_vars/bastion.yml` - All bastion hosts
- `host_vars/bastion_private` - Specific host (highest precedence)

### 3. **Inventory Organization**
```ini
[bastion]
bastion_private ansible_host=10.120.11.20
bastion_public ansible_host=31.69.51.11

[bastion:vars]
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### 4. **Proxy Jump (SSH Bastion)**
The inventory demonstrates SSH proxy jumping through bastion:
```ini
ansible_ssh_common_args='-o ProxyCommand="ssh -W %h:%p user@bastion-host"'
```

### 5. **Conditionals Based on Environment**
```yaml
- name: Install extra security tools
  package:
    name: "{{ extra_packages }}"
  when: environment == "production"
```

### 6. **Templates with Environment Variables**
Templates automatically use correct values based on environment:
```jinja2
# {{ environment }} environment configuration
max_connections = {{ db_max_connections }}
```

## 🔧 Environment Differences

### Development Environment
- **Lower resources** (2-4GB RAM, 2-4 CPUs)
- **Debug mode enabled** for easier troubleshooting
- **Less restrictive security** (SSH from anywhere)
- **Shorter backup retention** (7 days)
- **More verbose logging**
- **Sample data loaded**

### Production Environment
- **Higher resources** (4-16GB RAM, 4-8 CPUs)
- **Debug mode disabled** for performance
- **Strict security** (whitelisted IPs, 2FA ready)
- **Extended backup retention** (30 days)
- **Optimized logging**
- **Performance tuning enabled**
- **Monitoring and alerting configured**

## 📖 Playbook Guide

### site.yml - Complete Deployment
Deploys entire infrastructure in correct order:
1. Common configuration (all hosts)
2. Security hardening (all hosts)
3. Bastion configuration (bastion group)
4. Fossology application (fossology group)

### pb_update_linux_packages.yml - Package Updates
Updates all packages on all systems. Safe for regular maintenance.

### gather-system-info.yml - Information Gathering
Collects and displays system information, creates reports.

### security-hardening.yml - Security Configuration
Applies security best practices:
- Kernel parameters
- Password policies
- Audit rules
- Security scanning

### test-deployment.yml - Validation
Validates deployment with assertions:
- Configuration checks
- Service status
- Port availability
- File existence

## 🎓 Training Exercises

### Exercise 1: Deploy to Development
```bash
# Deploy everything to dev
ansible-playbook -i dev/hosts site.yml

# Verify deployment
ansible-playbook -i dev/hosts test-deployment.yml

# Check system info
ansible-playbook -i dev/hosts gather-system-info.yml
```

### Exercise 2: Understand Environment Differences
```bash
# Compare dev and prod configurations
diff dev/group_vars/all.yml prod/group_vars/all.yml

# Deploy to both and compare
ansible-playbook -i dev/hosts gather-system-info.yml
ansible-playbook -i prod/hosts gather-system-info.yml
```

### Exercise 3: Test SSH Bastion
```bash
# Test connection through bastion
ssh -J bastion_public@31.69.51.11 ubuntu@10.20.191.10

# Use the bastion-connect helper (after deployment)
# On bastion: bastion-connect fossology-app
```

### Exercise 4: Security Hardening
```bash
# Apply security hardening
ansible-playbook -i prod/hosts security-hardening.yml --check
ansible-playbook -i prod/hosts security-hardening.yml

# Run security scan
ansible -i prod/hosts all -a "/opt/scripts/security-scan.sh"
```

### Exercise 5: Selective Deployment
```bash
# Deploy only bastion configuration
ansible-playbook -i dev/hosts site.yml --tags bastion

# Deploy to one host only
ansible-playbook -i dev/hosts site.yml --limit bastion_public

# Skip certain roles
ansible-playbook -i dev/hosts site.yml --skip-tags fossology
```

## 🔍 Troubleshooting

### Connection Issues
```bash
# Test basic connectivity
ansible -i dev/hosts all -m ping

# Test through bastion
ansible -i dev/hosts fossology -m ping -vvv

# Check SSH configuration
ansible -i dev/hosts bastion -m command -a "sshd -T"
```

### Variable Issues
```bash
# View all variables for a host
ansible-inventory -i dev/hosts --host bastion_private

# View inventory structure
ansible-inventory -i dev/hosts --graph

# List all hosts
ansible -i dev/hosts all --list-hosts
```

### Debugging Playbooks
```bash
# Verbose output
ansible-playbook -i dev/hosts site.yml -v
ansible-playbook -i dev/hosts site.yml -vv
ansible-playbook -i dev/hosts site.yml -vvv

# Syntax check
ansible-playbook site.yml --syntax-check

# List tasks
ansible-playbook site.yml --list-tasks

# Start at specific task
ansible-playbook -i dev/hosts site.yml --start-at-task "Install Fossology dependencies"
```

## 💡 Best Practices Demonstrated

1. ✅ **Environment separation** with dedicated inventory directories
2. ✅ **Security layering** (bastion hosts, firewall, fail2ban)
3. ✅ **Variable organization** by environment and host
4. ✅ **Role-based architecture** for reusability
5. ✅ **Idempotent playbooks** safe to run multiple times
6. ✅ **Check mode support** for safe testing
7. ✅ **Comprehensive logging** and monitoring
8. ✅ **Backup automation** with retention policies
9. ✅ **Documentation** in playbooks and roles
10. ✅ **Validation and testing** built into workflows

## 🌟 Advanced Topics

### SSH Proxy Jump Configuration
The inventory uses ProxyCommand for bastion jumping:
```ini
ansible_ssh_common_args='-o ProxyCommand="ssh -W %h:%p user@bastion"'
```

### Environment-Specific Overrides
```yaml
# Production gets more resources
# In prod/group_vars/all.yml
app_max_memory: "4G"

# Development gets less
# In dev/group_vars/all.yml
app_max_memory: "2G"
```

### Dynamic Security Based on Environment
```yaml
# Stricter in production
when: environment == "production"
```

## 📞 Quick Reference

```bash
# Deploy to dev
ansible-playbook -i dev/hosts site.yml

# Deploy to prod (with check first!)
ansible-playbook -i prod/hosts site.yml --check
ansible-playbook -i prod/hosts site.yml

# Update packages
ansible-playbook -i dev/hosts pb_update_linux_packages.yml

# Security hardening
ansible-playbook -i prod/hosts security-hardening.yml

# Test deployment
ansible-playbook -i dev/hosts test-deployment.yml

# Gather info
ansible-playbook -i dev/hosts gather-system-info.yml
```

---

**Happy Learning! 🚀**

See also:
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for command cheat sheet
- [EXERCISES.md](EXERCISES.md) for hands-on practice
