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
JOB_TEMPLATE_NAME = "simple-playbook"
PLAYBOOK_NAME = "ansible/simple-playbook.yaml"


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
        job_data = {
            "name": JOB_TEMPLATE_NAME,
            "description": f"Job template for {PLAYBOOK_NAME}",
            "project": project["id"],
            "playbook": PLAYBOOK_NAME,
            "inventory": inventory["id"],
            "ask_inventory": False,
            "ask_credential": False,
            "verbosity": 0,
            "extra_vars": "",
            "limit": "",
            "forks": 0,
            "use_fact_cache": False,
        }
        
        job_template = self.get_or_create("job_templates", JOB_TEMPLATE_NAME, job_data)
        return job_template

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

    def setup(self, launch=False):
        """Setup project and job template"""
        print("=" * 60)
        print("AWX Project and Job Template Setup")
        print("=" * 60)
        
        try:
            # Create project
            project = self.create_project()
            if not project:
                return False
            
            # Get inventory
            inventory = self.get_inventory()
            if not inventory:
                return False
            
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
            print(f"\nJob Template: {JOB_TEMPLATE_NAME}")
            print(f"  Playbook: {PLAYBOOK_NAME}")
            print(f"  Job Template ID: {job_template['id']}")
            print(f"  Inventory: {inventory['name']}")
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
