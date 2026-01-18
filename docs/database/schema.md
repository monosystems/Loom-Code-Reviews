# Database Schema

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom uses **PostgreSQL** as the primary database for persistence. The schema is designed for:
- Simple self-hosted deployment
- High performance for webhook handling
- Efficient job queue processing
- Review history tracking

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  repositories   │
│─────────────────│
│ id (PK)         │
│ platform        │◄────────┐
│ platform_id     │         │
│ full_name       │         │
│ webhook_secret  │         │
│ is_active       │         │
│ config_cache    │         │
│ created_at      │         │
│ updated_at      │         │
└─────────────────┘         │
                            │
                            │ 1:N
                            │
┌─────────────────┐         │
│      jobs       │         │
│─────────────────│         │
│ id (PK)         │         │
│ repo_id (FK)    │─────────┘
│ platform_pr_id  │
│ pr_number       │
│ head_sha        │
│ status          │
│ priority        │
│ created_at      │
│ started_at      │
│ completed_at    │
│ error_message   │
│ retry_count     │
│ metadata        │
└────────┬────────┘
         │
         │ 1:1
         │
         ▼
┌─────────────────┐
│    reviews      │
│─────────────────│
│ id (PK)         │
│ job_id (FK)     │◄────────┐
│ pr_number       │         │
│ pr_title        │         │
│ pr_author       │         │
│ summary         │         │
│ total_findings  │         │
│ blocker_count   │         │
│ warning_count   │         │
│ info_count      │         │
│ llm_tokens_used │         │
│ duration_ms     │         │
│ created_at      │         │
└─────────────────┘         │
                            │ 1:N
                            │
┌─────────────────┐         │
│    findings     │         │
│─────────────────│         │
│ id (PK)         │         │
│ review_id (FK)  │─────────┘
│ pipeline_name   │
│ file_path       │
│ line_number     │
│ severity        │
│ category        │
│ message         │
│ suggestion      │
│ platform_comment_id │
│ posted_at       │
│ created_at      │
└─────────────────┘
```

---

## Tables

### 1. repositories

Stores connected git repositories.

```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,  -- 'github', 'gitlab', 'bitbucket', etc.
    platform_id VARCHAR(255) NOT NULL,  -- Platform-specific repo ID
    full_name VARCHAR(255) NOT NULL,  -- 'owner/repo'
    webhook_secret VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    config_cache JSONB,  -- Cached .loom/config.yaml
    config_cache_updated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(platform, platform_id)
);

CREATE INDEX idx_repositories_full_name ON repositories(full_name);
CREATE INDEX idx_repositories_platform ON repositories(platform);
CREATE INDEX idx_repositories_active ON repositories(is_active) WHERE is_active = true;
```

**Fields:**
- `id` - Internal UUID
- `platform` - Git platform identifier (github, gitlab, etc.)
- `platform_id` - Platform-specific repository ID (GitHub repo ID, GitLab project ID)
- `full_name` - Repository full name (owner/repo)
- `webhook_secret` - Secret for webhook signature verification
- `is_active` - Whether reviews are enabled
- `config_cache` - Cached configuration to avoid repeated fetches
- `config_cache_updated_at` - When config was last cached
- `created_at` - When repository was added
- `updated_at` - Last modification time

**Indexes:**
- Unique constraint on (platform, platform_id)
- Index on full_name for lookups
- Index on platform for filtering
- Partial index on is_active for active repo queries

---

### 2. jobs

Review job queue and execution history.

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    platform_pr_id VARCHAR(255) NOT NULL,  -- Platform-specific PR/MR ID
    pr_number INTEGER NOT NULL,
    head_sha VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',  
        -- 'queued', 'processing', 'completed', 'failed', 'cancelled'
    priority INTEGER NOT NULL DEFAULT 5,  -- 1-10, higher = more urgent
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB,  -- Additional context (branch names, author, etc.)
    
    UNIQUE(repo_id, head_sha)
);

CREATE INDEX idx_jobs_repo_id ON jobs(repo_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_priority ON jobs(priority DESC) WHERE status = 'queued';
```

**Fields:**
- `id` - Job UUID
- `repo_id` - Reference to repository
- `platform_pr_id` - Platform-specific PR/MR identifier
- `pr_number` - PR/MR number (user-visible)
- `head_sha` - Commit SHA being reviewed
- `status` - Current job status
- `priority` - Job priority (1-10, based on severity config)
- `created_at` - When job was created
- `started_at` - When worker picked up job
- `completed_at` - When job finished
- `error_message` - Error details if failed
- `retry_count` - Number of retry attempts
- `metadata` - Additional context (JSON)

