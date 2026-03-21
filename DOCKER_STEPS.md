# Docker Setup Guide - AI-Adaptive Onboarding Engine

This guide explains how to build and run the AI-Adaptive Onboarding Engine using Docker for easy deployment and consistent environment across machines.

---

## 📋 Prerequisites

Before using Docker, ensure you have:
- **Docker** installed ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Desktop** (optional, for GUI management)
- At least **3 GB of disk space** (for base image + dependencies)
- **Internet connection** (for initial build)

Verify Docker installation:
```bash
docker --version
```

---

## 🏗️ Step 1: Build the Docker Image

Navigate to the project directory and build the Docker image:

```bash
cd /path/to/AI-Adaptive\ Onboarding\ Engine

# Build the image with a tag
docker build -t adaptive-onboarding:latest .
```

**Alternative with custom tag:**
```bash
docker build -t adaptive-onboarding:v1.0 .
```

**What happens during build:**
- Downloads Python 3.10 slim base image
- Installs system dependencies (build-essential, curl)
- Installs Python requirements (Flask, torch, transformers, sentence-transformers, etc.)
- Copies application code into container
- Sets up environment variables
- Configures health checks

**Build output:**
```
Successfully built abc123xyz
Successfully tagged adaptive-onboarding:latest
```

> ⏱️ **First build takes 10-15 minutes** (subsequent builds are faster due to caching)

---

## 🚀 Step 2: Run the Docker Container

After building the image, run the container:

### **Option A: Basic Run (localhost only)**
```bash
docker run -p 5000:5000 adaptive-onboarding:latest
```

### **Option B: Run in Background (Recommended for production)**
```bash
docker run -d \
  --name onboarding-app \
  -p 5000:5000 \
  adaptive-onboarding:latest
```

### **Option C: Run with Volume Mounting (for local file access)**
```bash
docker run -d \
  --name onboarding-app \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  adaptive-onboarding:latest
```

### **Option D: Run with Network Accessibility**
```bash
docker run -d \
  --name onboarding-app \
  -p 0.0.0.0:5000:5000 \
  adaptive-onboarding:latest
```

**Parameter meanings:**
| Parameter | Meaning |
|-----------|---------|
| `-d` | Run in detached mode (background) |
| `--name` | Container name for easy reference |
| `-p 5000:5000` | Map port 5000 (host:container) |
| `-v` | Mount local directory inside container |
| `-e` | Pass environment variables |

---

## ✅ Step 3: Verify the Container is Running

Check if container is running:
```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                        PORTS                    STATUS
abc123xyz      adaptive-onboarding:latest   0.0.0.0:5000->5000/tcp   Up 2 minutes (healthy)
```

---

## 🌐 Step 4: Access the Application

Once container is running, access the web interface:

```bash
# Open in browser
http://localhost:5000
```

Or from another machine:
```bash
http://<your-machine-ip>:5000
```

Expected home page: AI-Adaptive Onboarding Engine interface with file upload

---

## 📊 Step 5: Monitor Container Health

Check container logs:
```bash
# View logs (last 50 lines)
docker logs onboarding-app

# Follow logs in real-time
docker logs -f onboarding-app

# View last 100 lines
docker logs --tail 100 onboarding-app
```

Check container stats:
```bash
docker stats onboarding-app
```

Health check status:
```bash
docker inspect --format='{{json .State.Health.Status}}' onboarding-app
```

---

## 🛑 Step 6: Stop the Container

Stop running container:
```bash
docker stop onboarding-app
```

Stop all containers:
```bash
docker stop $(docker ps -q)
```

Remove container:
```bash
docker rm onboarding-app
```

---

## 🔄 Step 7: Restart the Container

Restart container:
```bash
docker restart onboarding-app
```

---

## 🧹 Step 8: Cleanup

Remove stopped containers:
```bash
docker container prune
```

Remove unused images:
```bash
docker image prune
```

Remove specific image:
```bash
docker rmi adaptive-onboarding:latest
```

Remove everything (use with caution):
```bash
docker system prune -a
```

---

## 🔧 Advanced Usage

### **Push to Docker Hub**

1. Tag image with Docker Hub username:
```bash
docker tag adaptive-onboarding:latest <your-username>/adaptive-onboarding:latest
```

2. Login to Docker Hub:
```bash
docker login
```

3. Push image:
```bash
docker push <your-username>/adaptive-onboarding:latest
```

