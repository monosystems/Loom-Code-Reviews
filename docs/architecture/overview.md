# System Architecture Overview

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Vision

Loom is a **self-hostable, open-source AI code review platform** that provides CodeRabbit-level functionality with complete control over:
- LLM providers (any OpenAI-compatible API)
- Git platforms (GitHub, GitLab, Bitbucket, Gitea, Azure DevOps, etc.)
- Deployment infrastructure
- Data privacy

---

## Core Principles

1. **Platform Agnostic** - Works with any git platform via adapter pattern
2. **LLM Agnostic** - Works with any OpenAI-compatible API (base_url + api_key)
3. **Configuration as Code** - `.loom/config.yaml` in repository defines behavior
4. **Fully Open Source** - AGPL-3.0 licensed, community-driven
5. **Privacy First** - Your code never leaves your infrastructure

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Git Platforms                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  GitHub  │  │  GitLab  │  │Bitbucket │  │  Gitea   │  ...   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        │  Webhooks   │  Webhooks   │  Webhooks   │  Webhooks
        └─────────────┴─────────────┴─────────────┘
                              ▼
        ┌─────────────────────────────────────────────────┐
        │         Webhook Handler (FastAPI)               │
        │  - Receives webhook events                      │
        │  - Validates signatures                         │
        │  - Routes to appropriate adapter                │
        │  - Creates review jobs                          │
        └──────────────────────┬──────────────────────────┘
                               │
                               ▼
        ┌─────────────────────────────────────────────────┐
        │         Job Queue (Redis + Celery)              │
        │  - Async job processing                         │
        │  - Priority queues                              │
        │  - Retry logic                                  │
        └──────────────────────┬──────────────────────────┘
                               │
                               ▼
        ┌─────────────────────────────────────────────────┐
        │           Review Workers (Celery)               │
        │                                                  │
        │  ┌────────────────────────────────────────┐    │
        │  │  1. Fetch PR/MR diff via adapter       │    │
        │  │  2. Load .loom/config.yaml from repo   │    │
        │  │  3. Load prompt templates               │    │
        │  │  4. Call LLM provider(s)                │    │
        │  │  5. Parse responses                     │    │
        │  │  6. Post comments back via adapter      │    │
        │  └────────────────────────────────────────┘    │
        └────────┬─────────────────────────┬──────────────┘
                 │                         │
         ┌───────▼────────┐       ┌───────▼────────────────────────┐
         │  Git Platform  │       │  LLM API Client                │
         │    Adapters    │       │  (OpenAI-compatible)           │
         │                │       │                                │
         │ • GitHub       │       │  base_url + api_key            │
         │ • GitLab       │       │                                │
         │ • Bitbucket    │       │  Examples:                     │
         │ • Gitea        │       │  • OpenAI API                  │
         │ • Azure DevOps │       │  • Anthropic API               │
         │                │       │  • Ollama (localhost)          │
         │                │       │  • Groq, Together.ai, etc.     │
         └────────────────┘       └────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────────────────────┐
        │         Database (PostgreSQL)                    │
        │  - Repositories                                  │
        │  - Review jobs & history                         │
        │  - Configuration cache                           │
        └──────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Webhook Handler (FastAPI)

**Responsibility:** Receive and validate webhook events

**Key Features:**
- Platform-specific signature validation
- Event routing to appropriate adapter
- Rate limiting per repository
- Job creation and queuing

**Technology:**
- FastAPI (Python 3.11+)
- Async I/O
- Pydantic for validation

**Endpoints:**
```
POST /webhooks/github
POST /webhooks/gitlab
POST /webhooks/bitbucket
POST /webhooks/gitea
POST /webhooks/azure-devops
POST /health
GET  /metrics (Prometheus)
```

### 2. Job Queue (Redis + Celery)

**Responsibility:** Asynchronous job processing

**Key Features:**
- Priority queues (blocker > warning > info)
- Automatic retries with exponential backoff
- Dead letter queue for failed jobs
- Job status tracking

