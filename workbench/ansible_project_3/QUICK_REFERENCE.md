# Ansible Quick Reference - Project 2

## 🎯 Environment-Specific Commands

### Development Environment
```bash
# Full deployment
ansible-playbook -i dev/hosts site.yml

# Check mode (dry run)
ansible-playbook -i dev/hosts site.yml --check

# Specific host
ansible-playbook -i dev/hosts site.yml --limit bastion_private

# Specific role
ansible-playbook -i dev/hosts site.yml --tags bastion
```

### Production Environment
```bash
# ALWAYS check first in production!
ansible-playbook -i prod/hosts site.yml --check

# Full deployment
ansible-playbook -i prod/hosts site.yml

# Serial deployment (one at a time)
ansible-playbook -i prod/hosts site.yml --serial 1

# With confirmation
ansible-playbook -i prod/hosts site.yml --step
```

## 📋 Inventory Commands

```bash
# List all hosts in dev
ansible -i dev/hosts all --list-hosts

# List production hosts
ansible -i prod/hosts all --list-hosts

# List bastion hosts only
ansible -i dev/hosts bastion --list-hosts

# View inventory structure
ansible-inventory -i dev/hosts --graph
ansible-inventory -i prod/hosts --graph

# View all variables for a host
ansible-inventory -i dev/hosts --host bastion_private
ansible-inventory -i prod/hosts --host fossology-app

# List groups
ansible -i dev/hosts --list-hosts all
```

## 🔧 Ad-hoc Commands

### Connection Testing
```bash
# Ping all dev hosts
ansible -i dev/hosts all -m ping

# Ping production
ansible -i prod/hosts all -m ping

# Test bastion connectivity
ansible -i dev/hosts bastion -m ping

# Test Fossology app
ansible -i dev/hosts fossology -m ping
```

### System Information
```bash
# Check uptime
ansible -i dev/hosts all -m command -a "uptime"

# Get disk space
ansible -i dev/hosts all -m command -a "df -h"

# Check memory
ansible -i dev/hosts all -m command -a "free -h"

# List running services
ansible -i dev/hosts all -m command -a "systemctl list-units --type=service --state=running"

# Gather facts
ansible -i dev/hosts all -m setup

# Gather specific facts
ansible -i dev/hosts all -m setup -a "filter=ansible_os_family"
```

### Service Management
```bash
# Check service status
ansible -i dev/hosts all -m systemd -a "name=ssh state=started" --check

# Restart Apache (on Fossology)
ansible -i dev/hosts fossology -m service -a "name=apache2 state=restarted" --become

# Check PostgreSQL status
ansible -i dev/hosts fossology -m systemd -a "name=postgresql" --become
```

## 📖 Playbook Commands

### Main Playbooks
```bash
# Complete infrastructure deployment
ansible-playbook -i dev/hosts site.yml
ansible-playbook -i prod/hosts site.yml --check

# Package updates
ansible-playbook -i dev/hosts pb_update_linux_packages.yml
ansible-playbook -i prod/hosts pb_update_linux_packages.yml --check

# System information gathering
ansible-playbook -i dev/hosts gather-system-info.yml
ansible-playbook -i prod/hosts gather-system-info.yml

# Security hardening
ansible-playbook -i dev/hosts security-hardening.yml
ansible-playbook -i prod/hosts security-hardening.yml --check

# Testing and validation
ansible-playbook -i dev/hosts test-deployment.yml
ansible-playbook -i prod/hosts test-deployment.yml
```

### Playbook Options
```bash
# Check syntax
ansible-playbook site.yml --syntax-check

# List all tasks
ansible-playbook site.yml --list-tasks

# List all tags
ansible-playbook site.yml --list-tags

# Verbose output
ansible-playbook -i dev/hosts site.yml -v
ansible-playbook -i dev/hosts site.yml -vv
ansible-playbook -i dev/hosts site.yml -vvv

# Start at specific task
ansible-playbook -i dev/hosts site.yml --start-at-task "Install Fossology dependencies"

# Run specific tags
ansible-playbook -i dev/hosts site.yml --tags "common,security"

# Skip tags
ansible-playbook -i dev/hosts site.yml --skip-tags "fossology"

# Limit to hosts
ansible-playbook -i dev/hosts site.yml --limit "bastion"
ansible-playbook -i dev/hosts site.yml --limit "bastion_private,bastion_public"
```

## 🏷️ Common Tags

```bash
# By role
--tags common
--tags security
--tags bastion
--tags fossology

# By function
--tags packages
--tags config
--tags services
--tags backup
--tags monitoring

# By component
--tags ssh
--tags firewall
--tags database
--tags web
```

## 🔍 Debugging Commands

### Variable Inspection
```bash
# All variables for a host
ansible-inventory -i dev/hosts --host bastion_private

# Check variable precedence
ansible -i dev/hosts bastion_private -m debug -a "var=hostvars[inventory_hostname]"

# Check specific variable
ansible -i dev/hosts all -m debug -a "var=environment"
ansible -i dev/hosts all -m debug -a "var=server_role"
```

### Connection Debugging
```bash
# Very verbose connection debug
ansible -i dev/hosts all -m ping -vvvv

# Check SSH configuration
ansible -i dev/hosts bastion -m command -a "sshd -T" --become

# Test connection through proxy
ansible -i dev/hosts fossology -m ping -vvv
```

### Playbook Debugging
```bash
# Syntax check
ansible-playbook site.yml --syntax-check

# Step through playbook
ansible-playbook -i dev/hosts site.yml --step

# Check mode (dry run)
ansible-playbook -i dev/hosts site.yml --check

# Diff mode (show changes)
ansible-playbook -i dev/hosts site.yml --check --diff
```

