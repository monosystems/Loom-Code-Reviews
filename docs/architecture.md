# Architecture

This document describes the technical architecture of Loom Code Reviews.

## Overview

Loom is designed as a modular, self-hosted system that can scale from a single Docker container to a distributed deployment. The architecture follows these principles:

1. **Separation of Concerns** - Web app handles UI/API, worker handles processing
2. **Platform Agnostic** - Adapters abstract away git platform differences
3. **LLM Agnostic** - Unified interface for any LLM provider
4. **Database Agnostic** - SQLite for simplicity, PostgreSQL for scale
5. **Configuration as Code** - Review behavior defined in repository

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Git Platforms                                     │
│        GitHub    GitLab    Bitbucket    Gitea    Azure DevOps               │
└──────────┬──────────┬──────────┬──────────┬──────────┬──────────────────────┘
           │          │          │          │          │
           │  Webhooks (PR opened, updated, commented)  │
           │          │          │          │          │
           ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Platform Adapters                                  │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   GitHub    │ │   GitLab    │ │  Bitbucket  │ │    Gitea    │  ...      │
│  │   Adapter   │ │   Adapter   │ │   Adapter   │ │   Adapter   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                                             │
│  Common Interface:                                                          │
│  • getFile(path) → content                                                  │
│  • getDiff(prId) → diff                                                     │
│  • postComment(prId, comment)                                               │
│  • getExistingComments(prId)                                                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Loom Web App                                    │
│                            (Next.js + tRPC)                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Webhook Handlers                             │   │
│  │  /api/webhooks/github  /api/webhooks/gitlab  /api/webhooks/...      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                       │                                     │
│                                       ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          Job Scheduler                               │   │
│  │            Creates review jobs in database queue                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           Dashboard UI                               │   │
│  │  • Repository management    • Review history                         │   │
│  │  • Prompt library           • Team settings                          │   │
│  │  • Analytics                • User settings                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                            tRPC API                                  │   │
│  │  Type-safe API for dashboard ↔ backend communication                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ Database Queue
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Loom Worker                                     │
│                       (Background Job Processor)                             │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          Job Processor                                │  │
│  │                                                                       │  │
│  │  1. Poll for pending jobs                                             │  │
│  │  2. Load repository config (.loom/config.yaml)                        │  │
│  │  3. Apply trigger rules (branches, paths, authors)                    │  │
│  │  4. Execute review pipeline                                           │  │
│  │  5. Post results back to git platform                                 │  │
│  │  6. Update job status                                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                       │                                     │
│                                       ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Review Pipeline                               │  │
│  │                                                                       │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐          │  │
│  │  │ Security │ → │  Style   │ → │   Docs   │ → │  Custom  │          │  │
│  │  │  Check   │   │  Check   │   │  Check   │   │  Script  │          │  │
│  │  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘          │  │
│  │       │              │              │              │                 │  │
│  │       ▼              ▼              ▼              ▼                 │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐          │  │
│  │  │   LLM    │   │   LLM    │   │   LLM    │   │  Script  │          │  │
│  │  │ Provider │   │ Provider │   │ Provider │   │  Runner  │          │  │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
             ┌──────────┐       ┌──────────┐       ┌──────────┐
             │  OpenAI  │       │  Claude  │       │  Ollama  │
             │   API    │       │   API    │       │  (local) │
             └──────────┘       └──────────┘       └──────────┘
