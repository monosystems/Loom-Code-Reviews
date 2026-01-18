# Database Migrations

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom uses **Alembic** for database schema migrations, providing:
- Version-controlled schema changes
- Automatic migration generation
- Rollback capability
- Production-safe deployments

---

## Migration Tool: Alembic

### Why Alembic?

✅ **Pros:**
- Industry standard for Python/SQLAlchemy
- Auto-generates migrations from model changes
- Supports both online and offline migrations
- Strong PostgreSQL support
- Battle-tested in production

### Installation

```bash
pip install alembic
```

**Dependencies:**
```toml
# pyproject.toml
[project]
dependencies = [
    "alembic>=1.13.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",  # PostgreSQL driver
]
```

---

## Project Structure

```
loom-reviews/
├── alembic/
│   ├── versions/           ← Migration files
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_config_cache.py
│   │   └── ...
│   ├── env.py              ← Alembic environment config
│   ├── script.py.mako      ← Migration template
│   └── README
├── alembic.ini             ← Alembic configuration
├── src/
│   └── models/             ← SQLAlchemy models
│       ├── __init__.py
│       ├── repository.py
│       ├── job.py
│       ├── review.py
│       └── finding.py
└── ...
```

---

## Alembic Configuration

### alembic.ini

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Database URL (override with env var in production)
sqlalchemy.url = postgresql://loom:loom@localhost:5432/loom

# Migration file naming
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Logging
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### env.py

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import all models
from src.models import Base  # This imports all models

# Alembic Config object
config = context.config

