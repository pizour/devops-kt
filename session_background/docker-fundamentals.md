# Docker Fundamentals
## DevOps Knowledge Transfer – Session 6

**Author:** Zdenek Pyszko  
**Date:** February 2026  
**Audience:** Infrastructure Engineers  
**Duration:** ~90 minutes  
**Level:** Beginner to Intermediate  
**Pre-requisite for:** Kubernetes Sessions (7+)

---

## Agenda

| # | Topic | Time | Style |
|---|-------|------|-------|
| 1 | Recap & Context: Why Containers? | 10 min | Slides + Discussion |
| 2 | Docker Fundamentals – Concepts | 10 min | Slides |
| 3 | Docker Ecosystem: Docker Desktop, docker.io, Docker Engine | 5 min | Screen Share |
| 4 | Dockerfile – Building Images | 15 min | Live Demo |
| 5 | Docker Compose – Multi-Container Apps | 10 min | Live Demo |
| — | **Break** | **5 min** | |
| 6 | Docker CLI – Essential Commands | 10 min | Live Demo |
| 7 | Docker Registries & Push/Pull | 10 min | Live Demo |
| 8 | Azure Container Registry (ACR) | 10 min | Live Demo |
| 9 | Practice Test | 10 min | Interactive |
| 10 | Q&A + Next Session Preview | 5 min | Discussion |

---

## Recap: Previous Sessions

| Session | Topics Covered |
|---------|----------------|
| Session 1 | DevOps Theory, Culture, Principles |
| Session 2 | Azure Portal GUI, Resource Management |
| Session 3 | IaC – Terraform |
| Session 4 | Ansible – Configuration Management |
| Session 5 | Git & CI/CD Pipelines |
| **Session 6** | **Docker Fundamentals** ← _Today_ |
| Session 7+ | _Kubernetes (coming next)_ |

---

# PART 1: WHY CONTAINERS?

---

## The Problem: "It Works on My Machine"

```
Developer Laptop          Staging Server           Production Server
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ Python 3.11  │         │ Python 3.9   │         │ Python 3.8   │
│ Node 20      │         │ Node 18      │         │ Node 16      │
│ libssl 3.0   │         │ libssl 1.1   │         │ libssl 1.0   │
│ Ubuntu 24.04 │         │ RHEL 8       │         │ RHEL 7       │
└──────────────┘         └──────────────┘         └──────────────┘
      ✅ Works                ❌ Fails                ❌ Fails
```

**Root Cause:** Different environments have different OS versions, libraries, runtimes and configurations.

---

## The Solution: Containers

```
┌──────────────────────────────────────────────────────────────────┐
│                        Container Image                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  App Code + Python 3.11 + Node 20 + libssl 3.0 + configs  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

Same image runs EVERYWHERE:
  ✅ Developer Laptop    ✅ Staging Server    ✅ Production Server
```

> _"Ship the whole environment, not just the code."_

---

## VMs vs Containers

```
         Virtual Machines                         Containers
┌─────────────────────────────┐   ┌─────────────────────────────────┐
│  ┌─────┐ ┌─────┐ ┌─────┐   │   │  ┌─────┐ ┌─────┐ ┌─────┐      │
│  │App A│ │App B│ │App C│   │   │  │App A│ │App B│ │App C│      │
│  ├─────┤ ├─────┤ ├─────┤   │   │  ├─────┤ ├─────┤ ├─────┤      │
│  │Bins │ │Bins │ │Bins │   │   │  │Bins │ │Bins │ │Bins │      │
│  │Libs │ │Libs │ │Libs │   │   │  │Libs │ │Libs │ │Libs │      │
│  ├─────┤ ├─────┤ ├─────┤   │   │  └──┬──┘ └──┬──┘ └──┬──┘      │
│  │Guest│ │Guest│ │Guest│   │   │     └────────┼────────┘         │
│  │ OS  │ │ OS  │ │ OS  │   │   │        Docker Engine            │
│  └─────┘ └─────┘ └─────┘   │   │  ┌────────────────────────┐    │
│  ┌──────────────────────┐   │   │  │      Host OS            │    │
│  │     Hypervisor        │   │   │  └────────────────────────┘    │
│  ├──────────────────────┤   │   │  ┌────────────────────────┐    │
│  │      Host OS          │   │   │  │     Infrastructure      │    │
│  ├──────────────────────┤   │   │  └────────────────────────┘    │
│  │    Infrastructure     │   │   └─────────────────────────────────┘
│  └──────────────────────┘   │
└─────────────────────────────┘
     Heavy (GBs, minutes)              Light (MBs, seconds)
```

