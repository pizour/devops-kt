# Ansible Quick Reference Guide

## 🎯 Common Ansible Commands

### Inventory Commands
```bash
# List all hosts
ansible -i inventories/hosts-germany.yml all --list-hosts

# List hosts in specific group
ansible -i inventories/hosts-germany.yml linux-nvas-germany --list-hosts

# View inventory graph
ansible-inventory -i inventories/hosts-germany.yml --graph

# View all variables for a host
ansible-inventory -i inventories/hosts-germany.yml --host nva-01-germany-central
```

### Ad-hoc Commands
```bash
# Ping all hosts
ansible -i inventories/hosts-germany.yml all -m ping

# Run shell command
ansible -i inventories/hosts-germany.yml all -m command -a "uptime"

# Gather facts
ansible -i inventories/hosts-germany.yml all -m setup

# Copy file
ansible -i inventories/hosts-germany.yml all -m copy -a "src=/local/file dest=/remote/file"

# Install package
ansible -i inventories/hosts-germany.yml all -m apt -a "name=vim state=present" --become
```

### Playbook Commands
```bash
# Run playbook
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml

# Check syntax
ansible-playbook deploy-infrastructure.yml --syntax-check

# Dry run (check mode)
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --check

# Run with specific tags
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --tags "common,webserver"

# Skip specific tags
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --skip-tags "database"

# Limit to specific hosts
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --limit nva-01-germany-central

# Verbose output
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml -v    # verbose
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml -vv   # more verbose
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml -vvv  # debug

# List all tasks
ansible-playbook deploy-infrastructure.yml --list-tasks

# List all tags
ansible-playbook deploy-infrastructure.yml --list-tags

# Start at specific task
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --start-at-task "Install nginx"
```

## 📋 Playbook Examples

### Basic Playbook Structure
```yaml
---
- name: Playbook description
  hosts: all                    # Target hosts/groups
  gather_facts: yes            # Gather system facts
  become: yes                  # Run with sudo
  
  vars:
    variable_name: value       # Playbook variables
  
  tasks:
    - name: Task description
      module_name:
        parameter: value
```

### Task with Conditional
```yaml
- name: Install package on Debian
  apt:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"
```

### Task with Loop
```yaml
- name: Create multiple users
  user:
    name: "{{ item }}"
    state: present
  loop:
    - alice
    - bob
    - charlie
```

### Task with Handler
```yaml
tasks:
  - name: Copy nginx config
    copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
    notify: restart nginx

handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
```

## 🎲 Variable Precedence (Low to High)

1. Command line values (e.g., -e "var=value")
2. Role defaults (roles/role_name/defaults/main.yml)
3. Inventory file or script group vars
4. Inventory group_vars/all
5. Playbook group_vars/all
6. Inventory group_vars/*
7. Playbook group_vars/*
8. Inventory file or script host vars
9. Inventory host_vars/*
10. Playbook host_vars/*
11. Host facts / cached set_facts
12. Play vars
13. Play vars_prompt
14. Play vars_files
15. Role vars (roles/role_name/vars/main.yml)
16. Block vars (only for tasks in block)
17. Task vars (only for the task)
18. Include_vars
19. Set_facts / registered vars
20. Role (and include_role) params
21. Include params
22. Extra vars (always win precedence: -e)

## 🔧 Useful Modules

### Files & Directories
- `file` - Manage files and directories
- `copy` - Copy files to remote hosts
- `template` - Template a file to remote hosts
- `lineinfile` - Ensure a line is in a file
- `blockinfile` - Insert/update/remove a block of lines

### Packages
- `package` - Generic package manager
- `apt` - Debian/Ubuntu package manager
- `yum` - RedHat/CentOS package manager
- `pip` - Python package manager

### Services
- `service` - Manage services
- `systemd` - Systemd service manager

### Commands
- `command` - Execute commands (doesn't use shell)
- `shell` - Execute shell commands
- `raw` - Execute raw commands (no Python needed)

### Users & Groups
- `user` - Manage user accounts
- `group` - Manage groups

### System
- `hostname` - Manage hostname
- `timezone` - Configure timezone
- `reboot` - Reboot a machine
- `setup` - Gather facts

## 🎨 Jinja2 Filters

```yaml
# String manipulation
{{ hostname | upper }}                    # HOSTNAME
{{ hostname | lower }}                    # hostname
{{ hostname | capitalize }}               # Hostname
{{ hostname | replace('old', 'new') }}   # Replace text

# Default values
{{ undefined_var | default('default') }}  # Set default value

# Lists
{{ list | join(', ') }}                   # Join list items
{{ list | first }}                        # First item
{{ list | last }}                         # Last item
{{ list | length }}                       # List length

# Dictionaries
{{ dict | dict2items }}                   # Convert to list of key-value pairs

# Numbers
{{ number | int }}                        # Convert to integer
{{ number | float }}                      # Convert to float
{{ number | abs }}                        # Absolute value

# JSON/YAML
{{ data | to_json }}                      # Convert to JSON
{{ data | to_yaml }}                      # Convert to YAML
{{ data | to_nice_json }}                 # Pretty JSON
{{ data | to_nice_yaml }}                 # Pretty YAML

# Path manipulation
{{ path | basename }}                     # Get filename
{{ path | dirname }}                      # Get directory
{{ path | splitext }}                     # Split extension
```

## 📦 Common Patterns

### Block with Error Handling
```yaml
- name: Handle errors gracefully
  block:
    - name: Risky task
      command: /bin/risky-command
  rescue:
    - name: Handle error
      debug:
        msg: "Task failed, but we handled it"
  always:
    - name: Always runs
      debug:
        msg: "This runs no matter what"
```

### Delegation
```yaml
- name: Run on different host
  command: echo "Hello"
  delegate_to: localhost
  run_once: yes
```

### Register and Debug
```yaml
- name: Execute command
  command: whoami
  register: command_output

- name: Display output
  debug:
    var: command_output.stdout
```

### Loop with Dictionary
```yaml
- name: Create users with properties
  user:
    name: "{{ item.name }}"
    state: "{{ item.state }}"
  loop:
    - { name: 'alice', state: 'present' }
    - { name: 'bob', state: 'present' }
```

## 🏷️ Best Practices

1. ✅ Always use `become` instead of `sudo`
2. ✅ Use `package` module for OS-agnostic package installation
3. ✅ Always name your tasks descriptively
4. ✅ Use `check_mode` for testing
5. ✅ Tag your tasks for selective execution
6. ✅ Use handlers for service restarts
7. ✅ Keep playbooks idempotent
8. ✅ Use roles for reusability
9. ✅ Store secrets in Ansible Vault
10. ✅ Use `--syntax-check` before running playbooks

## 🐛 Debugging

```bash
# Verbose output
ansible-playbook playbook.yml -vvv

# Debug module
- debug:
    var: variable_name
    
- debug:
    msg: "Variable value is {{ variable_name }}"

# Check variable
- debug:
    var: hostvars[inventory_hostname]

# Pause for debugging
- pause:
    prompt: "Press Enter to continue"
```

## 📚 Documentation

```bash
# Module documentation
ansible-doc <module_name>
ansible-doc copy
ansible-doc apt

# List all modules
ansible-doc -l

# Search modules
ansible-doc -l | grep <keyword>
```

---

**Keep this guide handy during training sessions! 📖**