**Status Values:**
- `queued` - Waiting for worker
- `processing` - Currently being processed
- `completed` - Successfully completed
- `failed` - Failed after retries
- `cancelled` - Manually cancelled

**Indexes:**
- Unique on (repo_id, head_sha) to prevent duplicate reviews
- Index on status for queue queries
- Index on created_at for history
- Priority index for queue ordering

---

### 3. reviews

Completed code reviews.

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    pr_number INTEGER NOT NULL,
    pr_title TEXT NOT NULL,
    pr_author VARCHAR(255) NOT NULL,
    summary TEXT,  -- Overall review summary
    total_findings INTEGER NOT NULL DEFAULT 0,
    blocker_count INTEGER NOT NULL DEFAULT 0,
    warning_count INTEGER NOT NULL DEFAULT 0,
    info_count INTEGER NOT NULL DEFAULT 0,
    llm_provider VARCHAR(100),  -- Which LLM was used
    llm_model VARCHAR(100),     -- Model name
    llm_tokens_used INTEGER,    -- Total tokens consumed
    duration_ms INTEGER,        -- Review processing time
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(job_id)
);

CREATE INDEX idx_reviews_pr_number ON reviews(pr_number);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);
CREATE INDEX idx_reviews_total_findings ON reviews(total_findings DESC);
```

**Fields:**
- `id` - Review UUID
- `job_id` - Reference to job (1:1 relationship)
- `pr_number` - PR/MR number
- `pr_title` - PR/MR title
- `pr_author` - Author username
- `summary` - Generated review summary
- `total_findings` - Total number of findings
- `blocker_count` - Number of blocker-severity findings
- `warning_count` - Number of warning-severity findings
- `info_count` - Number of info-severity findings
- `llm_provider` - LLM provider used (from base_url)
- `llm_model` - Model identifier
- `llm_tokens_used` - Tokens consumed (for cost tracking)
- `duration_ms` - Processing duration in milliseconds
- `created_at` - Review completion time

**Indexes:**
- Unique on job_id (one review per job)
- Index on pr_number for lookup
- Index on created_at for history
- Index on total_findings for filtering

---

### 4. findings

Individual code review findings/comments.

```sql
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    pipeline_name VARCHAR(100) NOT NULL,  -- Which pipeline generated this
    file_path TEXT,  -- Relative file path (NULL for general comments)
    line_number INTEGER,  -- Line number (NULL for file-level or general)
    severity VARCHAR(20) NOT NULL,  -- 'blocker', 'warning', 'info'
    category VARCHAR(100),  -- e.g., 'security', 'performance', 'style'
    message TEXT NOT NULL,  -- The finding description
    suggestion TEXT,  -- Suggested fix (optional)
    platform_comment_id VARCHAR(255),  -- Platform-specific comment ID
    posted_at TIMESTAMP,  -- When comment was posted to platform
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_findings_review_id ON findings(review_id);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_file_path ON findings(file_path);
CREATE INDEX idx_findings_pipeline ON findings(pipeline_name);
```

**Fields:**
- `id` - Finding UUID
- `review_id` - Reference to review
- `pipeline_name` - Which pipeline generated this finding
- `file_path` - File path (relative to repo root)
- `line_number` - Specific line number
- `severity` - Finding severity level
- `category` - Finding category/type
- `message` - Description of the issue
- `suggestion` - Recommended fix
- `platform_comment_id` - ID from git platform after posting
- `posted_at` - When comment was posted
- `created_at` - When finding was created

**Severity Values:**
- `blocker` - Critical issue, blocks merge
- `warning` - Important issue, should fix
- `info` - Suggestion, optional

**Indexes:**
- Index on review_id for fetching all findings
- Index on severity for filtering
- Index on file_path for file-level queries
- Index on pipeline_name for analytics

---

## Additional Tables (Future Considerations)

### webhook_deliveries (Optional)

Log of webhook deliveries for debugging.

```sql
CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    repo_id UUID REFERENCES repositories(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    signature_valid BOOLEAN NOT NULL,
    job_created BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_deliveries_platform ON webhook_deliveries(platform);
CREATE INDEX idx_webhook_deliveries_created_at ON webhook_deliveries(created_at DESC);
CREATE INDEX idx_webhook_deliveries_repo_id ON webhook_deliveries(repo_id);
```

**Note:** This table is optional and can be added later for debugging webhook issues.

---

## Data Types & Conventions

### UUIDs
- All primary keys use UUID v4 (PostgreSQL `gen_random_uuid()`)
- Benefits: No ID collisions, harder to guess, distributed-friendly

### Timestamps
- All timestamps are `TIMESTAMP WITHOUT TIME ZONE`
- Stored in UTC
- Application handles timezone conversion

### JSON Fields
- `JSONB` for structured data that needs querying
- Used for: config_cache, metadata, webhook payloads

### VARCHAR Lengths
- Platform identifiers: 50 chars
- IDs/secrets: 255 chars
- Usernames: 255 chars
- Paths: TEXT (unlimited)

---

## Relationships

### One-to-Many
- `repositories` → `jobs` (one repo, many review jobs)
- `reviews` → `findings` (one review, many findings)

### One-to-One
- `jobs` → `reviews` (one job creates one review)

### Cascade Behavior
- Delete repository → Delete all jobs → Delete all reviews → Delete all findings
- Ensures no orphaned data

---

## Performance Considerations

### Indexes
- All foreign keys are indexed
- Status fields indexed for queue queries
- Timestamp fields indexed for history queries
- Partial indexes for common WHERE conditions

### Partitioning (Future)
For high-volume deployments:
- Partition `jobs` by `created_at` (monthly)
- Partition `findings` by `created_at` (monthly)
- Archive old data after 6-12 months

### Query Optimization
```sql
-- Efficient queue query
SELECT * FROM jobs 
WHERE status = 'queued' 
ORDER BY priority DESC, created_at ASC 
LIMIT 10;

-- Efficient review history
SELECT r.*, COUNT(f.id) as finding_count
FROM reviews r
LEFT JOIN findings f ON f.review_id = r.id
WHERE r.created_at > NOW() - INTERVAL '30 days'
GROUP BY r.id
ORDER BY r.created_at DESC;
```

---

## Sample Data

### Example Repository
```sql
INSERT INTO repositories (platform, platform_id, full_name, webhook_secret, is_active)
VALUES (
    'github',
    '123456789',
    'acme-corp/api-server',
    'whsec_abc123def456',
    true
);
```

### Example Job
```sql
INSERT INTO jobs (repo_id, platform_pr_id, pr_number, head_sha, status, priority)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'MDExOlB1bGxSZXF1ZXN0MTIzNDU2',
    42,
    'abc123def456789012345678901234567890abcd',
    'queued',
    7
);
```

### Example Review
```sql
INSERT INTO reviews (
    job_id, pr_number, pr_title, pr_author,
    total_findings, blocker_count, warning_count, info_count,
    llm_provider, llm_model, llm_tokens_used, duration_ms
)
VALUES (
    '660e8400-e29b-41d4-a716-446655440000',
    42,
    'Add user authentication',
    'developer',
    5, 1, 3, 1,
    'openai',
    'gpt-4',
    2500,
    32000
);
```

### Example Finding
```sql
INSERT INTO findings (
    review_id, pipeline_name, file_path, line_number,
    severity, category, message, suggestion
)
VALUES (
    '770e8400-e29b-41d4-a716-446655440000',
    'security',
    'src/auth/login.py',
    45,
    'blocker',
    'security',
    'SQL injection vulnerability: User input is directly concatenated into SQL query',
    'Use parameterized queries: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
);
```

---

## Migration Strategy

See [migrations.md](migrations.md) for detailed migration approach using Alembic.

---

## Schema Evolution

### Version 0.1.0 (MVP)
- Core tables: repositories, jobs, reviews, findings
- Basic indexes
- PostgreSQL-specific features (UUID, JSONB)

### Future Versions
- Add `webhook_deliveries` table
- Add analytics tables (usage metrics, costs)
- Add caching tables (LLM responses)
- Partitioning for high volume

---

## Database Sizing Estimates

**For a typical deployment (100 repos, 500 PRs/month):**

| Table | Rows/Month | Storage/Month |
|-------|-----------|---------------|
| repositories | ~10 new | ~10 KB |
| jobs | ~500 | ~500 KB |
| reviews | ~500 | ~200 KB |
| findings | ~2,500 | ~5 MB |
| **Total** | **~3,500** | **~6 MB** |

**Annual growth:** ~70 MB

**Scaling:** Comfortable up to millions of reviews before partitioning needed.

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Migration Strategy](migrations.md)
- [Architecture Overview](../architecture/overview.md)