| Aspect | Virtual Machine | Container |
|--------|----------------|-----------|
| **Startup** | Minutes | Seconds |
| **Size** | GBs (full OS) | MBs (app + deps only) |
| **Isolation** | Full hardware-level | Process-level (shared kernel) |
| **Density** | ~10s per host | ~100s per host |
| **Use Case** | Different OS, strong isolation | Microservices, CI/CD, scaling |

> **Key Insight for Infra Engineers:** Containers don't replace VMs — they complement them. In Azure, containers run *on top of* VMs (AKS nodes, for example).

---

# PART 2: DOCKER FUNDAMENTALS

---

## What Is Docker?

- **Open platform** for building, shipping, and running containerised applications
- Created in **2013** by Solomon Hykes (dotCloud → Docker, Inc.)
- Uses **Linux kernel features** (namespaces, cgroups) for isolation
- De-facto standard for containers — though alternatives exist (Podman, containerd)

---

## Docker Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Docker Host                              │
│                                                                  │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │ Docker CLI   │────▶│         Docker Daemon (dockerd)       │  │
│  │ (docker ...)│     │                                        │  │
│  └──────────────┘     │  ┌────────┐ ┌────────┐ ┌────────┐   │  │
│                        │  │Container│ │Container│ │Container│   │  │
│                        │  │  nginx  │ │  app   │ │  db    │   │  │
│                        │  └────────┘ └────────┘ └────────┘   │  │
│                        │                                        │  │
│                        │  Images:    nginx:latest, python:3.11  │  │
│                        └──────────────────────────────────────┘  │
│                                      ▲                           │
└──────────────────────────────────────│───────────────────────────┘
                                       │ docker pull / push
                              ┌────────┴────────┐
                              │  Container       │
                              │  Registry         │
                              │  (Docker Hub,    │
                              │   ACR, GitHub)   │
                              └─────────────────┘
```

**Core concepts:**

| Term | What It Is |
|------|-----------|
| **Image** | Read-only template with app + dependencies (like a VM snapshot) |
| **Container** | Running instance of an image (like a VM running from a snapshot) |
| **Dockerfile** | Recipe/script to build an image |
| **Registry** | Storage for images (Docker Hub, ACR, etc.) |
| **Docker Daemon** | Background service that manages containers |
| **Docker CLI** | Command-line tool to interact with the daemon |

---

## Image Layers – How Images Work

```
┌─────────────────────────────────┐
│  Layer 5: COPY app.py /app/     │  ← Your application code
├─────────────────────────────────┤
│  Layer 4: RUN pip install flask │  ← Dependencies
├─────────────────────────────────┤
│  Layer 3: RUN apt-get update    │  ← OS packages
├─────────────────────────────────┤
│  Layer 2: ENV PYTHON=3.11       │  ← Environment config
├─────────────────────────────────┤
│  Layer 1: FROM python:3.11-slim │  ← Base image
└─────────────────────────────────┘
```

- Each instruction in a Dockerfile creates a **layer**
- Layers are **cached** — if a layer hasn't changed, Docker reuses it
- This is why **order matters** in a Dockerfile (put things that change least at the top)
- Images are **immutable** — you build a new image for every change

---

# PART 3: DOCKER ECOSYSTEM

---

## Docker Desktop vs docker.io vs Docker Engine

| Product | What It Is | Platform | Licensing |
|---------|-----------|----------|-----------|
| **Docker Engine** | Core daemon + CLI (open source) | Linux | Free (Apache 2.0) |
| **docker.io** | Docker Engine packaged by Debian/Ubuntu | Linux (apt) | Free |
| **Docker Desktop** | GUI + Engine + Compose + Kubernetes | Windows, macOS, Linux | Free for small business (<250 employees / <$10M revenue); **paid** otherwise |
| **Docker CE** | Community Edition (= Docker Engine) | Linux | Free |

### Installation on Ubuntu (what you'd do on a server)

```bash
# Option A: Quick install from Ubuntu repos (docker.io)
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable --now docker

