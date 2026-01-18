# Deployment Documentation

This directory contains comprehensive deployment guides for Loom Code Reviews.

---

## Quick Links

- **[Docker Deployment](docker.md)** - Production-ready containerized deployment
- **[Environment Variables](environment.md)** - Complete variable reference
- **[Development Setup](development.md)** - Local development guide

---

## Deployment Options

### 1. Docker Compose (Recommended)

**Best for:** Small teams, single-server deployments

**Effort:** ⭐ Easy  
**Setup Time:** 10 minutes  
**Scalability:** Up to ~100 repos

```bash
docker-compose up -d
```

See: [docker.md](docker.md)

---

### 2. Manual Installation

**Best for:** Development, understanding internals

**Effort:** ⭐⭐ Medium  
**Setup Time:** 30 minutes  
**Scalability:** Up to ~50 repos

```bash
pip install -r requirements.txt
uvicorn src.main:app
```

See: [development.md](development.md)

---

### 3. Kubernetes (Future)

**Best for:** Large organizations, high availability

**Effort:** ⭐⭐⭐ Advanced  
**Setup Time:** 2-4 hours  
**Scalability:** Unlimited

*Documentation coming soon*

---

## Quick Start Matrix

| Use Case | Guide | Setup Time | Complexity |
|----------|-------|------------|------------|
| Try Loom locally | [development.md](development.md) | 15 min | Low |
| Small team (1-10 devs) | [docker.md](docker.md) | 20 min | Low |
| Medium team (10-50 devs) | [docker.md](docker.md) + scaling | 45 min | Medium |
| Enterprise (50+ devs) | Kubernetes (future) | 2-4 hours | High |

---

## Prerequisites

### All Deployments

- **Git platform account** (GitHub, GitLab, etc.)
- **LLM API key** (OpenAI, Anthropic, etc.)
- **Basic command line knowledge**

### Docker Deployment

- Docker 24.0+
- Docker Compose 2.20+
- 2GB RAM
- 10GB disk

### Manual Deployment

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- 4GB RAM
- 5GB disk

---

## Configuration Steps

### 1. Choose Deployment Method

- **New to Docker?** → Start with [development.md](development.md)
- **Production deployment?** → Use [docker.md](docker.md)
- **Just exploring?** → Use [development.md](development.md)

### 2. Set Environment Variables

See: [environment.md](environment.md)

**Required:**
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
GITHUB_API_TOKEN=ghp_...
OPENAI_API_KEY=sk-...
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Services

**Docker:**
```bash
docker-compose up -d
```

**Manual:**
```bash
# Terminal 1
uvicorn src.main:app

# Terminal 2
celery -A src.worker worker
```

### 5. Configure Webhooks

In your git platform:
- **URL:** `https://your-loom.com/webhooks/github`
- **Secret:** Your `GITHUB_WEBHOOK_SECRET`
- **Events:** Pull requests

### 6. Test

```bash
curl http://localhost:8000/health
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Git Platform (GitHub, etc.)               │
└────────────────────────┬────────────────────────────────────┘
                         │ Webhook
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI                                │
│                    (Webhook Handler)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ Queue Job
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       Redis                                  │
│                    (Job Queue)                               │
└────────────────────────┬────────────────────────────────────┘
                         │ Process Job
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                            │
│           (Fetch diff, call LLM, post comments)              │
└───┬─────────────────────────────────────────────────────┬───┘
    │                                                      │
    ▼                                                      ▼
┌─────────────┐                                    ┌─────────────┐
│ PostgreSQL  │                                    │  LLM API    │
│ (Database)  │                                    │ (OpenAI)    │
└─────────────┘                                    └─────────────┘
```

---

## Environment Variables Quick Reference

### Core Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/loom

# Redis
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
```

### Platform Tokens

```bash
# GitHub
GITHUB_API_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-secret

