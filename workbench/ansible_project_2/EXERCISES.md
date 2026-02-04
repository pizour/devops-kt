# Ansible Training Exercises

## 🎓 Exercise Set 1: Understanding the Basics

### Exercise 1.1: Explore the Inventory
**Objective**: Understand how hosts are organized

**Tasks**:
1. Open [inventories/hosts-germany.yml](inventories/hosts-germany.yml)
2. Identify the group name for German hosts
3. List all hostnames in the Germany inventory
4. Run: `ansible-inventory -i inventories/hosts-germany.yml --graph`

**Questions**:
- How many hosts are in the germany group?
- What is the IP address of nva-01-germany-central?
- How would you target only the Germany hosts in a playbook?

### Exercise 1.2: Variable Precedence
**Objective**: Understand how Ansible resolves variables

**Tasks**:
1. Open [group_vars/all.yml](group_vars/all.yml) and note the `max_connections` value
2. Open [group_vars/linux-nvas-germany.yml](group_vars/linux-nvas-germany.yml) and note its value
3. Open [host_vars/nva-01-germany-central.yml](host_vars/nva-01-germany-central.yml) and note its value
4. Run: `ansible-inventory -i inventories/hosts-germany.yml --host nva-01-germany-central`

**Questions**:
- What is the final value of `max_connections` for nva-01-germany-central?
- Why does it have that value?
- Which variable file has the highest precedence?

### Exercise 1.3: First Playbook Run
**Objective**: Execute your first playbook

**Tasks**:
1. Review [gather-info.yml](gather-info.yml)
2. Run: `ansible-playbook -i inventories/hosts-germany.yml gather-info.yml --check`
3. Run: `ansible-playbook -i inventories/hosts-germany.yml gather-info.yml`
4. Check the generated report in `/tmp/<hostname>-report.yml`

**Questions**:
- What is the difference between `--check` mode and normal execution?
- What facts were gathered about your system?
- Where are the facts stored during playbook execution?

---

## 🎓 Exercise Set 2: Working with Roles

### Exercise 2.1: Analyze a Role Structure
**Objective**: Understand role components

**Tasks**:
1. Navigate to [roles/common](roles/common)
2. List all directories: tasks, handlers, templates, defaults
3. Open [roles/common/tasks/main.yml](roles/common/tasks/main.yml)
4. Identify tasks that use loops
5. Find tasks that notify handlers

**Questions**:
- What directories are present in the common role?
- Which handler gets notified when timezone changes?
- How many tasks use loops in the common role?

### Exercise 2.2: Modify a Template
**Objective**: Learn Jinja2 templating

**Tasks**:
1. Open [roles/common/templates/resolv.conf.j2](roles/common/templates/resolv.conf.j2)
2. Identify Jinja2 syntax (variables, loops)
3. Add a comment at the top: `# Custom DNS Configuration for {{ region }}`
4. Test by running the common role

**Questions**:
- What Jinja2 loop is used in the template?
- How are variables referenced in templates?
- What will be the output for the Germany region?

### Exercise 2.3: Create a Simple Role
**Objective**: Build your own role

**Tasks**:
1. Create a new role directory: `roles/monitoring`
2. Create the basic structure:
   ```bash
   mkdir -p roles/monitoring/{tasks,handlers,templates,defaults}
   ```
3. Create `roles/monitoring/tasks/main.yml` with a task to install `htop`
4. Create a simple playbook that uses this role
5. Test your role

**Expected Output**: htop should be installed on target systems

---

## 🎓 Exercise Set 3: Advanced Playbook Features

### Exercise 3.1: Working with Tags
**Objective**: Use tags for selective execution

**Tasks**:
1. Run: `ansible-playbook deploy-infrastructure.yml --list-tags`
2. Run only common tasks: `ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --tags common`
3. Skip database tasks: `ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --skip-tags database`

**Questions**:
- How many different tags are available?
- What is the benefit of using tags?
- Can a task have multiple tags?

### Exercise 3.2: Conditionals and Loops
**Objective**: Master task control flow

**Tasks**:
1. Open [configure-servers.yml](configure-servers.yml)
2. Find a task with a `when` conditional
3. Find a task with a `loop`
4. Modify the `security_packages` variable to add `nmap`
5. Run the playbook and verify nmap is installed

**Questions**:
- What conditions are used in the playbook?
- How do you loop over a list vs. a dictionary?
- Can you combine loops and conditionals?

### Exercise 3.3: Error Handling
**Objective**: Handle failures gracefully

**Tasks**:
1. Open [advanced-concepts.yml](advanced-concepts.yml)
2. Find the block with rescue and always sections
3. Run the playbook: `ansible-playbook -i inventories/hosts-germany.yml advanced-concepts.yml --tags error-handling`
4. Check `/tmp/ansible-errors.log` for logged errors

**Questions**:
- What happens in the rescue block?
- When does the always block execute?
- How would you ignore errors without using block/rescue?

---

## 🎓 Exercise Set 4: Real-World Scenarios