# Option B: Official Docker Engine (recommended for production)
# Add Docker's official GPG key and repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Allow your user to run docker without sudo
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
```

### Docker Desktop (for local development on laptops)

- GUI application with tray icon
- Includes: Docker Engine, Docker Compose, Docker Scout, Kubernetes (optional)
- Manages Linux VM transparently on Windows/macOS (uses WSL2 on Windows, HyperKit/Virtualization.framework on macOS)
- **Demo:** Brief walkthrough of Docker Desktop UI

> **For Infrastructure Engineers:** On Azure VMs and servers, you install Docker Engine directly. Docker Desktop is for developer laptops.

---

# PART 4: DOCKERFILE – BUILDING IMAGES

---

## Dockerfile Basics

A Dockerfile is a text file with instructions for building an image. Think of it as an **automated install script**.

### Anatomy of a Dockerfile

```dockerfile
# 1. Base image – every Dockerfile starts with FROM
FROM python:3.11-slim

# 2. Metadata
LABEL maintainer="zdenek@example.com"
LABEL description="Simple Flask web application"

# 3. Set working directory inside the container
WORKDIR /app

# 4. Copy dependency file first (for better caching)
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY . .

# 7. Expose port (documentation, not enforcement)
EXPOSE 5000

# 8. Define the command to run
CMD ["python", "app.py"]
```

---

## Key Dockerfile Instructions

| Instruction | Purpose | Example |
|-------------|---------|---------|
| `FROM` | Base image (REQUIRED, must be first) | `FROM ubuntu:22.04` |
| `RUN` | Execute command during build | `RUN apt-get update && apt-get install -y curl` |
| `COPY` | Copy files from host to image | `COPY ./src /app/src` |
| `ADD` | Like COPY, but also handles URLs and tar extraction | `ADD archive.tar.gz /app/` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `ENV` | Set environment variable | `ENV NODE_ENV=production` |
| `EXPOSE` | Document which port the app uses | `EXPOSE 8080` |
| `CMD` | Default command when container starts | `CMD ["nginx", "-g", "daemon off;"]` |
| `ENTRYPOINT` | Fixed command (CMD becomes arguments) | `ENTRYPOINT ["python"]` |
| `ARG` | Build-time variable | `ARG VERSION=1.0` |
| `VOLUME` | Declare mount point | `VOLUME /data` |
| `USER` | Set the user to run as | `USER appuser` |

---

## Demo: Build a Simple Image

### Project structure

```
demo-app/
├── app.py
├── requirements.txt
└── Dockerfile
```

### app.py

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Docker! 🐳"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### requirements.txt

```
flask==3.0.0
```

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Build & Run

```bash
# Build the image (don't forget the dot!)
docker build -t demo-app:1.0 .

# Run the container
docker run -d -p 8080:5000 --name my-app demo-app:1.0

# Test it
curl http://localhost:8080

# View logs
docker logs my-app

# Stop and remove
docker stop my-app && docker rm my-app
```

---

## Dockerfile Best Practices

```dockerfile
# ❌ BAD – large image, runs as root, no caching benefit
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

# ✅ GOOD – slim base, layer caching, non-root user
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN adduser --disabled-password --gecos '' appuser
COPY . .
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
```

| Practice | Why |
|----------|-----|
| Use **slim/alpine** base images | Smaller images = faster pulls, smaller attack surface |
| **COPY dependencies first**, then code | Leverage Docker layer caching |
| Use **`.dockerignore`** file | Exclude unnecessary files (`.git/`, `node_modules/`, `*.md`) |
| **Don't run as root** | Security — use `USER` instruction |
| **Combine RUN commands** | Fewer layers, smaller image: `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*` |
| Use **multi-stage builds** for compiled apps | Build in one stage, copy only the binary to a minimal final image |

---

## Multi-Stage Build Example

```dockerfile
# Stage 1: Build
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o myapp .

