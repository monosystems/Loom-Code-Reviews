"""add indexes

Revision ID: a1aafca93930
Revises: 184a0cce8697
Create Date: 2026-01-19 17:39:11.569445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1aafca93930'
down_revision: Union[str, Sequence[str], None] = '184a0cce8697'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes."""
    op.create_index('idx_repositories_platform', 'repositories', ['platform'], unique=False)
    op.create_index('idx_repositories_active', 'repositories', ['is_active'], unique=False, postgresql_where=sa.text('is_active = true'))
    op.create_unique_constraint('uq_repositories_platform_id', 'repositories', ['platform', 'platform_id'])
    op.create_index('idx_jobs_status', 'jobs', ['status'], unique=False)
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'], unique=False)
    op.create_index('idx_jobs_priority', 'jobs', ['priority'], unique=False, postgresql_where=sa.text("status = 'queued'"))
    op.create_unique_constraint('uq_jobs_repo_head', 'jobs', ['repo_id', 'head_sha'])
    op.create_index('idx_reviews_pr_number', 'reviews', ['pr_number'], unique=False)
    op.create_index('idx_reviews_created_at', 'reviews', ['created_at'], unique=False)
    op.create_index('idx_reviews_total_findings', 'reviews', ['total_findings'], unique=False)
    op.create_index('idx_findings_severity', 'findings', ['severity'], unique=False)
    op.create_index('idx_findings_file_path', 'findings', ['file_path'], unique=False)
    op.create_index('idx_findings_pipeline', 'findings', ['pipeline_name'], unique=False)


def downgrade() -> None:
    """Remove indexes."""
    op.drop_index('idx_findings_pipeline', table_name='findings')
    op.drop_index('idx_findings_file_path', table_name='findings')
    op.drop_index('idx_findings_severity', table_name='findings')
    op.drop_index('idx_reviews_total_findings', table_name='reviews')
    op.drop_index('idx_reviews_created_at', table_name='reviews')
    op.drop_index('idx_reviews_pr_number', table_name='reviews')
    op.drop_constraint('uq_jobs_repo_head', 'jobs')
    op.drop_index('idx_jobs_priority', table_name='jobs')
    op.drop_index('idx_jobs_created_at', table_name='jobs')
    op.drop_index('idx_jobs_status', table_name='jobs')
    op.drop_constraint('uq_repositories_platform_id', 'repositories')
    op.drop_index('idx_repositories_active', table_name='repositories')
    op.drop_index('idx_repositories_platform', table_name='repositories')
