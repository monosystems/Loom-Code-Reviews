"""Unit tests for the Finding model."""
from datetime import datetime
from uuid import uuid4

import pytest

from src.models.finding import Finding


class TestFindingModel:
    """Test cases for the Finding model."""

    def test_finding_table_name(self):
        """Test that the table name is correctly set."""
        assert Finding.__tablename__ == "findings"

    def test_finding_has_uuid_id(self):
        """Test that Finding has a UUID id column."""
        assert hasattr(Finding, 'id')

    def test_finding_has_created_at(self):
        """Test that Finding has created_at timestamp."""
        assert hasattr(Finding, 'created_at')

    def test_finding_has_updated_at(self):
        """Test that Finding has updated_at timestamp."""
        assert hasattr(Finding, 'updated_at')

    def test_finding_review_id_column(self):
        """Test that Finding has review_id column."""
        assert hasattr(Finding, 'review_id')

    def test_finding_pipeline_name_column(self):
        """Test that Finding has pipeline_name column."""
        assert hasattr(Finding, 'pipeline_name')

    def test_finding_file_path_column(self):
        """Test that Finding has file_path column."""
        assert hasattr(Finding, 'file_path')

    def test_finding_line_number_column(self):
        """Test that Finding has line_number column."""
        assert hasattr(Finding, 'line_number')

    def test_finding_severity_column(self):
        """Test that Finding has severity column."""
        assert hasattr(Finding, 'severity')

    def test_finding_category_column(self):
        """Test that Finding has category column."""
        assert hasattr(Finding, 'category')

    def test_finding_message_column(self):
        """Test that Finding has message column."""
        assert hasattr(Finding, 'message')

    def test_finding_suggestion_column(self):
        """Test that Finding has suggestion column."""
        assert hasattr(Finding, 'suggestion')

    def test_finding_platform_comment_id_column(self):
        """Test that Finding has platform_comment_id column."""
        assert hasattr(Finding, 'platform_comment_id')

    def test_finding_posted_at_column(self):
        """Test that Finding has posted_at column."""
        assert hasattr(Finding, 'posted_at')

    def test_finding_review_relationship(self):
        """Test that Finding has review relationship."""
        assert hasattr(Finding, 'review')

    def test_finding_instantiation(self):
        """Test that Finding can be instantiated."""
        finding_id = uuid4()
        review_id = uuid4()
        finding = Finding(
            id=finding_id,
            review_id=review_id,
            pipeline_name="security",
            severity="blocker",
            message="Security vulnerability found"
        )
        assert finding.id == finding_id
        assert finding.review_id == review_id
        assert finding.pipeline_name == "security"
        assert finding.severity == "blocker"
        assert finding.message == "Security vulnerability found"

    def test_finding_default_values(self):
        """Test that default values are set correctly."""
        finding = Finding(
            review_id=uuid4(),
            pipeline_name="security",
            severity="blocker",
            message="Security vulnerability found"
        )
        assert finding.file_path is None
        assert finding.line_number is None
        assert finding.category is None
        assert finding.suggestion is None
        assert finding.platform_comment_id is None
        assert finding.posted_at is None