# Stage 2: Runtime (minimal image)
FROM alpine:3.18
COPY --from=builder /app/myapp /usr/local/bin/myapp
EXPOSE 8080
CMD ["myapp"]
```

```
Build stage image:  ~800 MB (Go toolchain + source)
Final image:        ~15 MB  (alpine + single binary)
```

> **Analogy for Infra Engineers:** It's like building a VM from a template, installing everything, exporting just the application, then deploying it on a minimal OS image.

---

# PART 5: DOCKER COMPOSE

---

## What Is Docker Compose?

- Tool for defining and running **multi-container** applications
- Uses a **YAML file** (`docker-compose.yml` or `compose.yaml`) to configure services
- Single command to start/stop everything: `docker compose up / down`

### When to use it?

```
Without Compose:
  docker run -d --name db -e POSTGRES_PASSWORD=secret postgres:16
  docker run -d --name app --link db -p 8080:5000 my-app:1.0
  docker run -d --name redis redis:7
  # ... manually manage networking, volumes, dependencies

With Compose:
  docker compose up -d      ← one command, all services
```

---

## Docker Compose – Example

```yaml
# compose.yaml
services:
  # Web application
  app:
    build: .
    ports:
      - "8080:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    restart: unless-stopped

  # PostgreSQL database
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis cache
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  db-data:       # Named volume for persistent data
```

---

## Docker Compose Commands

```bash
# Start all services (detached)
docker compose up -d

# View running services
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f app

# Stop all services
docker compose down

# Stop and remove volumes (careful – deletes data!)
docker compose down -v

# Rebuild images and restart
docker compose up -d --build

# Scale a service (run 3 instances of app)
docker compose up -d --scale app=3

# Execute command in running service
docker compose exec app bash
```

---

## Docker Compose – Networking

```
┌────────────────────────────────────────────┐
│          Docker Compose Network             │
│          (auto-created: myapp_default)      │
│                                             │
│  ┌──────┐    ┌──────┐    ┌──────┐         │
│  │ app  │───▶│  db  │    │cache │         │
│  │:5000 │    │:5432 │    │:6379 │         │
│  └──┬───┘    └──────┘    └──────┘         │
│     │                                       │
└─────│───────────────────────────────────────┘
      │ port mapping
      ▼
   Host:8080
```

- Compose creates a **dedicated network** for each project automatically
- Services can reach each other by **service name** (DNS): `app` connects to `db:5432`
- Only explicitly mapped ports are accessible from the host

---

# ☕ BREAK (5 min)

---

# PART 6: DOCKER CLI – ESSENTIAL COMMANDS

---

## Container Lifecycle

```
        docker create            docker start
Image ──────────────▶ Created ──────────────▶ Running
                                    ▲              │
                                    │    docker     │
                                    │    restart    │
                                    │              ▼
                               docker start    Stopped
                                    ▲              │
                                    │   docker     │
                                    │   stop       │
                                    │              │
                                    └──────────────┘

                       docker rm
               Created/Stopped ──────────▶ Deleted
```

---

## Essential Docker Commands

### Images

```bash
# List local images
docker images
docker image ls

# Pull image from registry
docker pull nginx:latest
docker pull python:3.11-slim

# Build image from Dockerfile
docker build -t myapp:1.0 .
docker build -t myapp:latest -f Dockerfile.prod .

# Remove image
docker rmi nginx:latest
docker image rm myapp:1.0

# Inspect image details
docker image inspect nginx:latest

# Show image history (layers)
docker image history nginx:latest

# Prune unused images
docker image prune -a
```

### Containers

```bash
# Run a container (pull + create + start)
docker run -d --name web -p 80:80 nginx:latest

# Common run flags
docker run -d \                  # Detached (background)
  --name my-container \          # Custom name
  -p 8080:80 \                   # Port mapping host:container
  -v /host/path:/container/path \ # Volume mount
  -e MY_VAR=value \              # Environment variable
  --restart unless-stopped \     # Restart policy
  nginx:latest

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop / Start / Restart
docker stop my-container
docker start my-container
docker restart my-container

# Remove container
docker rm my-container
docker rm -f my-container        # Force remove (even if running)

# View logs
docker logs my-container
docker logs -f my-container      # Follow (tail -f)
docker logs --tail 50 my-container

