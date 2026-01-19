"""Unit tests for FindingDAO."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.finding import Finding
from src.repositories.finding import FindingDAO, Severity


class TestFindingDAO:
    """Test cases for FindingDAO."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock async session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def dao(self, mock_session):
        """Create a FindingDAO instance with mock session."""
        return FindingDAO(mock_session)

    @pytest.fixture
    def sample_finding(self):
        """Create a sample Finding object."""
        finding = Finding(
            id=uuid4(),
            review_id=uuid4(),
            pipeline_name="security",
            severity="blocker",
            message="Security vulnerability found"
        )
        return finding

    @pytest.mark.asyncio
    async def test_get_by_id(self, dao, mock_session, sample_finding):
        """Test getting a finding by ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_finding
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_id(sample_finding.id)

        assert result == sample_finding

    @pytest.mark.asyncio
    async def test_get_all(self, dao, mock_session, sample_finding):
        """Test getting all findings."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_finding]
        mock_session.execute.return_value = mock_result

        result = await dao.get_all()

        assert len(result) == 1
        assert result[0] == sample_finding

    @pytest.mark.asyncio
    async def test_create(self, dao, mock_session):
        """Test creating a finding."""
        mock_instance = MagicMock()
        mock_instance.id = uuid4()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.execute.return_value = MagicMock()

        review_id = uuid4()
        result = await dao.create(
            review_id=review_id,
            pipeline_name="code_quality",
            severity="warning",
            message="Code quality issue"
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update(self, dao, mock_session, sample_finding):
        """Test updating a finding."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_result.scalar_one_or_none.return_value = sample_finding
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        await dao.update(sample_finding.id, suggestion="Fix this issue")

        mock_session.execute.assert_called()  # Called twice: update + get_by_id
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self, dao, mock_session, sample_finding):
        """Test deleting a finding."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        result = await dao.delete(sample_finding.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_get_by_review_id(self, dao, mock_session, sample_finding):
        """Test getting findings by review ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_finding]
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_review_id(sample_finding.review_id)

        assert len(result) == 1
        assert result[0] == sample_finding

    @pytest.mark.asyncio
    async def test_get_by_severity(self, dao, mock_session, sample_finding):
        """Test getting findings by severity."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_finding]
        mock_session.execute.return_value = mock_result

        result = await dao.get_by_severity(sample_finding.review_id, "blocker")

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_create_findings(self, dao, mock_session):
        """Test creating multiple findings at once."""
        mock_session.add_all = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        review_id = uuid4()
        findings_list = [
            {
                "pipeline_name": "security",
                "severity": "blocker",
                "message": "Issue 1"
            },
            {
                "pipeline_name": "code_quality",
                "severity": "warning",
                "message": "Issue 2"
            }
        ]

        result = await dao.create_findings(review_id, findings_list)

        mock_session.add_all.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_posted(self, dao, mock_session, sample_finding):
        """Test marking a finding as posted."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_result.scalar_one_or_none.return_value = sample_finding
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()

        await dao.mark_posted(sample_finding.id, "comment_123")

        mock_session.execute.assert_called()  # Called twice: update + get_by_id
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_count(self, dao, mock_session, sample_finding):
        """Test counting findings."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_finding]
        mock_session.execute.return_value = mock_result

        result = await dao.count()

        assert result == 1


class TestSeverity:
    """Test cases for Severity constants."""

    def test_blocker_severity(self):
        """Test BLOCKER severity value."""
        assert Severity.BLOCKER == "blocker"

    def test_warning_severity(self):
        """Test WARNING severity value."""
        assert Severity.WARNING == "warning"

    def test_info_severity(self):
        """Test INFO severity value."""
        assert Severity.INFO == "info"
