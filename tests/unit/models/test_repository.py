"""Unit tests for the Repository model."""
from datetime import datetime
from uuid import uuid4

import pytest

from src.models.repository import Repository


class TestRepositoryModel:
    """Test cases for the Repository model."""

    def test_repository_table_name(self):
        """Test that the table name is correctly set."""
        assert Repository.__tablename__ == "repositories"

    def test_repository_has_uuid_id(self):
        """Test that Repository has a UUID id column."""
        assert hasattr(Repository, 'id')

    def test_repository_has_created_at(self):
        """Test that Repository has created_at timestamp."""
        assert hasattr(Repository, 'created_at')

    def test_repository_has_updated_at(self):
        """Test that Repository has updated_at timestamp."""
        assert hasattr(Repository, 'updated_at')

    def test_repository_platform_column(self):
        """Test that Repository has platform column."""
        assert hasattr(Repository, 'platform')

    def test_repository_platform_id_column(self):
        """Test that Repository has platform_id column."""
        assert hasattr(Repository, 'platform_id')

    def test_repository_full_name_column(self):
        """Test that Repository has full_name column."""
        assert hasattr(Repository, 'full_name')

    def test_repository_webhook_secret_column(self):
        """Test that Repository has webhook_secret column."""
        assert hasattr(Repository, 'webhook_secret')

    def test_repository_is_active_column(self):
        """Test that Repository has is_active column."""
        assert hasattr(Repository, 'is_active')

    def test_repository_config_cache_column(self):
        """Test that Repository has config_cache column."""
        assert hasattr(Repository, 'config_cache')

    def test_repository_config_cache_updated_at_column(self):
        """Test that Repository has config_cache_updated_at column."""
        assert hasattr(Repository, 'config_cache_updated_at')

    def test_repository_relationship(self):
        """Test that Repository has jobs relationship."""
        assert hasattr(Repository, 'jobs')

    def test_repository_instantiation(self):
        """Test that Repository can be instantiated."""
        repo_id = uuid4()
        repo = Repository(
            id=repo_id,
            platform="github",
            platform_id="123",
            full_name="test/repo",
            webhook_secret="secret"
        )
        assert repo.id == repo_id
        assert repo.platform == "github"
        assert repo.platform_id == "123"
        assert repo.full_name == "test/repo"

    def test_repository_repr(self):
        """Test Repository string representation."""
        repo = Repository(
            platform="github",
            platform_id="123",
            full_name="test/repo",
            webhook_secret="secret"
        )
        repr_str = repr(repo)
        assert "Repository" in repr_str