# Execute command inside running container
docker exec -it my-container bash
docker exec my-container cat /etc/os-release

# Copy files between host and container
docker cp my-container:/app/log.txt ./log.txt
docker cp ./config.yml my-container:/app/config.yml

# Resource usage
docker stats
```

### System

```bash
# System-wide information
docker info

# Disk usage
docker system df

# Clean up everything unused
docker system prune -a --volumes
```

---

## Port Mapping Explained

```
        Host Machine                    Container
  ┌─────────────────────┐      ┌─────────────────────┐
  │                     │      │                     │
  │    localhost:8080 ──────────────▶ :80 (nginx)    │
  │    localhost:3000 ──────────────▶ :5000 (flask)  │
  │    localhost:5432 ──────────────▶ :5432 (postgres)│
  │                     │      │                     │
  └─────────────────────┘      └─────────────────────┘

  docker run -p 8080:80 nginx          # host:container
  docker run -p 3000:5000 flask-app    # host:container
  docker run -p 5432:5432 postgres     # same port
```

`-p HOST_PORT:CONTAINER_PORT`

---

# PART 7: DOCKER REGISTRIES & PUSH/PULL

---

## What Is a Container Registry?

A container registry is a **repository for storing and distributing container images** — similar to how GitHub stores code, registries store images.

```
Developer                   Registry                    Server
┌─────────┐  docker push   ┌─────────┐   docker pull  ┌─────────┐
│ Build    │ ─────────────▶ │  Store   │ ◀──────────── │ Deploy   │
│ Image    │                │  Image   │               │ Image    │
└─────────┘                └─────────┘                └─────────┘
```

### Popular Registries

| Registry | URL | Type |
|---------|-----|------|
| **Docker Hub** | hub.docker.com | Public + Private |
| **Azure Container Registry (ACR)** | *.azurecr.io | Private (Azure) |
| **GitHub Container Registry** | ghcr.io | Public + Private |
| **AWS ECR** | *.ecr.amazonaws.com | Private (AWS) |
| **Google Artifact Registry** | *.pkg.dev | Private (GCP) |
| **Harbor** | Self-hosted | Private (on-prem) |

---

## Image Naming Convention

```
registry/repository:tag

Examples:
  docker.io/library/nginx:latest        # Docker Hub official
  docker.io/myuser/myapp:1.0            # Docker Hub user
  myregistry.azurecr.io/myapp:v2.1      # Azure Container Registry
  ghcr.io/myorg/myapp:sha-abc123        # GitHub Container Registry
```

| Component | Description | Example |
|-----------|-------------|---------|
| **Registry** | Where the image is stored | `myregistry.azurecr.io` |
| **Repository** | Image name (can include namespace) | `myapp`, `team/myapp` |
| **Tag** | Version identifier | `latest`, `1.0`, `v2.1-rc1` |

> **Warning:** `latest` is NOT necessarily the newest — it's just the default tag. Always use explicit version tags in production.

---

## Push & Pull Workflow

```bash
# 1. Build your image
docker build -t myapp:1.0 .

# 2. Tag it for your target registry
docker tag myapp:1.0 myregistry.azurecr.io/myapp:1.0

# 3. Log in to the registry
docker login myregistry.azurecr.io

# 4. Push the image
docker push myregistry.azurecr.io/myapp:1.0

# 5. On another machine — pull and run
docker pull myregistry.azurecr.io/myapp:1.0
docker run -d -p 8080:5000 myregistry.azurecr.io/myapp:1.0
```

---

# PART 8: AZURE CONTAINER REGISTRY (ACR)

---

## What Is ACR?

- **Managed** Docker registry service in Azure (no infrastructure to manage)
- Integrated with Azure AD, AKS, App Service, Azure DevOps
- Supports Docker images, Helm charts, OCI artifacts
- Geo-replication for global deployments
- Built-in vulnerability scanning (Microsoft Defender for Cloud)

---

## ACR Tiers

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Storage | 10 GB | 100 GB | 500 GB |
| Webhooks | 2 | 10 | 500 |
| Geo-replication | ❌ | ❌ | ✅ |
| Private Link | ❌ | ❌ | ✅ |
| Content Trust | ❌ | ❌ | ✅ |
| ~Cost/month | ~$5 | ~$20 | ~$50+ |

> **For our hub-spoke architecture:** Premium tier with Private Link — ACR is accessed via private endpoint in the hub VNet (no public exposure).

---

## ACR – Create & Use

### Create ACR (Terraform – from our Session 3!)

```hcl
resource "azurerm_container_registry" "acr" {
  name                = "myprojectacr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Premium"
  admin_enabled       = false    # Use managed identity / Azure AD instead

  # Optional: Private endpoint (hub-spoke pattern)
  public_network_access_enabled = false
}
```

### Create ACR (Azure CLI)

```bash
# Create resource group
az group create --name rg-acr-demo --location westeurope