## 🛡️ Security Commands

### SSH and Bastion
```bash
# Check SSH configuration
ansible -i dev/hosts bastion -a "sshd -T" --become

# View fail2ban status
ansible -i dev/hosts bastion -a "fail2ban-client status sshd" --become

# Check firewall status
ansible -i dev/hosts all -a "ufw status verbose" --become

# View active connections
ansible -i dev/hosts bastion -a "ss -tuln" --become

# Check session logs
ansible -i dev/hosts bastion -a "ls -lh /var/log/bastion-sessions/" --become
```

### Security Scanning
```bash
# Run security scan
ansible -i prod/hosts all -a "/opt/scripts/security-scan.sh" --become

# Check failed logins
ansible -i prod/hosts all -a "grep 'Failed password' /var/log/auth.log | tail -20" --become

# View active users
ansible -i dev/hosts all -m command -a "who"
```

## 💾 Backup and Maintenance

```bash
# Run Fossology backup
ansible -i prod/hosts fossology -a "/opt/scripts/fossology-backup.sh" --become

# Check backup files
ansible -i prod/hosts fossology -a "ls -lh /opt/backups/" --become

# Run health check
ansible -i dev/hosts all -a "/opt/scripts/health-check.sh" --become

# Check bastion status
ansible -i dev/hosts bastion -a "/opt/scripts/bastion-status.sh" --become
```

## 📊 Monitoring Commands

```bash
# System health
ansible -i dev/hosts all -m command -a "uptime"

# Disk usage
ansible -i dev/hosts all -m shell -a "df -h | grep -v tmpfs"

# Memory usage
ansible -i dev/hosts all -m command -a "free -h"

# Top processes
ansible -i dev/hosts all -m shell -a "ps aux | head -20"

# Network connections
ansible -i dev/hosts all -m command -a "ss -tuln" --become

# Service status
ansible -i dev/hosts fossology -m systemd -a "name=apache2" --become
ansible -i dev/hosts fossology -m systemd -a "name=postgresql" --become
```

## 🔄 Common Workflows

### Complete Dev Deployment
```bash
# 1. Check syntax
ansible-playbook site.yml --syntax-check

# 2. Test with check mode
ansible-playbook -i dev/hosts site.yml --check

# 3. Deploy
ansible-playbook -i dev/hosts site.yml

# 4. Validate
ansible-playbook -i dev/hosts test-deployment.yml

# 5. Gather info
ansible-playbook -i dev/hosts gather-system-info.yml
```

### Production Deployment (Safe)
```bash
# 1. Always start with check mode
ansible-playbook -i prod/hosts site.yml --check

# 2. Review changes with diff
ansible-playbook -i prod/hosts site.yml --check --diff

# 3. Deploy to one host first
ansible-playbook -i prod/hosts site.yml --limit bastion_private

# 4. If successful, deploy to all
ansible-playbook -i prod/hosts site.yml

# 5. Validate everything
ansible-playbook -i prod/hosts test-deployment.yml
```

### Security Hardening Workflow
```bash
# 1. Check current state
ansible-playbook -i prod/hosts gather-system-info.yml

# 2. Test hardening
ansible-playbook -i prod/hosts security-hardening.yml --check

# 3. Apply hardening
ansible-playbook -i prod/hosts security-hardening.yml

# 4. Validate security
ansible -i prod/hosts all -a "/opt/scripts/security-scan.sh" --become
```

### Package Update Workflow
```bash
# 1. Check for updates
ansible -i dev/hosts all -m apt -a "update_cache=yes" --check --become

# 2. Test update playbook
ansible-playbook -i dev/hosts pb_update_linux_packages.yml --check

# 3. Update dev first
ansible-playbook -i dev/hosts pb_update_linux_packages.yml

# 4. If successful, update prod
ansible-playbook -i prod/hosts pb_update_linux_packages.yml --check
ansible-playbook -i prod/hosts pb_update_linux_packages.yml
```

## 🎯 Environment Comparison

```bash
# Compare inventory files
diff dev/hosts prod/hosts

# Compare variables
diff dev/group_vars/all.yml prod/group_vars/all.yml
diff dev/group_vars/bastion.yml prod/group_vars/bastion.yml

# Compare configurations
ansible-inventory -i dev/hosts --host bastion_private > /tmp/dev-bastion.txt
ansible-inventory -i prod/hosts --host bastion_private > /tmp/prod-bastion.txt
diff /tmp/dev-bastion.txt /tmp/prod-bastion.txt
```

## 📚 Documentation

```bash
# Module documentation
ansible-doc apt
ansible-doc systemd
ansible-doc copy
ansible-doc template

# List all modules
ansible-doc -l

# Search for modules
ansible-doc -l | grep firewall
ansible-doc -l | grep postgres
```

## 💡 Pro Tips

```bash
# Create alias for common commands
alias ans-dev='ansible-playbook -i dev/hosts'
alias ans-prod='ansible-playbook -i prod/hosts'
alias ans-check='ansible-playbook --check --diff'

# Use them
ans-dev site.yml
ans-prod site.yml --check

# Save output to file
ansible-playbook -i dev/hosts site.yml | tee deployment.log

# Time execution
time ansible-playbook -i dev/hosts site.yml

# Parallel execution (default is 5)
ansible-playbook -i dev/hosts site.yml --forks 10
```

---

**Keep this reference handy during operations! 📖**
