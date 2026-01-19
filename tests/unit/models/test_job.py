"""Unit tests for the Job model."""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import inspect

from src.models.job import Job


class TestJobModel:
    """Test cases for the Job model."""

    def test_job_table_name(self):
        """Test that the table name is correctly set."""
        assert Job.__tablename__ == "jobs"

    def test_job_has_uuid_id(self):
        """Test that Job has a UUID id column."""
        assert hasattr(Job, 'id')
        inspector = inspect(Job)
        columns = {col['name']: col for col in inspector.get_columns('jobs')}
        assert 'id' in columns

    def test_job_has_created_at(self):
        """Test that Job has created_at timestamp."""
        assert hasattr(Job, 'created_at')

    def test_job_has_updated_at(self):
        """Test that Job has updated_at timestamp."""
        assert hasattr(Job, 'updated_at')

    def test_job_repo_id_column(self):
        """Test that Job has repo_id column."""
        assert hasattr(Job, 'repo_id')
        inspector = inspect(Job)
        columns = {col['name']: col for col in inspector.get_columns('jobs')}
        assert 'repo_id' in columns

    def test_job_platform_pr_id_column(self):
        """Test that Job has platform_pr_id column."""
        assert hasattr(Job, 'platform_pr_id')

    def test_job_pr_number_column(self):
        """Test that Job has pr_number column."""
        assert hasattr(Job, 'pr_number')

    def test_job_head_sha_column(self):
        """Test that Job has head_sha column."""
        assert hasattr(Job, 'head_sha')

    def test_job_status_column(self):
        """Test that Job has status column."""
        assert hasattr(Job, 'status')

    def test_job_priority_column(self):
        """Test that Job has priority column."""
        assert hasattr(Job, 'priority')

    def test_job_started_at_column(self):
        """Test that Job has started_at column."""
        assert hasattr(Job, 'started_at')

    def test_job_completed_at_column(self):
        """Test that Job has completed_at column."""
        assert hasattr(Job, 'completed_at')

    def test_job_error_message_column(self):
        """Test that Job has error_message column."""
        assert hasattr(Job, 'error_message')

    def test_job_retry_count_column(self):
        """Test that Job has retry_count column."""
        assert hasattr(Job, 'retry_count')

    def test_job_job_metadata_column(self):
        """Test that Job has job_metadata column."""
        assert hasattr(Job, 'job_metadata')

    def test_job_repository_relationship(self):
        """Test that Job has repository relationship."""
        assert hasattr(Job, 'repository')

    def test_job_review_relationship(self):
        """Test that Job has review relationship."""
        assert hasattr(Job, 'review')

    def test_job_status_default_value(self):
        """Test that status has default 'queued' in column definition."""
        inspector = inspect(Job)
        columns = {col['name']: col for col in inspector.get_columns('jobs')}
        assert columns['status'].default.arg == "queued"

    def test_job_priority_default_value(self):
        """Test that priority has default 5 in column definition."""
        inspector = inspect(Job)
        columns = {col['name']: col for col in inspector.get_columns('jobs')}
        assert columns['priority'].default.arg == 5

    def test_job_retry_count_default_value(self):
        """Test that retry_count has default 0 in column definition."""
        inspector = inspect(Job)
        columns = {col['name']: col for col in inspector.get_columns('jobs')}
        assert columns['retry_count'].default.arg == 0

    def test_job_instantiation(self):
        """Test that Job can be instantiated."""
        job_id = uuid4()
        repo_id = uuid4()
        job = Job(
            id=job_id,
            repo_id=repo_id,
            platform_pr_id="123",
            pr_number=1,
            head_sha="abc123"
        )
        assert job.id == job_id
        assert job.repo_id == repo_id
        assert job.platform_pr_id == "123"
        assert job.pr_number == 1
        assert job.head_sha == "abc123"

    def test_job_repr(self):
        """Test Job string representation."""
        job = Job(
            repo_id=uuid4(),
            platform_pr_id="123",
            pr_number=1,
            head_sha="abc123"
        )
        repr_str = repr(job)
        assert "Job" in repr_str