# Override sqlalchemy.url with environment variable
database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
config.set_main_option("sqlalchemy.url", database_url)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL file)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (directly on database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Migration Workflow

### 1. Initialize Alembic (One-time)

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini and env.py as shown above
```

### 2. Create Initial Migration

```bash
# Auto-generate migration from SQLAlchemy models
alembic revision --autogenerate -m "initial schema"

# This creates: alembic/versions/20260118_1200_abc123_initial_schema.py
```

**Generated migration example:**
```python
"""initial schema

Revision ID: abc123def456
Revises: 
Create Date: 2026-01-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_id', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('webhook_secret', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('config_cache', postgresql.JSONB(), nullable=True),
        sa.Column('config_cache_updated_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('platform', 'platform_id')
    )
    op.create_index('idx_repositories_full_name', 'repositories', ['full_name'])
    op.create_index('idx_repositories_platform', 'repositories', ['platform'])
    op.create_index('idx_repositories_active', 'repositories', ['is_active'], 
                    postgresql_where=sa.text('is_active = true'))
    
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('repo_id', postgresql.UUID(), nullable=False),
        sa.Column('platform_pr_id', sa.String(255), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=False),
        sa.Column('head_sha', sa.String(64), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repo_id', 'head_sha')
    )
    # ... more tables and indexes
    

def downgrade() -> None:
    op.drop_table('findings')
    op.drop_table('reviews')
    op.drop_table('jobs')
    op.drop_table('repositories')
```

### 3. Review and Edit Migration

```bash
# Open generated migration file
vim alembic/versions/20260118_1200_abc123_initial_schema.py

# Verify:
# - Table names correct
# - Column types correct
# - Indexes created
# - Foreign keys correct
# - Defaults appropriate
```

### 4. Apply Migration

```bash
# Development
alembic upgrade head

# Production (with specific database URL)
DATABASE_URL=postgresql://user:pass@prod-db:5432/loom alembic upgrade head
```

### 5. Rollback if Needed

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all
alembic downgrade base
```

---

## Common Migration Patterns

### Adding a Column

```bash
# 1. Add column to SQLAlchemy model
# src/models/repository.py
class Repository(Base):
    # ... existing columns
    description = Column(String(500), nullable=True)  # NEW

# 2. Generate migration
alembic revision --autogenerate -m "add repository description"

# 3. Review generated migration
# alembic/versions/xxx_add_repository_description.py
def upgrade():
    op.add_column('repositories', 
        sa.Column('description', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('repositories', 'description')

# 4. Apply
alembic upgrade head
```

### Adding an Index

```python
def upgrade():
    op.create_index(
        'idx_jobs_pr_number', 
        'jobs', 
        ['pr_number']
    )

def downgrade():
    op.drop_index('idx_jobs_pr_number', 'jobs')
```

### Modifying a Column

```python
def upgrade():
    # Increase VARCHAR length
    op.alter_column(
        'repositories',
        'full_name',
        type_=sa.String(512),  # was 255
        existing_type=sa.String(255)
    )

def downgrade():
    op.alter_column(
        'repositories',
        'full_name',
        type_=sa.String(255),
        existing_type=sa.String(512)
    )
```

### Adding NOT NULL (Safely)

```python
def upgrade():
    # Step 1: Add column as nullable
    op.add_column('reviews', 
        sa.Column('pr_url', sa.String(500), nullable=True))
    
    # Step 2: Populate existing rows
    op.execute("""
        UPDATE reviews 
        SET pr_url = 'https://github.com/placeholder/' || pr_number
        WHERE pr_url IS NULL
    """)
    
    # Step 3: Make NOT NULL
    op.alter_column('reviews', 'pr_url', nullable=False)

def downgrade():
    op.drop_column('reviews', 'pr_url')
```

### Creating Enum Type

```python
def upgrade():
    # Create enum type
    status_enum = postgresql.ENUM(
        'queued', 'processing', 'completed', 'failed', 'cancelled',
        name='job_status'
    )
    status_enum.create(op.get_bind())
    
    # Use in column
    op.alter_column(
        'jobs',
        'status',
        type_=status_enum,
        postgresql_using='status::job_status'
    )

def downgrade():
    op.alter_column('jobs', 'status', type_=sa.String(20))
    postgresql.ENUM(name='job_status').drop(op.get_bind())
```

---

## Best Practices

### 1. Always Review Auto-Generated Migrations

Alembic's autogenerate is smart but not perfect:
- ✅ DO review every generated migration
- ✅ DO test migrations on dev database first
- ❌ DON'T blindly apply migrations to production

### 2. Make Migrations Reversible

```python
# GOOD: Reversible
def upgrade():
    op.add_column('jobs', sa.Column('worker_id', sa.String(100)))

def downgrade():
    op.drop_column('jobs', 'worker_id')

# BAD: Irreversible (data loss)
def upgrade():
    op.drop_table('old_jobs')

def downgrade():
    pass  # Can't restore dropped data!
```

### 3. One Change Per Migration

```python
# GOOD: Single purpose
# Migration: add_review_summary.py
def upgrade():
    op.add_column('reviews', sa.Column('summary', sa.Text()))

# BAD: Multiple unrelated changes
def upgrade():
    op.add_column('reviews', sa.Column('summary', sa.Text()))
    op.add_column('jobs', sa.Column('priority', sa.Integer()))
    op.create_table('new_table', ...)
```

### 4. Handle Large Tables Carefully

For large tables (> 1M rows):
```python
# Use partial indexes
op.create_index(
    'idx_jobs_queued',
    'jobs',
    ['created_at'],
    postgresql_where=sa.text("status = 'queued'")
)

# Add columns with default in two steps
# Step 1: Add nullable column
op.add_column('jobs', sa.Column('new_field', sa.Integer(), nullable=True))

# Step 2: Populate in batches (outside migration)
# Step 3: Make NOT NULL in separate migration
```

### 5. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test re-upgrade
alembic upgrade head
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Migration tested on dev database
- [ ] Migration tested on staging database
- [ ] Downgrade migration tested
- [ ] Data backup created
- [ ] Migration reviewed by team
- [ ] Performance impact assessed (for large tables)
- [ ] Deployment window planned (if downtime needed)

### Deployment Process

```bash
# 1. Backup database
pg_dump -h prod-db -U loom loom > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Apply migrations
DATABASE_URL=postgresql://user:pass@prod-db:5432/loom \
  alembic upgrade head

# 3. Verify
DATABASE_URL=postgresql://user:pass@prod-db:5432/loom \
  alembic current

# 4. If issues, rollback
DATABASE_URL=postgresql://user:pass@prod-db:5432/loom \
  alembic downgrade -1
```

### Zero-Downtime Migrations

For production systems that can't have downtime:

**Phase 1: Additive changes only**
```python
# Migration 1: Add new column (nullable)
def upgrade():
    op.add_column('jobs', sa.Column('new_status', sa.String(20), nullable=True))
```

**Phase 2: Dual-write**
```python
# Application code writes to both old and new columns
job.status = "queued"
job.new_status = "queued"
```

**Phase 3: Backfill data**
```sql
UPDATE jobs SET new_status = status WHERE new_status IS NULL;
```

**Phase 4: Make NOT NULL**
```python
# Migration 2: Make column NOT NULL
def upgrade():
    op.alter_column('jobs', 'new_status', nullable=False)
```

**Phase 5: Remove old column**
```python
# Migration 3: Drop old column
def upgrade():
    op.drop_column('jobs', 'status')
    op.alter_column('jobs', 'new_status', new_column_name='status')
```

---

## Troubleshooting

### Migration Conflicts

```bash
# Error: "Multiple head revisions are present"

# List current heads
alembic heads

# Merge heads
alembic merge -m "merge heads" head1 head2
```

### Failed Migration

```bash
# Error during migration, database in inconsistent state

# Check current version
alembic current

# Stamp database to specific revision (use carefully!)
alembic stamp abc123

# Or rollback and retry
alembic downgrade -1
alembic upgrade head
```

### Missing Migrations

```bash
# Application expects newer schema than database has

# Check current version
alembic current

# Check pending migrations
alembic history

# Apply missing migrations
alembic upgrade head
```

---

## Migration Checklist Template

Use this for each migration:

```markdown
## Migration: [name]

**Revision:** [revision_id]
**Date:** [date]
**Author:** [author]

### Changes
- [ ] Adds column X to table Y
- [ ] Creates index on column Z

### Testing
- [ ] Tested upgrade on dev
- [ ] Tested downgrade on dev
- [ ] Tested on staging
- [ ] Verified data integrity

### Performance
- [ ] Estimated execution time: [time]
- [ ] Locks required: [yes/no]
- [ ] Indexes created concurrently: [yes/no]

### Rollback Plan
- [ ] Downgrade migration tested
- [ ] Data loss acceptable: [yes/no]
- [ ] Backup created: [yes/no]

### Deployment
- [ ] Deployment window needed: [yes/no]
- [ ] Application restart required: [yes/no]
```

---

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [Database Schema](schema.md)
