# Environment Variables

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom uses environment variables for configuration. This document lists all available variables, their purpose, and default values.

**Configuration Priority:**
1. Environment variables (highest)
2. `.env` file
3. Default values (lowest)

---

## Quick Reference

### Required Variables

These **must** be set for Loom to function:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/loom
REDIS_URL=redis://host:6379/0
```

### Platform Tokens

At least one platform must be configured:

```bash
# GitHub (most common)
GITHUB_API_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-secret

# Or GitLab
GITLAB_API_TOKEN=glpat-...
GITLAB_WEBHOOK_SECRET=your-secret

# Or others...
```

### LLM API Keys

At least one LLM provider must be configured:

```bash
# OpenAI (most common)
OPENAI_API_KEY=sk-...

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Complete Variable List

### Database

#### DATABASE_URL
- **Description:** PostgreSQL connection string
- **Required:** Yes
- **Format:** `postgresql://user:password@host:port/database`
- **Example:** `postgresql://loom:loom@localhost:5432/loom`
- **Default:** None

**Connection String Format:**
```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

**SSL Example:**
```
postgresql://user:pass@host:5432/loom?sslmode=require
```

**Connection Pooling Parameters:**
```
postgresql://user:pass@host:5432/loom?pool_size=20&max_overflow=10
```

---

### Redis

#### REDIS_URL
- **Description:** Redis connection string for job queue and caching
- **Required:** Yes
- **Format:** `redis://[password@]host:port/db`
- **Example:** `redis://localhost:6379/0`
- **Default:** None

**With Password:**
```
redis://:password@localhost:6379/0
```

**Redis Sentinel:**
```
redis-sentinel://host1:26379,host2:26379/mymaster/0
```

---

### GitHub

#### GITHUB_API_TOKEN
- **Description:** GitHub Personal Access Token for API calls
- **Required:** If using GitHub
- **Format:** `ghp_...` (classic) or `github_pat_...` (fine-grained)
- **Scopes Required:** `repo`, `pull_request`
- **Example:** `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

**How to Create:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Copy token immediately (won't be shown again)

#### GITHUB_WEBHOOK_SECRET
- **Description:** Secret for verifying GitHub webhook signatures
- **Required:** If using GitHub
- **Format:** Any string (recommend 32+ random characters)
- **Example:** `whsec_abc123def456ghi789jkl012mno345pqr678`
- **Generate:** `openssl rand -hex 32`

**Configure in GitHub:**
1. Repository Settings → Webhooks → Add webhook
2. Set "Secret" field to this value

---

### GitLab

#### GITLAB_API_TOKEN
- **Description:** GitLab Personal Access Token
- **Required:** If using GitLab
- **Format:** `glpat-...`
- **Scopes Required:** `api` or `read_repository` + `write_repository`
- **Example:** `glpat-xxxxxxxxxxxxxxxxxxxx`

**How to Create:**
1. GitLab Settings → Access Tokens
2. Name: "Loom Code Reviews"
3. Scopes: `api`
4. Create token

#### GITLAB_WEBHOOK_SECRET
- **Description:** Secret token for GitLab webhooks
- **Required:** If using GitLab
- **Format:** Any string
- **Example:** `your-secret-token-here`

#### GITLAB_BASE_URL
- **Description:** GitLab API base URL (for self-hosted)
- **Required:** No (defaults to gitlab.com)
- **Default:** `https://gitlab.com/api/v4`
- **Example:** `https://gitlab.company.com/api/v4`

---

### Bitbucket

#### BITBUCKET_USERNAME
- **Description:** Bitbucket username
- **Required:** If using Bitbucket
- **Example:** `your-username`

#### BITBUCKET_APP_PASSWORD
- **Description:** Bitbucket App Password
- **Required:** If using Bitbucket
- **Permissions Required:** Repository Read, Pull Requests Write
- **Example:** `ATBBxxxxxxxxxxxxxxxxxx`