**Technology:**
- Redis (message broker + cache)
- Celery (distributed task queue)

**Queue Types:**
- `review.high` - Blocking issues
- `review.normal` - Warnings
- `review.low` - Info/suggestions

### 3. Review Workers (Celery)

**Responsibility:** Execute code reviews

**Key Features:**
- Parallel processing (configurable concurrency)
- Context gathering from repository
- Multi-pipeline execution
- Error handling and rollback

**Process Flow:**
1. Receive job from queue
2. Fetch PR/MR diff via platform adapter
3. Clone repository (shallow) or fetch via API
4. Load `.loom/config.yaml`
5. Load prompt templates from `.loom/prompts/`
6. For each pipeline:
   - Prepare context (diff + config + prompts)
   - Call LLM provider
   - Parse structured response
7. Aggregate all findings
8. Post comments back to PR/MR via adapter
9. Update job status

### 4. Git Platform Adapters

**Responsibility:** Abstract platform-specific APIs

**Interface:**
```python
class GitAdapter(ABC):
    @abstractmethod
    async def verify_webhook(request: Request) -> bool
    
    @abstractmethod
    async def fetch_diff(repo: str, pr_number: int) -> Diff
    
    @abstractmethod
    async def fetch_file(repo: str, path: str, ref: str) -> str
    
    @abstractmethod
    async def post_comment(repo: str, pr_number: int, comment: Comment)
    
    @abstractmethod
    async def get_pr_info(repo: str, pr_number: int) -> PRInfo
```

**Implementations:**
- `GitHubAdapter`
- `GitLabAdapter`
- `BitbucketAdapter`
- `GiteaAdapter`
- `AzureDevOpsAdapter`

### 5. LLM API Client

**Responsibility:** HTTP client for OpenAI-compatible APIs

**Key Concept:** All modern LLM providers support OpenAI's API format. We use a simple HTTP client with configurable base URL and API key.

**Configuration:**
```python
class LLMConfig:
    base_url: str      # e.g., "https://api.openai.com/v1"
    api_key: str       # API key for authentication
    model: str         # Model name (e.g., "gpt-4")
    temperature: float # 0.0 - 1.0
    max_tokens: int    # Response length limit
```

**Supported Providers (OpenAI-compatible):**
- **OpenAI:** `https://api.openai.com/v1`
- **Anthropic:** `https://api.anthropic.com/v1` (with compatibility layer)
- **Ollama:** `http://localhost:11434/v1`
- **Groq:** `https://api.groq.com/openai/v1`
- **Together.ai:** `https://api.together.xyz/v1`
- **OpenRouter:** `https://openrouter.ai/api/v1`
- Any self-hosted OpenAI-compatible endpoint

**Implementation:**
```python
async def call_llm(config: LLMConfig, prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json={
                "model": config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

### 6. Database (PostgreSQL)

**Responsibility:** Persistent storage

**Key Tables:**
- `repositories` - Connected repos
- `jobs` - Review job queue and history
- `reviews` - Completed reviews
- `comments` - Individual findings

**Technology:**
- PostgreSQL 16+
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)

---

## Data Flow

See [data-flow.md](data-flow.md) for detailed request processing.

---

## Configuration

### Repository Configuration

Each repository has a `.loom/config.yaml`:

```yaml
# LLM models to use
models:
  default:
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4
    temperature: 0.0
    max_tokens: 4000

  claude:
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-20250514
    temperature: 0.0
    max_tokens: 4000
  
  local:
    base_url: http://localhost:11434/v1
    api_key_env: OLLAMA_API_KEY  # Can be empty for Ollama
    model: codellama:13b
    temperature: 0.0
    max_tokens: 2000

# Review pipelines
pipelines:
  - name: security
    model: default
    prompt_file: .loom/prompts/security.md
    severity: blocker
  
  - name: quality
    model: default
    prompt_file: .loom/prompts/quality.md
    severity: warning

