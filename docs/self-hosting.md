# Self-Hosting Guide

This guide covers all deployment options for running Loom Code Reviews on your own infrastructure.

## Table of Contents

- [Requirements](#requirements)
- [Quick Start (Docker)](#quick-start-docker)
- [Docker Compose](#docker-compose)
- [Kubernetes](#kubernetes)
- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [Reverse Proxy Setup](#reverse-proxy-setup)
- [Upgrading](#upgrading)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)

## Requirements

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 512 MB | 1 GB+ |
| Disk | 1 GB | 10 GB+ |
| Network | Outbound HTTPS | Outbound HTTPS |

### Software Requirements

- Docker 20.10+ (or Podman 4.0+)
- Docker Compose 2.0+ (for compose deployments)
- Kubernetes 1.24+ (for k8s deployments)

### Network Requirements

Loom needs to:
- Receive webhooks from your git platform (inbound HTTPS)
- Call your LLM provider API (outbound HTTPS)
- Access your git platform API (outbound HTTPS)

## Quick Start (Docker)

The simplest way to run Loom - a single container with SQLite:

```bash
docker run -d \
  --name loom \
  -p 3000:3000 \
  -v loom-data:/data \
  -e BETTER_AUTH_SECRET=your-secret-min-32-chars \
  -e OPENAI_API_KEY=sk-... \
  ghcr.io/loom-reviews/loom:latest
```

That's it! Open `http://localhost:3000` to access Loom.

### With All Options

```bash
docker run -d \
  --name loom \
  -p 3000:3000 \
  -v loom-data:/data \
  -e BETTER_AUTH_SECRET=your-secret-min-32-chars \
  -e BETTER_AUTH_URL=https://loom.example.com \
  -e DATABASE_URL=file:/data/loom.db \
  -e OPENAI_API_KEY=sk-... \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e GITHUB_CLIENT_ID=... \
  -e GITHUB_CLIENT_SECRET=... \
  -e GOOGLE_CLIENT_ID=... \
  -e GOOGLE_CLIENT_SECRET=... \
  --restart unless-stopped \
  ghcr.io/loom-reviews/loom:latest
```

## Docker Compose

Recommended for production deployments with PostgreSQL:

### 1. Create Project Directory

```bash
mkdir loom && cd loom
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    image: ghcr.io/loom-reviews/loom:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://loom:loom@db:5432/loom
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - BETTER_AUTH_URL=${BETTER_AUTH_URL:-http://localhost:3000}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}
      - EMAIL_PROVIDER=${EMAIL_PROVIDER:-smtp}
      - SMTP_HOST=${SMTP_HOST:-}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SMTP_USER=${SMTP_USER:-}
      - SMTP_PASS=${SMTP_PASS:-}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    image: ghcr.io/loom-reviews/loom-worker:latest
    environment:
      - DATABASE_URL=postgres://loom:loom@db:5432/loom
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=loom
      - POSTGRES_PASSWORD=loom
      - POSTGRES_DB=loom
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U loom"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres-data:
```

### 3. Create .env File

```bash
# Required
BETTER_AUTH_SECRET=generate-a-random-32-char-string-here
BETTER_AUTH_URL=https://loom.yourdomain.com

# LLM Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# OAuth (at least one recommended)
GITHUB_CLIENT_ID=your-github-oauth-app-id
GITHUB_CLIENT_SECRET=your-github-oauth-app-secret
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# Email (optional, for magic links)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASS=password
```

### 4. Start Services

```bash
docker compose up -d
```

### 5. View Logs

```bash
docker compose logs -f
```

## Kubernetes

For enterprise-scale deployments. A Helm chart is provided:

### Using Helm

```bash
# Add Loom Helm repository
helm repo add loom https://charts.loom-reviews.dev
helm repo update

# Install with default values
helm install loom loom/loom \
  --namespace loom \
  --create-namespace \
  --set auth.secret=your-secret-min-32-chars \
  --set llm.openai.apiKey=sk-...

# Or with custom values file
helm install loom loom/loom \
  --namespace loom \
  --create-namespace \
  -f values.yaml
```

### Example values.yaml

```yaml
# Loom Helm Values

replicaCount:
  web: 2
  worker: 2

image:
  repository: ghcr.io/loom-reviews/loom
  tag: latest
  pullPolicy: IfNotPresent

auth:
  secret: ""  # Required: 32+ char secret
  url: https://loom.example.com

llm:
  openai:
    apiKey: ""
  anthropic:
    apiKey: ""

oauth:
  github:
    clientId: ""
    clientSecret: ""
  google:
    clientId: ""
    clientSecret: ""

database:
  # Use external PostgreSQL
  external: true
  url: postgres://user:pass@host:5432/loom
  
  # Or deploy PostgreSQL as subchart
  # external: false
  # postgresql:
  #   enabled: true

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: loom.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: loom-tls
      hosts:
        - loom.example.com

resources:
  web:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 512Mi
  worker:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 2000m
      memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `BETTER_AUTH_SECRET` | Secret for session encryption (min 32 chars) | `your-random-secret-string` |
| `DATABASE_URL` | Database connection string | `file:/data/loom.db` or `postgres://...` |

### LLM Providers

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic/Claude API key |
| `GOOGLE_AI_API_KEY` | Google Gemini API key |

### OAuth Providers

| Variable | Description |
|----------|-------------|
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GITLAB_CLIENT_ID` | GitLab OAuth client ID |
| `GITLAB_CLIENT_SECRET` | GitLab OAuth client secret |

### Email Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_PROVIDER` | `smtp` or `resend` | `smtp` |
| `SMTP_HOST` | SMTP server hostname | - |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | - |
| `SMTP_PASS` | SMTP password | - |
| `RESEND_API_KEY` | Resend API key (if using Resend) | - |
| `EMAIL_FROM` | From address for emails | `noreply@loom.local` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `BETTER_AUTH_URL` | Public URL of your Loom instance | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level (`debug`, `info`, `warn`, `error`) | `info` |
| `WORKER_CONCURRENCY` | Number of concurrent review jobs | `1` |
| `JOB_TIMEOUT_MS` | Max job execution time | `300000` (5 min) |

## Database Configuration

### SQLite (Default)

Zero configuration, perfect for single-instance deployments:

```bash
DATABASE_URL=file:/data/loom.db
```

The database file is stored at `/data/loom.db` inside the container.

### PostgreSQL

Recommended for production and multi-instance deployments:

```bash
DATABASE_URL=postgres://user:password@host:5432/database
```

#### Connection Pool Settings

For high-traffic deployments, tune the connection pool:

```bash
DATABASE_URL=postgres://user:password@host:5432/database?connection_limit=20&pool_timeout=30
```

## Reverse Proxy Setup

### Nginx

```nginx
server {
    listen 80;
    server_name loom.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name loom.example.com;

    ssl_certificate /etc/letsencrypt/live/loom.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/loom.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Caddy

```caddyfile
loom.example.com {
    reverse_proxy localhost:3000
}
```

### Traefik (Docker Labels)

```yaml
services:
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.loom.rule=Host(`loom.example.com`)"
      - "traefik.http.routers.loom.entrypoints=websecure"
      - "traefik.http.routers.loom.tls.certresolver=letsencrypt"
      - "traefik.http.services.loom.loadbalancer.server.port=3000"
```

## Upgrading

### Docker

```bash
docker pull ghcr.io/loom-reviews/loom:latest
docker stop loom
docker rm loom
# Run with same options as before
docker run -d --name loom ...
```

### Docker Compose

```bash
docker compose pull
docker compose up -d
```

### Kubernetes

```bash
helm repo update
helm upgrade loom loom/loom -n loom -f values.yaml
```

### Database Migrations

Migrations run automatically on startup. For manual control:

```bash
# Docker
docker exec loom pnpm db:migrate

# Kubernetes
kubectl exec -it deploy/loom-web -n loom -- pnpm db:migrate
```

## Backup and Restore

### SQLite

```bash
# Backup
docker cp loom:/data/loom.db ./loom-backup-$(date +%Y%m%d).db

# Restore
docker cp ./loom-backup.db loom:/data/loom.db
docker restart loom
```

### PostgreSQL

```bash
# Backup
docker exec loom-db pg_dump -U loom loom > loom-backup-$(date +%Y%m%d).sql

# Restore
docker exec -i loom-db psql -U loom loom < loom-backup.sql
```

## Troubleshooting

### Loom won't start

**Check logs:**
```bash
docker logs loom
```

**Common issues:**
- Missing `BETTER_AUTH_SECRET` - This is required
- Invalid `DATABASE_URL` - Check connection string format
- Port already in use - Change the host port mapping

### Webhooks not working

1. **Check webhook URL** - Must be publicly accessible
2. **Verify secret** - Must match what's configured in git platform
3. **Check logs** for webhook handler errors:
   ```bash
   docker logs loom 2>&1 | grep webhook
   ```

### LLM calls failing

1. **Verify API key** is set correctly
2. **Check network** - Can the container reach the LLM API?
   ```bash
   docker exec loom curl -I https://api.openai.com
   ```
3. **Check rate limits** on your LLM provider

### Database connection issues

**PostgreSQL:**
```bash
# Test connection from container
docker exec loom pg_isready -h db -U loom
```

**SQLite:**
```bash
# Check file permissions
docker exec loom ls -la /data/
```

### High memory usage

- Reduce `WORKER_CONCURRENCY`
- Check for stuck jobs in the queue
- Consider using PostgreSQL instead of SQLite for large deployments

### Getting Help

- **GitHub Issues**: [github.com/loom-reviews/loom-reviews/issues](https://github.com/loom-reviews/loom-reviews/issues)
- **Discussions**: [github.com/loom-reviews/loom-reviews/discussions](https://github.com/loom-reviews/loom-reviews/discussions)
