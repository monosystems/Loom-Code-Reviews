# Local Development Setup

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

This guide covers setting up Loom for local development on your machine. Perfect for:
- Contributing to Loom
- Testing configuration changes
- Developing new features
- Running local reviews

---

## Prerequisites

### Required Software

- **Python 3.11+**
- **PostgreSQL 16+**
- **Redis 7+**
- **Git**
- **Docker** (optional but recommended)

### System Requirements

- **OS:** Linux, macOS, or Windows (with WSL2)
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 5GB free space

---

## Quick Start (Docker)

**Fastest way to get started:**

```bash
# 1. Clone repository
git clone https://github.com/your-org/loom.git
cd loom

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your tokens
nano .env

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec api alembic upgrade head

# 6. Done! API running at http://localhost:8000
```

---

## Manual Setup (Without Docker)

### 1. Install System Dependencies

#### Ubuntu/Debian

```bash
# Python 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Redis
sudo apt install -y redis-server

# Development tools
sudo apt install -y git build-essential libpq-dev
```

#### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python
brew install python@3.11

# PostgreSQL
brew install postgresql@16
brew services start postgresql@16

# Redis
brew install redis
brew services start redis

# Development tools
xcode-select --install
```

#### Windows (WSL2)

```bash
# Install WSL2 first
wsl --install

# Then follow Ubuntu instructions above
```

---

### 2. Clone Repository

```bash
git clone https://github.com/your-org/loom.git
cd loom
```

---

### 3. Create Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate venv
# Linux/macOS:
source venv/bin/activate

# Windows (WSL):
source venv/bin/activate
```

**Verify:**
```bash
which python
# Should show: /path/to/loom/venv/bin/python

python --version
# Should show: Python 3.11.x
```

---

### 4. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install dev requirements
pip install -r requirements-dev.txt
```

**requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.6
httpx==0.26.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
pyyaml==6.0.1
jinja2==3.1.3
```

**requirements-dev.txt:**
```
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==24.1.1
ruff==0.1.14
mypy==1.8.0
pre-commit==3.6.0
httpx==0.26.0  # For testing
```

---

### 5. Setup PostgreSQL

#### Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In psql:
CREATE DATABASE loom;
CREATE USER loom WITH PASSWORD 'loom';
GRANT ALL PRIVILEGES ON DATABASE loom TO loom;
\q
```

**macOS (no sudo needed):**
```bash
psql postgres

CREATE DATABASE loom;
CREATE USER loom WITH PASSWORD 'loom';
GRANT ALL PRIVILEGES ON DATABASE loom TO loom;
\q
```

#### Verify Connection

```bash
psql -U loom -h localhost -d loom
# Password: loom

# Should connect successfully
\q
```

---

### 6. Setup Redis

#### Start Redis

```bash
# Linux
sudo systemctl start redis
sudo systemctl enable redis

# macOS (already started by brew)
brew services start redis

# Verify
redis-cli ping
# Should return: PONG
```

---

### 7. Configure Environment

#### Create .env File

```bash
cp .env.example .env
```

**Edit .env:**
```bash
# Database
DATABASE_URL=postgresql://loom:loom@localhost:5432/loom

# Redis
REDIS_URL=redis://localhost:6379/0

# GitHub (get from https://github.com/settings/tokens)
GITHUB_API_TOKEN=ghp_your_token_here
GITHUB_WEBHOOK_SECRET=dev-webhook-secret-123

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-key-here

# Development
LOG_LEVEL=DEBUG
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production
```

---

### 8. Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic revision --autogenerate -m "initial schema"

# Run migrations
alembic upgrade head

# Verify
psql -U loom -d loom -c "\dt"
# Should show: repositories, jobs, reviews, findings
```

---

### 9. Start Development Server

#### Terminal 1: API Server

```bash
# Activate venv
source venv/bin/activate

# Start FastAPI with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Terminal 2: Celery Worker

```bash
# Activate venv
source venv/bin/activate

# Start Celery worker
celery -A src.worker worker --loglevel=info --concurrency=2
```

**Output:**
```
[tasks]
  . src.tasks.review_pr
  
[2026-01-18 15:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2026-01-18 15:00:00,001: INFO/MainProcess] celery@hostname ready.
```

---

### 10. Verify Installation

#### Health Check

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-18T15:00:00Z"
}
```

#### API Documentation

Open browser: http://localhost:8000/docs

**You should see:** Interactive Swagger UI with all API endpoints.

---

## Development Workflow

### Project Structure