# Trigger rules
triggers:
  branches: ["main", "develop"]
  ignore_paths: ["*.lock", "dist/**"]
  max_changes: 1000
```

See [configuration/config-schema.md](../configuration/config-schema.md) for full schema.

### Prompt Templates

Located in `.loom/prompts/*.md`:

```markdown
# Security Review

You are a security expert reviewing code.

## Focus Areas
- SQL injection
- XSS vulnerabilities
- Authentication issues

## Response Format
Return JSON array of findings.

## Code Changes
{{diff}}
```

See [configuration/prompt-format.md](../configuration/prompt-format.md) for format spec.

---

## Deployment Models

### Self-Hosted

**Single Node (Development/Small Teams):**
```bash
docker-compose up
```

Components on single server:
- FastAPI (webhook handler)
- Celery workers (1-3 workers)
- PostgreSQL
- Redis

**Multi-Node (Production/Large Teams):**
- Load balancer → Multiple FastAPI instances
- Shared PostgreSQL (or managed DB service)
- Shared Redis (or managed cache service)
- Multiple Celery workers on separate machines
- Horizontal scaling as needed

See [deployment/](../deployment/) for detailed setup guides.

---

## Non-Functional Requirements

### Performance
- **Webhook Response:** < 100ms
- **Review Completion:** < 60s for typical PR (< 500 lines)
- **Concurrent Reviews:** 10+ per worker
- **Queue Throughput:** 1000+ reviews/hour (horizontal scaling)

### Reliability
- **Availability:** 99.9% uptime (SaaS)
- **Job Retry:** 3 attempts with exponential backoff
- **Data Persistence:** Daily backups
- **Graceful Degradation:** Continue with available LLMs if one fails

### Security
- **Webhook Verification:** HMAC signature validation
- **API Key Storage:** Environment variables or secrets manager
- **Code Isolation:** Sandboxed execution (future)
- **Rate Limiting:** Per-repo and per-user limits

### Scalability
- **Horizontal Scaling:** Add more workers
- **Database:** Read replicas for scaling reads
- **Cache:** Redis for config and frequent queries
- **Queue:** Redis cluster for high throughput

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| API Server | FastAPI | Async, fast, auto-docs, type-safe |
| Language | Python 3.11+ | Best LLM ecosystem, AI-friendly |
| Database | PostgreSQL 16 | Mature, reliable, multi-tenant ready |
| Queue | Celery + Redis | Proven, scalable, flexible |
| ORM | SQLAlchemy 2.0 | Type-safe, async support |
| Validation | Pydantic | Type validation, settings management |
| Testing | pytest + httpx | Async testing support |
| Deployment | Docker | Portable, easy to deploy |
| Monitoring | Prometheus | Industry standard |
| Logging | Structured JSON | Machine-readable |

---

## Open Questions / Future Decisions

### MVP Phase
- [ ] **Shallow git clone vs API-only?** (API-only = simpler, less resources)
- [ ] **Config validation:** Server-side or client-side CLI tool?
- [ ] **Retry strategy:** Exponential backoff parameters?
- [ ] **LLM timeout:** Per-provider or global?

### Post-MVP
- [ ] **Dashboard:** Separate React app or integrated Next.js?
- [ ] **Real-time updates:** WebSockets or Server-Sent Events?
- [ ] **Multi-region:** Geographic distribution for SaaS?
- [ ] **Caching strategy:** What to cache and for how long?

---

## References

- [Data Flow](data-flow.md) - Detailed request processing
- [Adapter Pattern](adapter-pattern.md) - Multi-platform design
- [API Specification](../api/) - Detailed API docs
- [Database Schema](../database/schema.md) - Database design
- [Configuration Schema](../configuration/config-schema.md) - Config format

---

## Changelog

### 2026-01-18 - Initial Design
- Created architecture overview
- Defined core components
- Established tech stack
- Documented deployment models