# Create ACR
az acr create \
  --resource-group rg-acr-demo \
  --name myprojectacr \
  --sku Standard

# Log in to ACR
az acr login --name myprojectacr

# Build and push (ACR Tasks – build in cloud, no local Docker needed!)
az acr build --registry myprojectacr --image myapp:1.0 .
```

---

## ACR Authentication Methods

| Method | Use Case | Command |
|--------|----------|---------|
| **Azure AD (az acr login)** | Developer / CI local | `az acr login --name myacr` |
| **Service Principal** | CI/CD pipelines | `docker login myacr.azurecr.io -u <sp-id> -p <sp-secret>` |
| **Managed Identity** | AKS / Azure services | Attach ACR to AKS (no credentials needed) |
| **Admin Account** | Quick testing only (NOT recommended) | Enable in portal, use username/password |
| **Token / Scope Map** | Fine-grained repo access | Repository-level pull/push tokens |

### AKS + ACR Integration (most common in our environment)

```bash
# Attach ACR to AKS cluster (managed identity – no secrets!)
az aks update \
  --resource-group rg-aks \
  --name my-aks-cluster \
  --attach-acr myprojectacr

# AKS nodes can now pull images from ACR without docker login
# In Kubernetes manifests, just reference:
#   image: myprojectacr.azurecr.io/myapp:1.0
```

---

## ACR – Useful Commands

```bash
# List repositories in ACR
az acr repository list --name myprojectacr -o table

# List tags for a repository
az acr repository show-tags --name myprojectacr --repository myapp -o table

# Show image details
az acr repository show --name myprojectacr --image myapp:1.0

# Delete an image
az acr repository delete --name myprojectacr --image myapp:1.0

# Import image from Docker Hub to ACR (no local Docker needed)
az acr import \
  --name myprojectacr \
  --source docker.io/library/nginx:latest \
  --image nginx:latest

