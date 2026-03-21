# 🐳 Docker Deployment Guide

**AI-Adaptive Onboarding Engine**

---

## Prerequisites

- Docker installed ([Install](https://docs.docker.com/get-docker/))
- 3+ GB disk space
- Internet connection

---

## Quick Start

```bash
# Build image
cd "/AI-Adaptive Onboarding Engine"
docker build -t adaptive-onboarding:latest .

# Run container
docker run -d --name onboarding-app -p 3000:3000 adaptive-onboarding:latest

# Access at http://localhost:3000
```

---

## Essential Commands

```bash
docker build -t adaptive-onboarding:latest .         # Build image
docker run -d -p 3000:3000 adaptive-onboarding:latest  # Run container
docker ps                                            # List containers
docker logs -f onboarding-app                        # View logs
docker stop onboarding-app                           # Stop container
docker rm onboarding-app                             # Remove container
```

---

## Advanced Usage

### With Volume Mounting
```bash
docker run -d -p 3000:3000 -v $(pwd)/uploads:/app/uploads adaptive-onboarding:latest
```

### With Environment Variables
```bash
docker run -d -p 3000:3000 -e FLASK_ENV=production adaptive-onboarding:latest
```

### Multiple Instances
```bash
docker run -d --name app1 -p 3000:3000 adaptive-onboarding:latest
docker run -d --name app2 -p 3001:3000 adaptive-onboarding:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./results:/app/results
    environment:
      - FLASK_ENV=production
```

Run: `docker-compose up -d`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port in use** | Use different port: `-p 3001:3000` |
| **Check logs** | `docker logs <container>` |
| **Rebuild cache** | `docker build --no-cache ...` |
| **Memory issues** | `docker run -m 4g ...` |

---

**See README.md for additional deployment options**