**How to Create:**
1. Bitbucket Settings → App passwords → Create app password
2. Permissions: Repository Read, Pull requests Read & Write
3. Copy password (won't be shown again)

#### BITBUCKET_WEBHOOK_UUIDS
- **Description:** Comma-separated list of webhook UUIDs
- **Required:** If using Bitbucket
- **Format:** `{uuid1},{uuid2},{uuid3}`
- **Example:** `{12345678-1234-1234-1234-123456789012}`

---

### Gitea

#### GITEA_API_TOKEN
- **Description:** Gitea access token
- **Required:** If using Gitea
- **Example:** `abc123def456...`

**How to Create:**
1. Gitea Settings → Applications → Generate New Token
2. Copy token

#### GITEA_WEBHOOK_SECRET
- **Description:** Secret for Gitea webhook verification
- **Required:** If using Gitea
- **Format:** Any string
- **Example:** `your-gitea-secret`

#### GITEA_BASE_URL
- **Description:** Gitea API base URL
- **Required:** Yes if using Gitea
- **Format:** `https://your-gitea.com/api/v1`
- **Example:** `https://gitea.company.com/api/v1`

---

### Azure DevOps

#### AZURE_DEVOPS_PAT
- **Description:** Azure DevOps Personal Access Token
- **Required:** If using Azure DevOps
- **Scopes Required:** Code (Read & Write), Pull Request Threads (Read & Write)
- **Example:** `abc123def456ghi789...`

**How to Create:**
1. Azure DevOps → User Settings → Personal access tokens
2. New Token
3. Scopes: Code (Read & Write)

#### AZURE_DEVOPS_WEBHOOK_SECRET
- **Description:** Password for Azure DevOps webhook Basic Auth
- **Required:** If using Azure DevOps
- **Example:** `your-webhook-password`

#### AZURE_DEVOPS_ORGANIZATION
- **Description:** Azure DevOps organization name
- **Required:** If using Azure DevOps
- **Example:** `your-organization`

---

### LLM Providers

#### OPENAI_API_KEY
- **Description:** OpenAI API key
- **Required:** If using OpenAI models
- **Format:** `sk-...`
- **Example:** `sk-proj-abc123...`

**Get Key:**
https://platform.openai.com/api-keys

#### ANTHROPIC_API_KEY
- **Description:** Anthropic (Claude) API key
- **Required:** If using Claude models
- **Format:** `sk-ant-...`
- **Example:** `sk-ant-api03-abc123...`

**Get Key:**
https://console.anthropic.com/settings/keys

#### GROQ_API_KEY
- **Description:** Groq API key (fast inference)
- **Required:** If using Groq
- **Format:** `gsk-...`
- **Example:** `gsk_abc123...`

**Get Key:**
https://console.groq.com/keys

#### TOGETHER_API_KEY
- **Description:** Together.ai API key
- **Required:** If using Together.ai
- **Example:** `abc123...`

**Get Key:**
https://api.together.xyz/settings/api-keys

#### OPENROUTER_API_KEY
- **Description:** OpenRouter API key
- **Required:** If using OpenRouter
- **Format:** `sk-or-...`
- **Example:** `sk-or-v1-abc123...`

**Get Key:**
https://openrouter.ai/keys

#### OLLAMA_API_KEY
- **Description:** Ollama API key (optional for local)
- **Required:** No
- **Default:** None (Ollama doesn't require auth for localhost)

---

### Application Settings

#### LOG_LEVEL
- **Description:** Logging verbosity
- **Required:** No
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default:** `INFO`
- **Example:** `WARNING`

**When to Use:**
- `DEBUG` - Development, debugging issues
- `INFO` - Production default
- `WARNING` - Production minimal logging
- `ERROR` - Production critical only

#### WORKERS
- **Description:** Number of Celery worker processes
- **Required:** No
- **Default:** `3`
- **Example:** `5`

**Recommendation:**
- Small instance: `3`
- Medium instance: `5-10`
- Large instance: `10-20`

#### ENVIRONMENT
- **Description:** Environment name
- **Required:** No
- **Options:** `development`, `staging`, `production`
- **Default:** `development`
- **Example:** `production`

**Effects:**
- `development`: Debug mode on, reload on code change
- `production`: Debug mode off, optimized

---

### Monitoring & Observability

#### SENTRY_DSN
- **Description:** Sentry DSN for error tracking
- **Required:** No (recommended for production)
- **Format:** `https://...@sentry.io/...`
- **Example:** `https://abc123@o123456.ingest.sentry.io/7890123`

**Get DSN:**
1. Create Sentry project
2. Settings → Client Keys (DSN)

#### PROMETHEUS_ENABLED
- **Description:** Enable Prometheus metrics endpoint
- **Required:** No
- **Options:** `true`, `false`
- **Default:** `true`
- **Example:** `true`

**Metrics Endpoint:**
`/metrics` (Prometheus format)

---

### Security

#### SECRET_KEY
- **Description:** Secret key for JWT signing, encryption
- **Required:** Yes (production)
- **Format:** 32+ random characters
- **Generate:** `openssl rand -hex 32`
- **Example:** `abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

⚠️ **CRITICAL:** Change this in production! Never use default!

#### ALLOWED_HOSTS
- **Description:** Comma-separated list of allowed hostnames
- **Required:** No (production recommended)
- **Default:** `*` (allow all)
- **Example:** `loom.company.com,api.loom.company.com`

**Security:** Restrict to actual domains in production.

#### CORS_ORIGINS
- **Description:** Comma-separated allowed CORS origins
- **Required:** No
- **Default:** `*`
- **Example:** `https://app.company.com,https://dashboard.company.com`

---

### Rate Limiting

#### RATE_LIMIT_ENABLED
- **Description:** Enable rate limiting
- **Required:** No
- **Default:** `true`
- **Example:** `true`

#### RATE_LIMIT_PER_HOUR
- **Description:** Max webhook requests per repository per hour
- **Required:** No
- **Default:** `100`
- **Example:** `200`

#### RATE_LIMIT_GLOBAL
- **Description:** Max total requests per hour
- **Required:** No
- **Default:** `1000`
- **Example:** `5000`

---

## Environment File Templates

### Development (.env.dev)

```bash
# Database
DATABASE_URL=postgresql://loom:loom@localhost:5432/loom

# Redis
REDIS_URL=redis://localhost:6379/0

# GitHub
GITHUB_API_TOKEN=ghp_your_token_here
GITHUB_WEBHOOK_SECRET=dev-webhook-secret

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Application
LOG_LEVEL=DEBUG
ENVIRONMENT=development
WORKERS=2

# Security
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=*
```

### Production (.env.prod)

```bash
# Database (use strong password!)
DATABASE_URL=postgresql://loom:STRONG_PASSWORD@postgres:5432/loom

# Redis (use password!)
REDIS_URL=redis://:REDIS_PASSWORD@redis:6379/0

# GitHub
GITHUB_API_TOKEN=${GITHUB_TOKEN_FROM_VAULT}
GITHUB_WEBHOOK_SECRET=${GITHUB_SECRET_FROM_VAULT}

# GitLab
GITLAB_API_TOKEN=${GITLAB_TOKEN_FROM_VAULT}
GITLAB_WEBHOOK_SECRET=${GITLAB_SECRET_FROM_VAULT}

# LLM APIs
OPENAI_API_KEY=${OPENAI_KEY_FROM_VAULT}
ANTHROPIC_API_KEY=${ANTHROPIC_KEY_FROM_VAULT}

# Application
LOG_LEVEL=WARNING
ENVIRONMENT=production
WORKERS=10

# Security
SECRET_KEY=${SECRET_KEY_FROM_VAULT}  # Generate: openssl rand -hex 32
ALLOWED_HOSTS=loom.company.com,api.loom.company.com
CORS_ORIGINS=https://dashboard.company.com

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
PROMETHEUS_ENABLED=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_HOUR=200
RATE_LIMIT_GLOBAL=5000
```

---

## Security Best Practices

### 1. Never Commit Secrets

**Add to `.gitignore`:**
```
.env
.env.*
*.env
secrets/
```

### 2. Use Secrets Management

**Option A: AWS Secrets Manager**
```bash
export GITHUB_API_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id loom/github-token --query SecretString --output text)
```

**Option B: HashiCorp Vault**
```bash
export GITHUB_API_TOKEN=$(vault kv get -field=token secret/loom/github)
```

**Option C: Docker Secrets**
```yaml
services:
  api:
    secrets:
      - github_token
    environment:
      GITHUB_API_TOKEN_FILE: /run/secrets/github_token
```

### 3. Rotate Credentials Regularly

- API tokens: Every 90 days
- Webhook secrets: Every 6 months
- Database passwords: Every year

### 4. Use Least Privilege

- Only grant required scopes
- Use fine-grained tokens when available
- Separate tokens per environment

---

## Validation

### Check Required Variables

```bash
#!/bin/bash
# scripts/check-env.sh

required_vars=(
  "DATABASE_URL"
  "REDIS_URL"
  "SECRET_KEY"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  fi
done

echo "✅ All required variables are set"
```

### Test Configuration

```python
# scripts/test-env.py
import os
from sqlalchemy import create_engine
import redis

# Test database
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
engine.connect()
print("✅ Database connection successful")

# Test redis
redis_url = os.getenv("REDIS_URL")
r = redis.from_url(redis_url)
r.ping()
print("✅ Redis connection successful")

# Test GitHub token
github_token = os.getenv("GITHUB_API_TOKEN")
import httpx
response = httpx.get(
    "https://api.github.com/user",
    headers={"Authorization": f"Bearer {github_token}"}
)
response.raise_for_status()
print("✅ GitHub API token valid")
```

---

## Troubleshooting

### "DATABASE_URL not set"

**Solution:**
```bash
export DATABASE_URL=postgresql://loom:loom@localhost:5432/loom
```

Or create `.env` file:
```bash
echo "DATABASE_URL=postgresql://loom:loom@localhost:5432/loom" > .env
```

### "Invalid GitHub token"

**Check token scopes:**
```bash
curl -H "Authorization: Bearer $GITHUB_API_TOKEN" \
  https://api.github.com/user
```

**If 401:** Token is invalid or expired. Create new token.

### "Redis connection refused"

**Check Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**If not running:**
```bash
# Docker
docker-compose up -d redis

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

---

## References

- [Docker Deployment](docker.md)
- [Development Setup](development.md)
- [Configuration Schema](../configuration/config-schema.md)