# GitLab
GITLAB_API_TOKEN=glpat-...
GITLAB_WEBHOOK_SECRET=your-secret
```

### LLM APIs

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

Complete list: [environment.md](environment.md)

---

## Deployment Checklist

### Development

- [ ] Install dependencies
- [ ] Configure `.env` file
- [ ] Start PostgreSQL
- [ ] Start Redis
- [ ] Run migrations
- [ ] Start FastAPI server
- [ ] Start Celery worker
- [ ] Test webhook locally (ngrok)

### Production

- [ ] Set strong passwords
- [ ] Configure firewall
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups
- [ ] Set resource limits
- [ ] Enable rate limiting
- [ ] Configure logging
- [ ] Test disaster recovery
- [ ] Document runbook

---

## Monitoring

### Health Checks

```bash
# API
curl http://localhost:8000/health

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping

# Workers
docker-compose exec worker celery -A src.worker inspect active
```

### Metrics

Access Prometheus metrics:
```
http://localhost:8000/metrics
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

---

## Scaling Guidelines

### Small Deployment (1-10 repos)

```yaml
api:
  deploy:
    replicas: 1
worker:
  deploy:
    replicas: 2
```

**Resources:**
- 2 CPU cores
- 4GB RAM
- 20GB disk

### Medium Deployment (10-100 repos)

```yaml
api:
  deploy:
    replicas: 3
worker:
  deploy:
    replicas: 5
```

**Resources:**
- 4 CPU cores
- 8GB RAM
- 50GB disk

### Large Deployment (100+ repos)

```yaml
api:
  deploy:
    replicas: 5
worker:
  deploy:
    replicas: 10
```

**Resources:**
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ disk

---

## Security Checklist

### Before Production

- [ ] Change all default passwords
- [ ] Generate new `SECRET_KEY`
- [ ] Enable HTTPS (TLS certificates)
- [ ] Restrict `ALLOWED_HOSTS`
- [ ] Use secrets management (Vault, AWS Secrets)
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Run security audit
- [ ] Enable Sentry error tracking
- [ ] Set up monitoring alerts

---

## Backup Strategy

### Database Backups

```bash
# Daily backup (cron)
0 2 * * * /path/to/loom/scripts/backup.sh
```

**Retention:**
- Daily: 30 days
- Weekly: 12 weeks
- Monthly: 12 months

### Configuration Backups

Backup these files:
- `.env` (encrypted!)
- `docker-compose.yml`
- `alembic/versions/`
- Repository configs (`.loom/config.yaml`)

---

## Support & Resources

### Documentation

- [Architecture](../architecture/overview.md)
- [API Reference](../api/webhooks.md)
- [Configuration](../configuration/config-schema.md)
- [Database Schema](../database/schema.md)
- [Platform Adapters](../adapters/README.md)

### Community

- GitHub Issues: https://github.com/your-org/loom/issues
- Discussions: https://github.com/your-org/loom/discussions

### Commercial Support

Contact: support@loom.dev (future SaaS offering)

---

## Troubleshooting

### Common Issues

| Issue | Guide | Section |
|-------|-------|---------|
| Can't connect to database | [environment.md](environment.md) | Database |
| Redis connection failed | [development.md](development.md) | Redis Setup |
| Webhook not received | [docker.md](docker.md) | Networking |
| Worker not processing | [development.md](development.md) | Celery |
| Out of memory | [docker.md](docker.md) | Scaling |

### Getting Help

1. Check logs: `docker-compose logs`
2. Search issues: GitHub Issues
3. Ask community: GitHub Discussions
4. Contact support: For commercial customers

---

## Next Steps

1. **Choose your deployment method** (Docker recommended)
2. **Read the corresponding guide** in detail
3. **Set up environment variables** ([environment.md](environment.md))
4. **Deploy!** Follow step-by-step instructions
5. **Configure your first repository** ([../configuration/](../configuration/))
6. **Monitor and iterate** (check logs, metrics)

Good luck! 🚀