### Exercise 4.1: Deploy a Web Server
**Objective**: Complete web server deployment

**Tasks**:
1. Review [roles/webserver/tasks/main.yml](roles/webserver/tasks/main.yml)
2. Understand the SSL certificate generation task
3. Run: `ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --tags webserver --limit nva-01-germany-central`
4. Verify nginx is running: `ansible -i inventories/hosts-germany.yml nva-01-germany-central -m command -a "systemctl status nginx"`
5. Check the deployed website at http://[host-ip]:[webserver_port]

**Challenge**: Modify the index.html template to add your own custom message

### Exercise 4.2: Database Primary-Replica Setup
**Objective**: Understand conditional role execution

**Tasks**:
1. Review host_vars files to see which hosts are primary vs replica
2. Run: `ansible-playbook -i inventories/hosts-germany.yml deploy-infrastructure.yml --tags database`
3. Observe how tasks differ between primary and replica hosts

**Questions**:
- How does Ansible know which host is primary?
- What tasks run only on replicas?
- Where is the replication source configured?

### Exercise 4.3: Rolling Updates
**Objective**: Learn serial execution

**Tasks**:
1. Review the serial execution play in [advanced-concepts.yml](advanced-concepts.yml)
2. Run: `ansible-playbook -i inventories/hosts-germany.yml advanced-concepts.yml --tags serial`
3. Observe how hosts are processed one at a time

**Questions**:
- Why would you use serial execution?
- What is the default behavior without serial?
- How would you set serial to 2 hosts at a time?

---

## 🎓 Exercise Set 5: Testing and Validation

### Exercise 5.1: Pre-Deployment Validation
**Objective**: Validate before deploying

**Tasks**:
1. Open [test-deployment.yml](test-deployment.yml)
2. Review the assert tasks
3. Run: `ansible-playbook -i inventories/hosts-germany.yml test-deployment.yml`
4. Intentionally change a host_var to break an assertion
5. Re-run and observe the failure

**Questions**:
- What assertions are checking?
- How do you write a good assertion message?
- When should you run validation playbooks?

### Exercise 5.2: Health Checks
**Objective**: Implement service health checks

**Tasks**:
1. Find the health check endpoint in the webserver role
2. Use curl to test it: `curl http://[host-ip]:[port]/health`
3. Review the uri module usage in test-deployment.yml
4. Add a new health check for a different endpoint

**Challenge**: Create a playbook that checks all services are running

### Exercise 5.3: Debugging
**Objective**: Troubleshoot playbook issues

**Tasks**:
1. Intentionally break a task (e.g., wrong package name)
2. Run with verbose mode: `ansible-playbook -vvv ...`
3. Identify the error in the output
4. Fix the issue
5. Use the debug module to print variable values

**Questions**:
- What do different verbosity levels show (-v, -vv, -vvv)?
- How do you debug variable values?
- What information is in the error messages?

---

## 🎓 Exercise Set 6: Custom Modifications

### Exercise 6.1: Add a New Group Variable
**Objective**: Extend the variable structure

**Tasks**:
1. Add a new variable `backup_server` to both region group_vars files
2. Use different values for each region
3. Create a task that uses this variable
4. Run and verify the correct value is used

### Exercise 6.2: Create a New Playbook
**Objective**: Build from scratch

**Tasks**:
1. Create `system-update.yml`
2. Add tasks to:
   - Update package cache
   - Upgrade all packages
   - Reboot if needed
   - Wait for system to come back
3. Test in check mode first
4. Run the playbook

### Exercise 6.3: Extend the Webserver Role
**Objective**: Modify existing roles

**Tasks**:
1. Add a task to create a custom nginx log format
2. Add a template for a custom virtual host
3. Create a handler to reload nginx (not restart)
4. Test your changes

---

## 🏆 Final Challenge: Complete Infrastructure

**Objective**: Put it all together

**Tasks**:
1. Deploy complete infrastructure to all hosts
2. Verify all services are running
3. Run validation playbooks
4. Generate and review all reports
5. Document any issues encountered

**Success Criteria**:
- ✅ All hosts accessible
- ✅ Common configuration applied
- ✅ Web servers running where enabled
- ✅ Databases configured correctly
- ✅ All validation tests pass
- ✅ Health checks responding

---

## 📝 Exercise Solutions

Solutions are intentionally not provided. Work through the exercises, experiment, and learn from mistakes. Use:
- `ansible-playbook --syntax-check`
- `ansible-playbook --check`
- `ansible-playbook -vvv`
- Ansible documentation: https://docs.ansible.com

**Remember**: The best way to learn Ansible is by doing! 🚀

---

## 💡 Tips for Success

1. **Always test in check mode first**
2. **Use tags to test individual components**
3. **Read error messages carefully**
4. **Use debug module liberally**
5. **Start simple and build complexity**
6. **Keep playbooks idempotent**
7. **Document your changes**
8. **Ask questions!**

Good luck with your Ansible journey! 🎉
