# Docker Deployment

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom is designed to run in Docker containers for easy deployment and scaling. This guide covers:
- Single-node deployment (development & small teams)
- Multi-container setup with Docker Compose
- Production deployment patterns
- Kubernetes deployment (future)

---

## Quick Start

### Prerequisites

- Docker 24.0+ 
- Docker Compose 2.20+
- 2GB RAM minimum
- 10GB disk space

### One-Command Deploy

```bash
docker-compose up -d
```

Access Loom at `http://localhost:8000`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │    Celery    │  │  PostgreSQL  │      │
│  │   (API +     │  │   Workers    │  │  (Database)  │      │
│  │  Webhooks)   │  │              │  │              │      │
│  │              │  │              │  │              │      │
│  │  Port: 8000  │  │  x3 workers  │  │  Port: 5432  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                 │                                 │
│         └────────┬────────┘                                 │
│                  │                                          │
│         ┌────────▼────────┐                                 │
│         │     Redis       │                                 │
│         │   (Queue +      │                                 │
│         │    Cache)       │                                 │
│         │                 │                                 │
│         │  Port: 6379     │                                 │
│         └─────────────────┘                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Dockerfile

### API & Worker Container

**File:** `Dockerfile`

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 loom && \
    chown -R loom:loom /app

USER loom

# Default command (overridden by docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage Build (Production)

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 loom && \
    chown -R loom:loom /app

USER loom

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Docker Compose

### Development Setup

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: loom-postgres
    environment:
      POSTGRES_USER: loom
      POSTGRES_PASSWORD: loom
      POSTGRES_DB: loom
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U loom"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - loom

  # Redis (Queue & Cache)
  redis:
    image: redis:7-alpine
    container_name: loom-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - loom

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: loom-api
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      # Database
      DATABASE_URL: postgresql://loom:loom@postgres:5432/loom
      
      # Redis
      REDIS_URL: redis://redis:6379/0
      
      # GitHub
      GITHUB_API_TOKEN: ${GITHUB_API_TOKEN}
      GITHUB_WEBHOOK_SECRET: ${GITHUB_WEBHOOK_SECRET}
      
      # GitLab
      GITLAB_API_TOKEN: ${GITLAB_API_TOKEN}
      GITLAB_WEBHOOK_SECRET: ${GITLAB_WEBHOOK_SECRET}
      
      # Other platforms
      BITBUCKET_USERNAME: ${BITBUCKET_USERNAME}
      BITBUCKET_APP_PASSWORD: ${BITBUCKET_APP_PASSWORD}
      GITEA_API_TOKEN: ${GITEA_API_TOKEN}
      GITEA_WEBHOOK_SECRET: ${GITEA_WEBHOOK_SECRET}
      
      # LLM APIs
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      
      # App Config
      LOG_LEVEL: INFO
      WORKERS: 1
    volumes:
      - ./src:/app/src
      - ./alembic:/app/alembic
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loom
    restart: unless-stopped

  # Celery Workers
  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A src.worker worker --loglevel=info --concurrency=3
    environment:
      DATABASE_URL: postgresql://loom:loom@postgres:5432/loom
      REDIS_URL: redis://redis:6379/0
      GITHUB_API_TOKEN: ${GITHUB_API_TOKEN}
      GITLAB_API_TOKEN: ${GITLAB_API_TOKEN}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      LOG_LEVEL: INFO
    volumes:
      - ./src:/app/src
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loom
    restart: unless-stopped
    deploy:
      replicas: 3

networks:
  loom:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Production Setup

**File:** `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: loom-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - loom
    restart: always

  redis:
    image: redis:7-alpine
    container_name: loom-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - loom
    restart: always

  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime  # Multi-stage build
    container_name: loom-api
    command: gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      
      # Platform tokens (from secrets)
      GITHUB_API_TOKEN: ${GITHUB_API_TOKEN}
      GITLAB_API_TOKEN: ${GITLAB_API_TOKEN}
      
      # LLM APIs
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      
      # Production settings
      LOG_LEVEL: WARNING
      SENTRY_DSN: ${SENTRY_DSN}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.loom.rule=Host(`loom.company.com`)"
      - "traefik.http.routers.loom.tls=true"
      - "traefik.http.routers.loom.tls.certresolver=letsencrypt"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loom
      - traefik
    restart: always

  worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    command: celery -A src.worker worker --loglevel=warning --concurrency=5
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      GITHUB_API_TOKEN: ${GITHUB_API_TOKEN}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      LOG_LEVEL: WARNING
      SENTRY_DSN: ${SENTRY_DSN}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - loom
    restart: always
    deploy:
      replicas: 5

networks:
  loom:
    driver: bridge
  traefik:
    external: true

volumes:
  postgres_data:
  redis_data:
```

---

## Environment Variables

**File:** `.env`