4. Others can pull it:
```bash
docker pull <your-username>/adaptive-onboarding:latest
```

---

### **Run Multiple Instances**

```bash
# Instance 1 (port 5000)
docker run -d --name app1 -p 5000:5000 adaptive-onboarding:latest

# Instance 2 (port 5001)
docker run -d --name app2 -p 5001:5000 adaptive-onboarding:latest

# Instance 3 (port 5002)
docker run -d --name app3 -p 5002:5000 adaptive-onboarding:latest
```

---

### **Build with Custom Parameters**

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t adaptive-onboarding:custom .
```

---

### **Run with Environment Variables**

```bash
docker run -d \
  --name onboarding-app \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  -e DEBUG=True \
  adaptive-onboarding:latest
```

---

## 📁 Dockerfile Breakdown

| Section | Purpose |
|---------|---------|
| `FROM python:3.10-slim` | Base image - minimal Python environment |
| `WORKDIR /app` | Sets working directory inside container |
| `ENV` | Environment variables for Flask configuration |
| `apt-get install` | System-level dependencies (build tools, curl) |
| `COPY requirements.txt .` | Copies Python dependencies file |
| `pip install` | Installs all Python packages from requirements |
| `COPY . .` | Copies entire application code |
| `EXPOSE 5000` | Declares port 5000 (documentation) |
| `HEALTHCHECK` | Automatic health monitoring |
| `CMD` | Default command to run (Flask app startup) |

---

## 🐛 Troubleshooting

### **Port Already in Use**
```bash
# Use different port
docker run -p 5001:5000 adaptive-onboarding:latest

# Or find and stop existing container
docker ps
docker stop <container-id>
```

### **Container Exits Immediately**
```bash
# Check logs
docker logs <container-id>

# Run with interactive terminal
docker run -it adaptive-onboarding:latest /bin/bash
```

### **File Upload Not Working**
```bash
# Mount upload directory with proper permissions
docker run -d \
  --name onboarding-app \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  adaptive-onboarding:latest
```

### **Memory Issues (torch/transformers)**
```bash
# Check available memory
free -h

# Run with memory limit (if needed)
docker run -d \
  -p 5000:5000 \
  -m 4g \
  adaptive-onboarding:latest
```

### **Rebuild Cache Issues**
```bash
# Force rebuild without cache
docker build --no-cache -t adaptive-onboarding:latest .
```

---

## 📊 Performance Optimization

### **Multi-stage Build** (future enhancement)
```dockerfile
# Can be added to Dockerfile for smaller final images
FROM python:3.10 AS builder
# Install dependencies...

FROM python:3.10-slim
COPY --from=builder /app .
```

### **Reduce Model Size**
Consider downloading and caching models:
```bash
docker run -v ~/.cache:/app/.cache adaptive-onboarding:latest
```

---

## 🚀 Deployment to Cloud Services

### **Docker Compose (Multiple Services)**
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  onboarding:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./results:/app/results
    environment:
      - FLASK_ENV=production
```

Run: `docker-compose up -d`

---

## ✨ Best Practices

✅ **Do:**
- Use `docker run -d` for production (background mode)
- Mount volumes for persistent data
- Use health checks for monitoring
- Tag images with version numbers
- Limit container resources with `-m` flag

❌ **Don't:**
- Run with `--privileged` flag unless necessary
- Store sensitive data in images
- Run as root (add user in Dockerfile)
- Use `latest` tag in production (use version tags)

---

## 📞 Support & Debugging

For issues with Docker, check:
1. Docker logs: `docker logs <container-name>`
2. Docker stats: `docker stats`
3. Flask documentation: https://flask.palletsprojects.com/
4. Docker documentation: https://docs.docker.com/

---

## 🎯 Quick Reference

```bash
# Build
docker build -t adaptive-onboarding:latest .

# Run (foreground)
docker run -p 5000:5000 adaptive-onboarding:latest

# Run (background)
docker run -d --name onboarding-app -p 5000:5000 adaptive-onboarding:latest

# Check status
docker ps

# View logs
docker logs -f onboarding-app

# Stop
docker stop onboarding-app

# Remove
docker rm onboarding-app
```

---

**Created**: March 2026  
**Project**: AI-Adaptive Onboarding Engine  
**Docker Version**: 20.10+  
**Python Version**: 3.10
