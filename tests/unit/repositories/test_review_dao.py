"""Unit tests for ReviewDAO."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestReviewDAO:
    """Test cases for ReviewDAO."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def dao(self, mock_session):
        """Create a ReviewDAO instance with mock session."""
        from src.repositories.review import ReviewDAO
        return ReviewDAO(mock_session)

    @pytest.fixture
    def sample_review(self):
        """Create a sample Review object."""
        from src.models.review import Review
        review = Review(
            id=uuid4(),
            job_id=uuid4(),
            pr_number=1,
            pr_title="Test PR",
            pr_author="testuser"
        )
        return review

    @pytest.mark.asyncio
    async def test_get_by_id(self, dao, mock_session, sample_review):
        """Test getting a review by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_review
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_id(sample_review.id)

        assert result == sample_review

    @pytest.mark.asyncio
    async def test_get_all(self, dao, mock_session, sample_review):
        """Test getting all reviews."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_review]
        mock_session.execute.return_value = mock_result

        result = await dao.get_all()

        assert len(result) == 1
        assert result[0] == sample_review

    @pytest.mark.asyncio
    async def test_create(self, dao, mock_session):
        """Test creating a review."""
        from src.models.review import Review
        
        mock_instance = MagicMock()
        mock_instance.id = uuid4()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.execute.return_value = MagicMock()

        job_id = uuid4()
        result = await dao.create_review(
            job_id=job_id,
            pr_number=2,
            pr_title="New PR",
            pr_author="newuser"
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update(self, dao, mock_session, sample_review):
        """Test updating a review."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_result.scalar_one_or_none.return_value = sample_review
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        await dao.update(sample_review.id, summary="New summary")

        mock_session.execute.assert_called()  # Called twice: update + get_by_id
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, dao, mock_session, sample_review):
        """Test deleting a review."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        result = await dao.delete(sample_review.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_by_job_id(self, dao, mock_session, sample_review):
        """Test getting a review by job ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_review
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_job_id(sample_review.job_id)

        assert result == sample_review
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_job_id_not_found(self, dao, mock_session):
        """Test getting a review by job ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_job_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_recent_reviews(self, dao, mock_session, sample_review):
        """Test getting recent reviews."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_review]
        mock_session.execute.return_value = mock_result

        result = await dao.get_recent_reviews(limit=10)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_reviews_by_repo(self, dao, mock_session, sample_review):
        """Test getting reviews by repository."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_review]
        mock_session.execute.return_value = mock_result

        repo_id = uuid4()
        result = await dao.get_reviews_by_repo(repo_id)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_count(self, dao, mock_session, sample_review):
        """Test counting reviews."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_review]
        mock_session.execute.return_value = mock_result

        result = await dao.count()

        assert result == 1