```

## Components

### Apps

#### Web (`apps/web`)

The main Next.js application serving:

- **Dashboard UI** - React-based interface for managing repositories, viewing reviews, and configuring settings
- **Webhook Endpoints** - REST endpoints receiving events from git platforms
- **tRPC API** - Type-safe API for frontend-backend communication
- **Authentication** - Better Auth handling OAuth and email/password

**Key Routes:**
```
/                     # Landing page
/login                # Authentication
/dashboard            # Main dashboard
/dashboard/repos      # Repository management
/dashboard/reviews    # Review history
/dashboard/prompts    # Prompt library
/dashboard/settings   # User/org settings
/api/auth/*           # Better Auth endpoints
/api/webhooks/*       # Platform webhooks
/api/trpc/*           # tRPC endpoints
```

#### Worker (`apps/worker`)

Background processor handling:

- **Job Polling** - Continuously checks for pending review jobs
- **Config Loading** - Fetches `.loom/config.yaml` from repositories
- **Pipeline Execution** - Runs review checks in sequence
- **LLM Calls** - Sends prompts to configured providers
- **Result Posting** - Comments back on PRs via adapters

**Job States:**
```
PENDING → IN_PROGRESS → COMPLETED
                     → FAILED
                     → CANCELLED
```

### Packages

#### Core (`packages/core`)

The review engine orchestrating the entire review process:

```typescript
// Main entry point
interface ReviewEngine {
  executeReview(job: ReviewJob): Promise<ReviewResult>;
}

// Pipeline execution
interface Pipeline {
  name: string;
  model: string;
  prompt: string;
  severity: 'blocker' | 'warning' | 'info';
}

// Review result
interface ReviewResult {
  summary: string;
  comments: ReviewComment[];
  status: 'approve' | 'request_changes' | 'comment';
}
```

**Components:**
- `engine.ts` - Main orchestrator
- `pipeline.ts` - Pipeline execution
- `diff-parser.ts` - Git diff parsing
- `formatter.ts` - Output formatting

#### Adapters (`packages/adapters`)

Unified interface for git platforms:

```typescript
interface RepoAdapter {
  // Repository operations
  getFile(path: string, ref?: string): Promise<string | null>;
  getDiff(prId: string): Promise<DiffResult>;
  
  // Comment operations
  postComment(prId: string, comment: Comment): Promise<void>;
  postInlineComment(prId: string, comment: InlineComment): Promise<void>;
  getExistingComments(prId: string): Promise<Comment[]>;
  
  // PR operations
  getPullRequest(prId: string): Promise<PullRequest>;
  updatePullRequestStatus(prId: string, status: Status): Promise<void>;
}
```

**Implementations:**
- `github/` - GitHub Cloud & Enterprise
- `gitlab/` - GitLab Cloud & Self-hosted
- `bitbucket/` - Bitbucket Cloud & Server
- `gitea/` - Gitea & Forgejo
- `azure-devops/` - Azure DevOps

#### Database (`packages/db`)

Drizzle ORM schema and utilities:

```typescript
// Core tables
users           // User accounts
organizations   // Teams/orgs
memberships     // User ↔ Org mapping
repos           // Connected repositories
reviews         // Review history
comments        // Posted comments
prompts         // Custom prompt library
jobs            // Background job queue
sessions        // Auth sessions
```

**Database Support:**
- SQLite (default, zero-config)
- PostgreSQL (optional, for scale)

#### Queue (`packages/queue`)

Database-backed job queue:

```typescript
interface JobQueue {
  enqueue(job: Job): Promise<string>;
  dequeue(): Promise<Job | null>;
  complete(jobId: string, result: any): Promise<void>;
  fail(jobId: string, error: Error): Promise<void>;
  getStatus(jobId: string): Promise<JobStatus>;
}
```

**Why DB-based Queue:**
- No additional infrastructure (Redis) required
- Works with SQLite for simple deployments
- Scales to PostgreSQL when needed
- Jobs survive restarts

#### LLM (`packages/llm`)

Unified LLM client abstraction:

```typescript
interface LLMClient {
  chat(messages: Message[], options?: Options): Promise<Response>;
  stream(messages: Message[], options?: Options): AsyncIterable<Chunk>;
}

interface LLMConfig {
  provider: 'openai-compatible' | 'anthropic' | 'google';
  baseUrl?: string;
  model: string;
  apiKey: string;
}
```

**Providers:**
- `openai-compatible.ts` - Works with OpenAI, Ollama, vLLM, Together, Groq, etc.
- `anthropic.ts` - Claude models
- `google.ts` - Gemini models

#### Config (`packages/config`)

YAML configuration parser:

```typescript
interface LoomConfig {
  triggers: TriggerConfig;
  models: Record<string, ModelConfig>;
  pipelines: PipelineConfig[];
  output: OutputConfig;
  personas?: Record<string, PersonaConfig>;
}

// Validates and parses .loom/config.yaml
function parseConfig(yaml: string): LoomConfig;
```

## Data Flow

### PR Review Flow

```
1. Developer opens PR on GitHub
                │
                ▼
2. GitHub sends webhook to /api/webhooks/github
                │
                ▼
3. Webhook handler validates signature
                │
                ▼
4. Creates review job in database queue
   { repo_id, pr_number, platform: 'github', status: 'pending' }
                │
                ▼
5. Worker picks up job, marks 'in_progress'
                │
                ▼
6. Worker loads .loom/config.yaml from repo via adapter
                │
                ▼
7. Applies trigger rules (branches, paths, authors)
   - If no match → mark complete, skip
                │
                ▼
8. Fetches PR diff via adapter
                │
                ▼
9. For each pipeline in config:
   a. Load prompt (from repo or system default)
   b. Render prompt with diff context
   c. Call LLM provider
   d. Parse response into comments
                │
                ▼
10. Aggregate all comments, apply severity/grouping
                │
                ▼
11. Post review via adapter (inline comments + summary)
                │
                ▼
12. Mark job complete, store review in history
```

### Configuration Loading Flow

```
1. Worker needs config for repo X
                │
                ▼
2. Check cache (optional, TTL-based)
                │
                ▼
3. Call adapter.getFile('.loom/config.yaml')
                │
                ▼
4. Parse YAML with Zod validation
                │
                ▼
5. For each pipeline with prompt_file:
   a. Load prompt via adapter.getFile()
   b. Fall back to system prompt if not found
                │
                ▼
6. Return validated, enriched config
```

## Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations (for teams)
CREATE TABLE organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organization memberships
CREATE TABLE memberships (
  user_id TEXT REFERENCES users(id),
  org_id TEXT REFERENCES organizations(id),
  role TEXT DEFAULT 'member', -- 'owner', 'admin', 'member'
  PRIMARY KEY (user_id, org_id)
);

-- Connected repositories
CREATE TABLE repos (
  id TEXT PRIMARY KEY,
  org_id TEXT REFERENCES organizations(id),
  platform TEXT NOT NULL, -- 'github', 'gitlab', etc.
  platform_id TEXT NOT NULL, -- External ID
  name TEXT NOT NULL,
  full_name TEXT NOT NULL, -- owner/repo
  webhook_secret TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(platform, platform_id)
);

-- Review history
CREATE TABLE reviews (
  id TEXT PRIMARY KEY,
  repo_id TEXT REFERENCES repos(id),
  pr_number INTEGER NOT NULL,
  pr_title TEXT,
  status TEXT, -- 'pending', 'completed', 'failed'
  summary TEXT,
  comment_count INTEGER DEFAULT 0,
  llm_tokens_used INTEGER DEFAULT 0,
  duration_ms INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

-- Job queue
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL, -- 'review', 'sync', etc.
  payload TEXT NOT NULL, -- JSON
  status TEXT DEFAULT 'pending',
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 3,
  error TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- Custom prompts library
CREATE TABLE prompts (
  id TEXT PRIMARY KEY,
  org_id TEXT REFERENCES organizations(id),
  name TEXT NOT NULL,
  description TEXT,
  content TEXT NOT NULL,
  is_system BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);
```

## Deployment Modes

### Single Container (SQLite)

Simplest deployment - everything in one container:

```
┌─────────────────────────────────────┐
│           Docker Container          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │     Next.js App + Worker    │   │
│  └─────────────────────────────┘   │
│                 │                   │
│  ┌─────────────────────────────┐   │
│  │    SQLite (/data/loom.db)   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Docker Compose (PostgreSQL)

Recommended for teams:

```
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Web App     │  │    Worker     │  │  PostgreSQL   │
│   (Next.js)   │  │  (Processor)  │  │               │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                    Shared Database
```

### Kubernetes (Enterprise)

For large-scale deployments:

```
┌─────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                 │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │  Web Pod    │  │  Web Pod    │  (HPA)           │
│  │  (replica)  │  │  (replica)  │                  │
│  └──────┬──────┘  └──────┬──────┘                  │
│         └────────┬───────┘                         │
│                  │                                 │
│         ┌────────▼────────┐                        │
│         │    Ingress      │                        │
│         └─────────────────┘                        │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │ Worker Pod  │  │ Worker Pod  │  (HPA)           │
│  │  (replica)  │  │  (replica)  │                  │
│  └─────────────┘  └─────────────┘                  │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           PostgreSQL (StatefulSet)           │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Security Considerations

### Webhook Verification

All incoming webhooks are verified:

```typescript
// GitHub
const signature = request.headers['x-hub-signature-256'];
const isValid = verifyGitHubSignature(payload, signature, secret);

// GitLab
const token = request.headers['x-gitlab-token'];
const isValid = token === expectedToken;
```

### API Key Storage

LLM API keys are:
- Stored encrypted in database (for dashboard-configured keys)
- Or referenced via environment variables (`api_key_env: OPENAI_API_KEY`)

### Repository Access

- OAuth tokens are scoped to minimum required permissions
- Tokens are encrypted at rest
- Access is validated on each request

## Performance Considerations

### Caching

- **Config Cache** - Repository configs cached with TTL
- **Prompt Cache** - System prompts cached in memory
- **LLM Response Cache** - Optional deduplication for identical diffs

### Job Processing

- **Batch Size** - Worker processes one job at a time (configurable)
- **Timeout** - Jobs have max execution time (default: 5 minutes)
- **Retry** - Failed jobs retry with exponential backoff

### Database

- **Indexes** - All foreign keys and query patterns indexed
- **Cleanup** - Old jobs/reviews pruned periodically
- **Connection Pool** - PostgreSQL uses connection pooling

## Extensibility

### Adding a New Git Platform

1. Create adapter in `packages/adapters/src/{platform}/`
2. Implement `RepoAdapter` interface
3. Add webhook handler in `apps/web/src/app/api/webhooks/{platform}/`
4. Register in adapter factory

### Adding a New LLM Provider

1. Create provider in `packages/llm/src/providers/{provider}.ts`
2. Implement `LLMClient` interface
3. Add to provider factory in `packages/llm/src/client.ts`

### Adding a New Pipeline Step Type

1. Define step interface in `packages/core/src/review/types.ts`
2. Create step handler in `packages/core/src/review/steps/`
3. Register in pipeline executor
