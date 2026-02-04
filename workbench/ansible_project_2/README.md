# Ansible Training Project

This is a comprehensive sample Ansible project designed to teach Ansible concepts to junior colleagues. The project demonstrates best practices, common patterns, and various Ansible features.

## 📁 Project Structure

```
ansible_project_1/
├── ansible.cfg                      # Ansible configuration file
├── inventories/                     # Inventory files (host definitions)
│   ├── hosts-germany.yml           # Germany region hosts
│   └── hosts-poland.yml            # Poland region hosts
├── group_vars/                     # Variables for groups of hosts
│   ├── all.yml                     # Variables for all hosts
│   ├── linux-nvas-germany.yml      # Variables for Germany group
│   └── linux-nvas-poland.yml       # Variables for Poland group
├── host_vars/                      # Variables for individual hosts
│   ├── nva-01-germany-central.yml  # Host-specific variables
│   ├── nva-02-germany-north.yml
│   ├── nva-01-poland-west.yml
│   └── nva-02-poland-central.yml
├── roles/                          # Reusable role definitions
│   ├── bootstrap_python/           # Python installation role
│   ├── common/                     # Common configuration role
│   ├── webserver/                  # Nginx web server role
│   └── database/                   # PostgreSQL database role
├── templates/                      # Jinja2 templates
│   └── server-info.txt.j2
└── playbooks/                      # Ansible playbooks
    ├── deploy-infrastructure.yml   # Complete infrastructure deployment
    ├── configure-servers.yml       # Server configuration management
    ├── gather-info.yml             # Information gathering
    ├── advanced-concepts.yml       # Advanced Ansible features
    └── test-deployment.yml         # Validation and testing
```

## 🎯 Learning Objectives

This project covers the following Ansible concepts:

### 1. **Inventory Management**
- Static inventory files (YAML format)
- Host grouping and hierarchy
- Host and group variables

### 2. **Variable Precedence**
- `group_vars/all.yml` - Lowest precedence
- `group_vars/<group_name>.yml` - Group-specific variables
- `host_vars/<hostname>.yml` - Highest precedence
- Variables in playbooks and roles

### 3. **Roles**
- **bootstrap_python**: Installing Python on target systems
- **common**: Common configuration tasks (timezone, users, directories)
- **webserver**: Nginx installation and configuration
- **database**: PostgreSQL setup with primary/replica support

### 4. **Playbooks**
- **deploy-infrastructure.yml**: Multi-play deployment with roles
- **configure-servers.yml**: Tasks, loops, conditionals, filters
- **gather-info.yml**: Facts gathering and system information
- **advanced-concepts.yml**: Error handling, delegation, serial execution
- **test-deployment.yml**: Assertions and validation

### 5. **Key Ansible Features Demonstrated**
- ✅ Tasks and modules
- ✅ Variables and facts
- ✅ Templates (Jinja2)
- ✅ Handlers
- ✅ Loops and conditionals
- ✅ Blocks and error handling
- ✅ Tags
- ✅ Delegation
- ✅ Filters
- ✅ Assertions and testing

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ansible
pip install ansible

# Install required collections
ansible-galaxy collection install community.general
ansible-galaxy collection install community.postgresql
```

### Running Playbooks

1. **Basic deployment to Germany region:**
```bash
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml
```

2. **Deploy to specific host:**
```bash
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --limit nva-01-germany-central
```

3. **Run specific role only:**
```bash
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --tags common
```

4. **Check mode (dry-run):**
```bash
ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --check
```

5. **Gather system information:**
```bash
ansible-playbook -i inventories/hosts-germany.yml gather-info.yml
```

6. **Test deployment:**
```bash
ansible-playbook -i inventories/hosts-germany.yml test-deployment.yml
```

## 📚 Training Exercises

### Exercise 1: Understanding Variables
1. Review the variable files in `group_vars/` and `host_vars/`
2. Note how `max_connections` is overridden at different levels
3. Understand variable precedence by checking which value is used

### Exercise 2: Running Your First Playbook
1. Start with `gather-info.yml` to understand your target hosts
2. Observe how facts are gathered and displayed
3. Check the generated reports in `/tmp/`

### Exercise 3: Deploying Infrastructure
1. Run `deploy-infrastructure.yml` step by step
2. Use tags to run specific parts: `--tags common`, `--tags webserver`
3. Check what changed on the target systems

### Exercise 4: Working with Roles
1. Examine the structure of the `common` role
2. Understand how tasks, handlers, templates, and defaults work together
3. Modify a template and see the changes

### Exercise 5: Advanced Concepts
1. Run `advanced-concepts.yml` to see error handling in action
2. Understand blocks, rescue, and always sections
3. Learn about delegation and serial execution

### Exercise 6: Testing and Validation
1. Run `test-deployment.yml` to validate your deployment
2. Study the assertions and how they verify configuration
3. Intentionally break something and see how validation catches it

## 🔧 Common Commands

```bash
# List all hosts in inventory
ansible -i inventories/hosts-germany.yml all --list-hosts