# Run a quick test container from ACR (ACR Tasks)
az acr run --registry myprojectacr --cmd 'myprojectacr.azurecr.io/myapp:1.0' /dev/null
```

---

## How ACR Fits in Our Architecture

```
┌───────────────────────────────────────────────────────┐
│                    Hub VNet                            │
│                                                       │
│  ┌───────────────┐    Private     ┌───────────────┐  │
│  │  ACR           │◄──Endpoint───▶│ Private DNS    │  │
│  │  (Premium)     │               │ Zone           │  │
│  │                │               │ azurecr.io     │  │
│  └───────────────┘               └───────────────┘  │
│         ▲                                             │
│         │  Pull images (private network)              │
│         │                                             │
├─────────│─────────────────────────────────────────────┤
│         │           Spoke VNet                        │
│         │                                             │
│  ┌──────┴────────┐                                   │
│  │  AKS Cluster   │                                   │
│  │  (nodes pull    │                                   │
│  │   from ACR)     │                                   │
│  └────────────────┘                                   │
└───────────────────────────────────────────────────────┘
```

> **Connection to Next Session:** In Kubernetes sessions (7+), we'll deploy apps to AKS that pull images from this ACR.

---

# PART 9: PRACTICE TEST

---

## Practice Test (10 minutes)

Answer the following questions. Discuss answers together after.

### Questions

**Q1.** What is the difference between a Docker **image** and a **container**?

<details>
<summary>Answer</summary>
An image is a read-only template (like a VM snapshot/template). A container is a running instance of an image (like a VM created from that template). You can run multiple containers from the same image.
</details>

---

**Q2.** What does this command do?  
```bash
docker run -d -p 3000:80 --name web nginx:latest
```

<details>
<summary>Answer</summary>
Runs an nginx container in detached mode (background), maps host port 3000 to container port 80, and names the container "web". You'd access it at http://localhost:3000.
</details>

---

**Q3.** Why do we `COPY requirements.txt` before `COPY . .` in a Dockerfile?

<details>
<summary>Answer</summary>
For Docker layer caching. If the requirements haven't changed, Docker reuses the cached layer from the pip install step and doesn't reinstall dependencies — making builds much faster.
</details>

---

**Q4.** What is the difference between `docker.io` (apt package) and **Docker Desktop**?

<details>
<summary>Answer</summary>
docker.io is the Docker Engine packaged by Ubuntu/Debian for Linux servers (CLI only, free). Docker Desktop is a GUI application for developer laptops (Windows/macOS/Linux) that includes Docker Engine, Compose, and optional Kubernetes. Docker Desktop requires a paid license for larger organisations.
</details>

---

**Q5.** How does AKS authenticate to ACR to pull images? What's the recommended method?

<details>
<summary>Answer</summary>
The recommended method is Managed Identity. You attach ACR to AKS using `az aks update --attach-acr`. AKS nodes are granted the AcrPull role automatically — no credentials to manage or rotate.
</details>

---

**Q6.** You have a `compose.yaml` with services `app` and `db`. How does the `app` service connect to the database?

<details>
<summary>Answer</summary>
By using the service name as the hostname: `db:5432` (for PostgreSQL). Docker Compose creates a shared network and provides DNS resolution between services using their names.
</details>

---

**Q7.** What's wrong with this Dockerfile?

```dockerfile
FROM ubuntu:latest
COPY . .
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip install -r requirements.txt
CMD python3 app.py
```

<details>
<summary>Answer</summary>
Multiple issues: (1) Using full ubuntu instead of python:slim — unnecessarily large. (2) Not combining RUN commands — creates extra layers. (3) Copying all files before installing deps — breaks layer caching. (4) Running as root — security risk. (5) Using `latest` tag — not reproducible. (6) No WORKDIR set. (7) Not cleaning up apt cache.
</details>

---

**Q8.** What does `docker system prune -a --volumes` do? When would you use it?

<details>
<summary>Answer</summary>
Removes ALL unused containers, networks, images (not just dangling), and volumes. Use it to free disk space on a development machine. Never run this on a production host without understanding what will be removed.
</details>

---

# PART 10: WRAP UP

---

## Key Takeaways

| Concept | One-Liner |
|---------|-----------|
| **Container** | Lightweight, portable package: app + dependencies + runtime |
| **Docker Image** | Immutable, layered template built from a Dockerfile |
| **Dockerfile** | Recipe to build an image — order matters for caching |
| **Docker Compose** | Define multi-container apps in YAML, manage with one command |
| **Registry** | Image storage & distribution (Docker Hub, ACR, GHCR) |
| **ACR** | Azure's managed registry — integrates with AKS via managed identity |

---

## What's Coming Next

| Session | Topic | Build On |
|---------|-------|----------|
| **Session 7** | Kubernetes Fundamentals – Architecture, Pods, Deployments | Docker images → K8s pods |
| **Session 8** | Kubernetes in Azure (AKS) – Deployment, Services, Ingress | ACR → AKS image pulls |
| **Session 9** | Kubernetes Operations – Helm, Monitoring, GitOps | Compose → Helm charts |

> _Today we learned to build and ship containers. Next time, we'll learn to **orchestrate** them at scale with Kubernetes._

---

## Resources

| Resource | Link |
|----------|------|
| Docker Official Docs | https://docs.docker.com/ |
| Dockerfile Reference | https://docs.docker.com/reference/dockerfile/ |
| Docker Compose Reference | https://docs.docker.com/compose/compose-file/ |
| Azure Container Registry Docs | https://learn.microsoft.com/en-us/azure/container-registry/ |
| Docker Hub | https://hub.docker.com/ |
| Play with Docker (free lab) | https://labs.play-with-docker.com/ |
| Our Terraform ACR Module | `terraform/examples/modules/acr/` |

---

_End of Session 6 – Docker Fundamentals_
