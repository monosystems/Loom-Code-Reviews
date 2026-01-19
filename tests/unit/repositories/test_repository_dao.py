"""Unit tests for RepositoryDAO."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestRepositoryDAO:
    """Test cases for RepositoryDAO."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def dao(self, mock_session):
        """Create a RepositoryDAO instance with mock session."""
        from src.repositories.repository import RepositoryDAO
        return RepositoryDAO(mock_session)

    @pytest.fixture
    def sample_repo(self):
        """Create a sample Repository object."""
        from src.models.repository import Repository
        repo = Repository(
            id=uuid4(),
            platform="github",
            platform_id="123",
            full_name="test/repo",
            webhook_secret="secret"
        )
        return repo

    @pytest.mark.asyncio
    async def test_get_by_id(self, dao, mock_session, sample_repo):
        """Test getting a repository by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_repo
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_id(sample_repo.id)

        assert result == sample_repo
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, dao, mock_session):
        """Test getting a repository by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, dao, mock_session, sample_repo):
        """Test getting all repositories."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_repo]
        mock_session.execute.return_value = mock_result

        result = await dao.get_all()

        assert len(result) == 1
        assert result[0] == sample_repo

    @pytest.mark.asyncio
    async def test_create(self, dao, mock_session):
        """Test creating a repository."""
        from src.models.repository import Repository
        
        mock_instance = MagicMock()
        mock_instance.id = uuid4()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.execute.return_value = MagicMock()

        result = await dao.create(
            platform="github",
            platform_id="456",
            full_name="new/repo",
            webhook_secret="new_secret"
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update(self, dao, mock_session, sample_repo):
        """Test updating a repository."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        result = await dao.update(sample_repo.id, is_active=False)

        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, dao, mock_session, sample_repo):
        """Test deleting a repository."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        result = await dao.delete(sample_repo.id)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, dao, mock_session):
        """Test deleting a repository that doesn't exist."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        result = await dao.delete(uuid4())

        assert result is False

    @pytest.mark.asyncio
    async def test_get_by_platform_and_id(self, dao, mock_session, sample_repo):
        """Test getting a repository by platform and platform_id."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_repo
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_platform_and_id("github", "123")

        assert result == sample_repo
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_full_name(self, dao, mock_session, sample_repo):
        """Test getting a repository by full_name."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_repo
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_full_name("test/repo")

        assert result == sample_repo
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_repositories(self, dao, mock_session, sample_repo):
        """Test getting active repositories."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_repo]
        mock_session.execute.return_value = mock_result

        result = await dao.get_active_repositories()

        assert len(result) == 1
        assert result[0] == sample_repo

    @pytest.mark.asyncio
    async def test_enable_repository(self, dao, mock_session, sample_repo):
        """Test enabling a repository."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        await dao.enable_repository(sample_repo.id)

        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_repository(self, dao, mock_session, sample_repo):
        """Test disabling a repository."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        await dao.disable_repository(sample_repo.id)

        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_config_cache(self, dao, mock_session, sample_repo):
        """Test updating config cache."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        config = {"key": "value"}
        await dao.update_config_cache(sample_repo.id, config)

        mock_session.execute.assert_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_count(self, dao, mock_session, sample_repo):
        """Test counting repositories."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_repo]
        mock_session.execute.return_value = mock_result

        result = await dao.count()

        assert result == 1