# Ping all hosts
ansible -i inventories/hosts-germany.yml all -m ping

# Check facts for a specific host
ansible -i inventories/hosts-germany.yml nva-01-germany-central -m setup

# Run ad-hoc command
ansible -i inventories/hosts-germany.yml all -m command -a "uptime"

# Validate playbook syntax
ansible-playbook --syntax-check deploy-infrastructure.yml

# List all tags in a playbook
ansible-playbook deploy-infrastructure.yml --list-tags

# List all tasks in a playbook
ansible-playbook deploy-infrastructure.yml --list-tasks
```

## 📖 Key Concepts Explained

### Inventory
Defines your managed hosts and how they're grouped. Each host can belong to multiple groups.

### Variables
Configuration data that can be used in playbooks and templates. Ansible has a clear variable precedence order.

### Roles
Reusable, standardized units of automation. A role includes tasks, handlers, files, templates, and variables.

### Playbooks
YAML files that define automation workflows. Can contain multiple plays targeting different hosts.

### Tasks
Individual actions to be performed (install package, copy file, start service, etc.).

### Handlers
Special tasks that only run when notified by other tasks (e.g., restart a service after config change).

### Templates
Jinja2 template files that allow dynamic content generation based on variables.

### Facts
System information automatically gathered by Ansible about target hosts.

### Tags
Labels for tasks that allow selective execution of parts of a playbook.

## 🎓 Teaching Tips

1. **Start Simple**: Begin with `gather-info.yml` to understand facts
2. **Build Gradually**: Move from simple tasks to complex roles
3. **Use Check Mode**: Always demonstrate `--check` for safe testing
4. **Show Idempotency**: Run playbooks multiple times to show they're safe
5. **Demonstrate Tags**: Show how to run specific parts of playbooks
6. **Error Handling**: Intentionally break things to show error messages
7. **Variables**: Explain precedence by modifying values at different levels

## 🔍 Troubleshooting

### Connection Issues
```bash
# Test SSH connectivity
ansible -i inventories/hosts-germany.yml all -m ping

# Use verbose mode for debugging
ansible-playbook -vvv deploy-infrastructure.yml
```

### Syntax Errors
```bash
# Validate YAML syntax
ansible-playbook --syntax-check <playbook.yml>

# Validate inventory
ansible-inventory -i inventories/hosts-germany.yml --list
```

### Variable Issues
```bash
# Display all variables for a host
ansible -i inventories/hosts-germany.yml nva-01-germany-central -m debug -a "var=hostvars[inventory_hostname]"
```

## 📝 Best Practices Demonstrated

1. ✅ **Organized directory structure** with separate folders for different components
2. ✅ **Role-based architecture** for reusability
3. ✅ **Variable separation** using group_vars and host_vars
4. ✅ **Templating** for dynamic configuration
5. ✅ **Error handling** with blocks and rescue
6. ✅ **Idempotent tasks** that can be run multiple times safely
7. ✅ **Tags** for selective execution
8. ✅ **Documentation** with comments in playbooks and roles
9. ✅ **Testing and validation** with assertions
10. ✅ **Handler usage** for service restarts

## 🌟 Next Steps

After mastering this project, explore:
- Ansible Vault for secrets management
- Dynamic inventories
- Custom modules
- Ansible Tower/AWX
- CI/CD integration
- Ansible Collections

## 📞 Support

For questions about this training project:
1. Review the comments in playbooks and roles
2. Check Ansible documentation: https://docs.ansible.com
3. Experiment in check mode first
4. Use `-vvv` for detailed output

---

**Happy Learning! 🚀**