```
loom/
├── src/                    # Application code
│   ├── main.py            # FastAPI app
│   ├── api/               # API routes
│   │   └── webhooks.py    # Webhook endpoints
│   ├── adapters/          # Platform adapters
│   │   ├── github.py
│   │   ├── gitlab.py
│   │   └── ...
│   ├── models/            # SQLAlchemy models
│   │   ├── repository.py
│   │   ├── job.py
│   │   └── ...
│   ├── tasks/             # Celery tasks
│   │   └── review.py      # Review task
│   └── worker.py          # Celery worker
├── alembic/               # Database migrations
│   └── versions/
├── tests/                 # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                  # Documentation
├── .env                   # Environment variables (gitignored)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Dev dependencies
├── docker-compose.yml     # Docker setup
└── README.md
```

---

### Running Tests

#### All Tests

```bash
pytest
```

#### With Coverage

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

#### Specific Test

```bash
pytest tests/unit/test_adapters.py::test_github_webhook
```

#### Watch Mode

```bash
pytest-watch
```

---

### Code Quality

#### Format Code (Black)

```bash
# Format all files
black src/ tests/

# Check only (no changes)
black --check src/ tests/
```

#### Lint Code (Ruff)

```bash
# Lint
ruff check src/ tests/

# Auto-fix
ruff check --fix src/ tests/
```

#### Type Check (Mypy)

```bash
mypy src/
```

#### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
```

---

### Database Management

#### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add new field"

# Create empty migration (for data migrations)
alembic revision -m "migrate data"
```

#### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Downgrade one version
alembic downgrade -1
```

#### Check Status

```bash
# Current version
alembic current

# Migration history
alembic history

# Show pending migrations
alembic show head
```

#### Reset Database

```bash
# Drop all tables
alembic downgrade base

# Re-create all tables
alembic upgrade head
```

---

### Testing Webhooks Locally

#### Using ngrok

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok tunnel
ngrok http 8000
```

**Output:**
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Configure webhook in GitHub:**
- URL: `https://abc123.ngrok.io/webhooks/github`
- Secret: Your `GITHUB_WEBHOOK_SECRET`
- Events: Pull requests

#### Using curl

```bash
# Test GitHub webhook
curl -X POST http://localhost:8000/webhooks/github \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"action":"opened"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/github_pr_opened.json
```

---

### Debugging

#### VS Code Launch Configuration

**File:** `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Celery Worker",
      "type": "python",
      "request": "launch",
      "module": "celery",
      "args": [
        "-A", "src.worker",
        "worker",
        "--loglevel=debug",
        "--concurrency=1"
      ],
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

#### Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in
breakpoint()
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Common Issues

### Port Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn src.main:app --port 8001
```

### Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Start if not running
sudo systemctl start postgresql  # Linux
brew services start postgresql@16  # macOS

# Check connection
psql -U loom -h localhost -d loom
```

### Redis Connection Refused

**Error:**
```
redis.exceptions.ConnectionError: Connection refused
```

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Start if not running
sudo systemctl start redis  # Linux
brew services start redis  # macOS
```

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Alembic Migration Conflicts

**Error:**
```
alembic.util.exc.CommandError: Multiple head revisions are present
```

**Solution:**
```bash
# Merge heads
alembic merge heads -m "merge migrations"

# Apply merge
alembic upgrade head
```

---

## Hot Reloading

### FastAPI Auto-Reload

Uvicorn automatically reloads on code changes:
```bash
uvicorn src.main:app --reload
```

**Watches:** `.py` files in current directory

### Celery Auto-Reload

Use `watchdog` for Celery:
```bash
pip install watchdog

celery -A src.worker worker --loglevel=info --autoreload
```

---

## Performance Tips

### Development Mode

- Use `--reload` for FastAPI (slower but convenient)
- Set `LOG_LEVEL=DEBUG` to see all logs
- Use `concurrency=1` for Celery (easier debugging)

### Testing Mode

- Use in-memory SQLite: `DATABASE_URL=sqlite:///:memory:`
- Use fakeredis: `pip install fakeredis`
- Mock external APIs

---

## Next Steps

1. **Read Architecture:** [docs/architecture/overview.md](../architecture/overview.md)
2. **Configure Loom:** [docs/configuration/config-schema.md](../configuration/config-schema.md)
3. **Write Tests:** See `tests/` directory
4. **Submit PR:** Contribution guidelines in `CONTRIBUTING.md`

---

## References

- [Docker Deployment](docker.md)
- [Environment Variables](environment.md)
- [API Documentation](../api/webhooks.md)
- [Database Schema](../database/schema.md)