```bash
# Database
POSTGRES_USER=loom
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=loom

# Redis
REDIS_PASSWORD=your-redis-password

# GitHub
GITHUB_API_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-github-webhook-secret

# GitLab
GITLAB_API_TOKEN=glpat-...
GITLAB_WEBHOOK_SECRET=your-gitlab-webhook-secret

# Bitbucket
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password
BITBUCKET_WEBHOOK_UUIDS=uuid1,uuid2

# Gitea
GITEA_API_TOKEN=your-gitea-token
GITEA_WEBHOOK_SECRET=your-gitea-webhook-secret
GITEA_BASE_URL=https://gitea.company.com/api/v1

# Azure DevOps
AZURE_DEVOPS_PAT=your-pat
AZURE_DEVOPS_WEBHOOK_SECRET=your-secret
AZURE_DEVOPS_ORGANIZATION=your-org

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk-...

# Monitoring (Optional)
SENTRY_DSN=https://...@sentry.io/...

# App Settings
LOG_LEVEL=INFO
```

**Security:** Never commit `.env` to git! Add to `.gitignore`.

---

## Deployment Steps

### Development

```bash
# 1. Clone repository
git clone https://github.com/your-org/loom.git
cd loom

# 2. Create .env file
cp .env.example .env
# Edit .env with your tokens

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Check logs
docker-compose logs -f

# 6. Access API
curl http://localhost:8000/health
```

### Production

```bash
# 1. Set environment variables (secrets management)
export GITHUB_API_TOKEN=ghp_...
export OPENAI_API_KEY=sk-...
# ... etc

# 2. Build production images
docker-compose -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 5. Verify
curl https://loom.company.com/health
```

---

## Scaling

### Horizontal Scaling (Multiple Nodes)

```yaml
# docker-compose.scale.yml
services:
  api:
    deploy:
      replicas: 3  # 3 API instances
  
  worker:
    deploy:
      replicas: 10  # 10 worker instances
```

**Deploy:**
```bash
docker-compose -f docker-compose.prod.yml -f docker-compose.scale.yml up -d
```

### Load Balancer (Traefik)

```yaml
# docker-compose.lb.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@company.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks:
      - traefik
```

---

## Database Backups

### Automated Backups

**File:** `scripts/backup.sh`

```bash
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/loom_backup_$TIMESTAMP.sql"

# Backup database
docker-compose exec -T postgres pg_dump -U loom loom > "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Keep only last 30 days
find "$BACKUP_DIR" -name "loom_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**Cron Job:**
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/loom/scripts/backup.sh
```

### Restore from Backup

```bash
# Restore database
gunzip -c /backups/loom_backup_20260118_020000.sql.gz | \
  docker-compose exec -T postgres psql -U loom loom
```

---

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Postgres health
docker-compose exec postgres pg_isready -U loom

# Redis health
docker-compose exec redis redis-cli ping

# Worker status
docker-compose exec worker celery -A src.worker inspect active
```

### Prometheus Metrics

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - loom

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    networks:
      - loom

volumes:
  prometheus_data:
  grafana_data:
```

**prometheus.yml:**
```yaml
scrape_configs:
  - job_name: 'loom-api'
    static_configs:
      - targets: ['api:8000']
```

---

## Logging

### Centralized Logging (ELK Stack)

```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elastic_data:/usr/share/elasticsearch/data
    networks:
      - loom

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    networks:
      - loom

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    networks:
      - loom
```

### Log to Stdout (Docker Logs)

```python
# src/logging.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}',
    stream=sys.stdout
)
```

**View logs:**
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs api

# Check health
docker-compose ps

# Rebuild container
docker-compose build --no-cache api
docker-compose up -d api
```

### Database Connection Issues

```bash
# Test connection
docker-compose exec api python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://loom:loom@postgres:5432/loom'); engine.connect()"

# Check postgres logs
docker-compose logs postgres
```

### Worker Not Processing Jobs

```bash
# Check worker status
docker-compose exec worker celery -A src.worker inspect active

# Check redis connection
docker-compose exec worker python -c "import redis; r = redis.Redis(host='redis'); r.ping()"

# Restart workers
docker-compose restart worker
```

### Out of Memory

```bash
# Check container memory
docker stats

# Increase memory limit
docker-compose.yml:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## Security Best Practices

### 1. Use Secrets Management

**Docker Secrets (Swarm):**
```yaml
services:
  api:
    secrets:
      - github_token
      - openai_key

secrets:
  github_token:
    external: true
  openai_key:
    external: true
```

**External Secrets (Kubernetes):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: loom-secrets
type: Opaque
data:
  github-token: <base64>
  openai-key: <base64>
```

### 2. Run as Non-Root

Already configured in Dockerfile:
```dockerfile
USER loom
```

### 3. Network Isolation

```yaml
networks:
  frontend:  # Public-facing (API)
  backend:   # Internal (DB, Redis)
```

### 4. Regular Updates

```bash
# Update base images
docker-compose pull
docker-compose up -d --build
```

---

## Next Steps

- **Kubernetes Deployment:** See [kubernetes.md](kubernetes.md) (future)
- **Environment Variables:** See [environment.md](environment.md)
- **Development Setup:** See [development.md](development.md)

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)
