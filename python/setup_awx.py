#!/usr/bin/env python3
"""
AWX Project and Job Template Setup Script

This script creates:
1. An AWX project pointing to the devops-kt Git repository
2. A job template using the simple-playbook.yaml with default inventory

Setup:
  1. Get the password: kubectl -n awx get secret awx-demo-admin-password -o jsonpath='{.data.password}' | base64 -d
  2. Start port-forward: kubectl -n awx port-forward svc/awx-demo-service 8080:80 &
  3. Run this script: python3 setup_awx.py
"""

import requests
import json
import sys
from urllib.parse import urljoin
import time

# AWX Configuration
AWX_HOST = "http://localhost:8080"  # Use port-forward: kubectl -n awx port-forward svc/awx-demo-service 8080:80
AWX_USERNAME = ""
AWX_PASSWORD = ""  # Will be set from env or arg

# Project Configuration
PROJECT_NAME = "devops-kt"
GIT_URL = "https://github.com/pizour/devops-kt/"

# Job Template Configuration
JOB_TEMPLATE_NAME = "gather-vm-info"
PLAYBOOK_NAME = "ansible/gather-vm-info.yaml"

# Inventory Configuration
INVENTORY_NAME = "devops-kt"
INVENTORY_DESCRIPTION = "DevOps-KT Infrastructure Inventory"

# Hosts to add
HOSTS = [
    {
        "name": "fw-nva",
        "description": "Ubuntu NVA Firewall",
        "variables": {
            "ansible_host": "10.0.0.10",
            "ansible_connection": "ssh",
        }
    }
]


class AWXClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({"Content-Type": "application/json"})

    def get_url(self, endpoint):
        return urljoin(self.host, f"/api/v2/{endpoint}/")

    def get_or_create(self, endpoint, name, data):
        """Get existing resource or create new one"""
        url = self.get_url(endpoint)
        
        # Check if exists
        response = self.session.get(url, params={"name": name})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                print(f"✓ {endpoint} '{name}' already exists (ID: {results[0]['id']})")
                return results[0]
        
        # Create new
        response = self.session.post(url, json=data)
        if response.status_code in [201, 200]:
            result = response.json()
            print(f"✓ Created {endpoint} '{name}' (ID: {result['id']})")
            return result
        else:
            print(f"✗ Failed to create {endpoint} '{name}'")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def get_inventory(self):
        """Get default inventory"""
        url = self.get_url("inventories")
        response = self.session.get(url, params={"name": "Demo Inventory"})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                print(f"✓ Found default inventory (ID: {results[0]['id']})")
                return results[0]
        
        # If not found, get first inventory
        response = self.session.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                print(f"✓ Using inventory: {results[0]['name']} (ID: {results[0]['id']})")
                return results[0]
        
        print("✗ No inventory found")
        return None

    def create_project(self):
        """Create or get AWX project"""
        print(f"\n📦 Setting up project: {PROJECT_NAME}")
        project_data = {
            "name": PROJECT_NAME,
            "description": "DevOps-KT repository",
            "scm_type": "git",
            "scm_url": GIT_URL,
            "scm_branch": "",
            "scm_clean": True,
            "scm_delete_on_update": False,
            "scm_update_on_launch": True,
            "scm_update_cache_timeout": 0,
        }
        
        project = self.get_or_create("projects", PROJECT_NAME, project_data)
        return project

    def create_job_template(self, project, inventory):
        """Create job template"""
        if not project or not inventory:
            print("✗ Cannot create job template without project and inventory")
            return None
        
        print(f"\n🎯 Setting up job template: {JOB_TEMPLATE_NAME}")
        
        # Extra vars for ansible connection
        extra_vars = {
            "ansible_user": "azureuser",
            "ansible_password": "xxx",
        }
        
        job_data = {
            "name": JOB_TEMPLATE_NAME,
            "description": f"Job template for {PLAYBOOK_NAME}",
            "project": project["id"],
            "playbook": PLAYBOOK_NAME,
            "inventory": inventory["id"],
            "ask_inventory": False,
            "ask_credential": False,
            "ask_variables_on_launch": True,
            "verbosity": 0,
            "extra_vars": json.dumps(extra_vars),
            "limit": "",
            "forks": 0,
            "use_fact_cache": False,
        }
        
        url = self.get_url("job_templates")
        
        # Check if exists
        response = self.session.get(url, params={"name": JOB_TEMPLATE_NAME})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                job_template = results[0]
                print(f"✓ {JOB_TEMPLATE_NAME} already exists (ID: {job_template['id']})")
                
                # Update the template with new settings
                update_url = self.get_url(f"job_templates/{job_template['id']}")
                update_response = self.session.patch(update_url, json=job_data)
                if update_response.status_code == 200:
                    print(f"✓ Updated job template settings")
                    return update_response.json()
                return job_template
        
        # Create new
        response = self.session.post(url, json=job_data)
        if response.status_code in [201, 200]:
            result = response.json()
            print(f"✓ Created job template '{JOB_TEMPLATE_NAME}' (ID: {result['id']})")
            return result
        else:
            print(f"✗ Failed to create job template")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def launch_job_template(self, job_template):
        """Launch the job template"""
        if not job_template:
            print("✗ Cannot launch job template")
            return None
        
        print(f"\n🚀 Launching job template: {JOB_TEMPLATE_NAME}")
        url = self.get_url(f"job_templates/{job_template['id']}/launch")
        
        response = self.session.post(url, json={})
        if response.status_code in [201, 200]:
            result = response.json()
            job_id = result.get("id")
            print(f"✓ Job launched (ID: {job_id})")
            print(f"  URL: {AWX_HOST}/#/jobs/{job_id}")
            return result
        else:
            print(f"✗ Failed to launch job")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def create_inventory(self):
        """Create or get inventory"""
        print(f"\n📦 Setting up inventory: {INVENTORY_NAME}")
        url = self.get_url("inventories")
        
        # Check if exists
        response = self.session.get(url, params={"name": INVENTORY_NAME})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                inventory = results[0]
                print(f"✓ Inventory '{INVENTORY_NAME}' already exists (ID: {inventory['id']})")
                return inventory
        
        # Create new
        inventory_data = {
            "name": INVENTORY_NAME,
            "description": INVENTORY_DESCRIPTION,
            "organization": 1,
        }
        
        response = self.session.post(url, json=inventory_data)
        if response.status_code in [201, 200]:
            inventory = response.json()
            print(f"✓ Created inventory '{INVENTORY_NAME}' (ID: {inventory['id']})")
            return inventory
        else:
            print(f"✗ Failed to create inventory")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def add_host(self, inventory, host_data):
        """Add host to inventory"""
        host_name = host_data["name"]
        print(f"  🖥️  Adding host: {host_name}")
        
        url = self.get_url(f"inventories/{inventory['id']}/hosts")
        
        # Check if exists
        response = self.session.get(url, params={"name": host_name})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                host = results[0]
                print(f"    ✓ Host '{host_name}' already exists (ID: {host['id']})")
                # Update variables if needed
                return self.update_host(host, host_data)
        
        # Create new
        host_payload = {
            "name": host_data["name"],
            "description": host_data.get("description", ""),
            "variables": json.dumps(host_data.get("variables", {}))
        }
        
        response = self.session.post(url, json=host_payload)
        if response.status_code in [201, 200]:
            host = response.json()
            print(f"    ✓ Created host '{host_name}' (ID: {host['id']})")
            return host
        else:
            print(f"    ✗ Failed to create host '{host_name}'")
            print(f"      Status: {response.status_code}")
            print(f"      Response: {response.text}")
            return None

    def update_host(self, host, host_data):
        """Update host variables"""
        url = self.get_url(f"hosts/{host['id']}")
        
        payload = {
            "variables": json.dumps(host_data.get("variables", {}))
        }
        
        response = self.session.patch(url, json=payload)
        if response.status_code in [200]:
            print(f"    ✓ Updated host variables")
            return response.json()
        else:
            print(f"    ✗ Failed to update host")
            return host

    def setup(self, launch=False):
        """Setup project, job template, and inventory"""
        print("=" * 60)
        print("AWX Setup: Project, Job Template, and Inventory")
        print("=" * 60)
        
        try:
            # Create project
            project = self.create_project()
            if not project:
                return False
            
            # Create custom inventory
            inventory = self.create_inventory()
            if not inventory:
                # Fall back to default inventory
                inventory = self.get_inventory()
                if not inventory:
                    return False
            
            # Add hosts to inventory
            for host_data in HOSTS:
                self.add_host(inventory, host_data)
            
            # Create job template
            job_template = self.create_job_template(project, inventory)
            if not job_template:
                return False
            
            # Launch if requested
            if launch:
                self.launch_job_template(job_template)
            
            print("\n" + "=" * 60)
            print("✓ Setup completed successfully!")
            print("=" * 60)
            print(f"\nProject: {PROJECT_NAME}")
            print(f"  Git URL: {GIT_URL}")
            print(f"  Project ID: {project['id']}")
            print(f"\nInventory: {INVENTORY_NAME}")
            print(f"  Inventory ID: {inventory['id']}")
            print(f"  Hosts: {len(HOSTS)}")
            print(f"\nJob Template: {JOB_TEMPLATE_NAME}")
            print(f"  Playbook: {PLAYBOOK_NAME}")
            print(f"  Job Template ID: {job_template['id']}")
            print(f"\nAccess AWX at: {AWX_HOST}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during setup: {e}")
            return False


def main():
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description="Setup AWX Project and Job Template",
        epilog="""
        Setup Instructions:
        1. Get password: kubectl -n awx get secret awx-demo-admin-password -o jsonpath='{.data.password}' | base64 -d
        2. Port forward: kubectl -n awx port-forward svc/awx-demo-service 8080:80 &
        3. Run: python3 setup_awx.py --password YOUR_PASSWORD
        """
    )
    parser.add_argument("--host", default=AWX_HOST, help="AWX host URL (default: %(default)s)")
    parser.add_argument("--username", default=AWX_USERNAME, help="AWX username (default: %(default)s)")
    parser.add_argument("--password", required=True, help="AWX password (or set AWX_PASSWORD env var)")
    parser.add_argument("--launch", action="store_true", help="Launch job template after creation")
    
    args = parser.parse_args()
    
    print(f"Connecting to AWX at: {args.host}")
    
    client = AWXClient(args.host, args.username, args.password)
    success = client.setup(launch=args.launch)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
