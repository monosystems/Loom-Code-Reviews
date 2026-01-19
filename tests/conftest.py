"""Pytest configuration and fixtures."""
import sys
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import inspect


# Mock the database connection module before any imports
mock_connection = MagicMock()
mock_connection.Base = MagicMock()
mock_connection.engine = MagicMock()
mock_connection.async_session_maker = MagicMock()
sys.modules['src.database.connection'] = mock_connection


def create_mock_inspector():
    """Create a mock SQLAlchemy inspector with column information."""
    
    def create_mock_column(name, default_value=None):
        """Create a mock column that behaves like a dict and has .default attribute."""
        mock_default = MagicMock()
        mock_default.arg = default_value
        
        mock_column = MagicMock()
        mock_column.__getitem__ = lambda self, key: {'name': name, 'type': MagicMock(), 'default': mock_default if default_value is not None else None}[key]
        mock_column.name = name
        mock_column.default = mock_default if default_value is not None else None
        return mock_column
    
    def mock_get_columns(table_name):
        """Return mock column definitions based on table name."""
        mock_columns = {
            'jobs': [
                create_mock_column('id'),
                create_mock_column('repo_id'),
                create_mock_column('platform_pr_id'),
                create_mock_column('pr_number'),
                create_mock_column('head_sha'),
                create_mock_column('status', 'queued'),
                create_mock_column('priority', 5),
                create_mock_column('started_at'),
                create_mock_column('completed_at'),
                create_mock_column('error_message'),
                create_mock_column('retry_count', 0),
                create_mock_column('job_metadata'),
                create_mock_column('created_at'),
                create_mock_column('updated_at'),
            ],
            'reviews': [
                create_mock_column('id'),
                create_mock_column('job_id'),
                create_mock_column('pr_number'),
                create_mock_column('pr_title'),
                create_mock_column('pr_author'),
                create_mock_column('summary'),
                create_mock_column('total_findings', 0),
                create_mock_column('blocker_count', 0),
                create_mock_column('warning_count', 0),
                create_mock_column('info_count', 0),
                create_mock_column('llm_provider'),
                create_mock_column('llm_model'),
                create_mock_column('llm_tokens_used'),
                create_mock_column('duration_ms'),
                create_mock_column('created_at'),
                create_mock_column('updated_at'),
            ],
            'findings': [
                create_mock_column('id'),
                create_mock_column('review_id'),
                create_mock_column('pipeline_name'),
                create_mock_column('file_path'),
                create_mock_column('line_number'),
                create_mock_column('severity'),
                create_mock_column('category'),
                create_mock_column('message'),
                create_mock_column('suggestion'),
                create_mock_column('platform_comment_id'),
                create_mock_column('posted_at'),
                create_mock_column('created_at'),
                create_mock_column('updated_at'),
            ],
            'repositories': [
                create_mock_column('id'),
                create_mock_column('platform'),
                create_mock_column('platform_id'),
                create_mock_column('full_name'),
                create_mock_column('webhook_secret'),
                create_mock_column('is_active'),
                create_mock_column('config_cache'),
                create_mock_column('config_cache_updated_at'),
                create_mock_column('created_at'),
                create_mock_column('updated_at'),
            ],
        }
        return mock_columns.get(table_name, [])
    
    mock_inspector = MagicMock()
    mock_inspector.get_columns = mock_get_columns
    return mock_inspector


# Mock the inspect function globally
_original_inspect = inspect
_mock_inspector_instance = create_mock_inspector()


def _mock_inspect(obj):
    """Mock inspect function that returns mock inspector."""
    return _mock_inspector_instance


# Patch sqlalchemy.inspect
import sqlalchemy
sqlalchemy.inspect = _mock_inspect


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    from unittest.mock import AsyncMock
    from sqlalchemy.ext.asyncio import AsyncSession
    
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def sample_uuid():
    """Create a sample UUID."""
    return uuid4()
