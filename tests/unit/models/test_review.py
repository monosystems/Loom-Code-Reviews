"""Unit tests for the Review model."""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import inspect

from src.models.review import Review


class TestReviewModel:
    """Test cases for the Review model."""

    def test_review_table_name(self):
        """Test that the table name is correctly set."""
        assert Review.__tablename__ == "reviews"

    def test_review_has_uuid_id(self):
        """Test that Review has a UUID id column."""
        assert hasattr(Review, 'id')
        inspector = inspect(Review)
        columns = {col['name']: col for col in inspector.get_columns('reviews')}
        assert 'id' in columns

    def test_review_has_created_at(self):
        """Test that Review has created_at timestamp."""
        assert hasattr(Review, 'created_at')

    def test_review_has_updated_at(self):
        """Test that Review has updated_at timestamp."""
        assert hasattr(Review, 'updated_at')

    def test_review_job_id_column(self):
        """Test that Review has job_id column."""
        assert hasattr(Review, 'job_id')
        inspector = inspect(Review)
        columns = {col['name']: col for col in inspector.get_columns('reviews')}
        assert 'job_id' in columns

    def test_review_pr_number_column(self):
        """Test that Review has pr_number column."""
        assert hasattr(Review, 'pr_number')

    def test_review_pr_title_column(self):
        """Test that Review has pr_title column."""
        assert hasattr(Review, 'pr_title')

    def test_review_pr_author_column(self):
        """Test that Review has pr_author column."""
        assert hasattr(Review, 'pr_author')

    def test_review_summary_column(self):
        """Test that Review has summary column."""
        assert hasattr(Review, 'summary')

    def test_review_total_findings_column(self):
        """Test that Review has total_findings column."""
        assert hasattr(Review, 'total_findings')

    def test_review_blocker_count_column(self):
        """Test that Review has blocker_count column."""
        assert hasattr(Review, 'blocker_count')

    def test_review_warning_count_column(self):
        """Test that Review has warning_count column."""
        assert hasattr(Review, 'warning_count')

    def test_review_info_count_column(self):
        """Test that Review has info_count column."""
        assert hasattr(Review, 'info_count')

    def test_review_llm_provider_column(self):
        """Test that Review has llm_provider column."""
        assert hasattr(Review, 'llm_provider')

    def test_review_llm_model_column(self):
        """Test that Review has llm_model column."""
        assert hasattr(Review, 'llm_model')

    def test_review_llm_tokens_used_column(self):
        """Test that Review has llm_tokens_used column."""
        assert hasattr(Review, 'llm_tokens_used')

    def test_review_duration_ms_column(self):
        """Test that Review has duration_ms column."""
        assert hasattr(Review, 'duration_ms')

    def test_review_job_relationship(self):
        """Test that Review has job relationship."""
        assert hasattr(Review, 'job')

    def test_review_findings_relationship(self):
        """Test that Review has findings relationship."""
        assert hasattr(Review, 'findings')

    def test_review_total_findings_default_value(self):
        """Test that total_findings has default 0 in column definition."""
        inspector = inspect(Review)
        columns = {col['name']: col for col in inspector.get_columns('reviews')}
        assert columns['total_findings'].default.arg == 0

    def test_review_counts_default_values(self):
        """Test that all count columns have default 0 in column definition."""
        inspector = inspect(Review)
        columns = {col['name']: col for col in inspector.get_columns('reviews')}
        assert columns['blocker_count'].default.arg == 0
        assert columns['warning_count'].default.arg == 0
        assert columns['info_count'].default.arg == 0

    def test_review_instantiation(self):
        """Test that Review can be instantiated."""
        review_id = uuid4()
        job_id = uuid4()
        review = Review(
            id=review_id,
            job_id=job_id,
            pr_number=1,
            pr_title="Test PR",
            pr_author="testuser"
        )
        assert review.id == review_id
        assert review.job_id == job_id
        assert review.pr_number == 1
        assert review.pr_title == "Test PR"
        assert review.pr_author == "testuser"

    def test_review_repr(self):
        """Test Review string representation."""
        review = Review(
            job_id=uuid4(),
            pr_number=1,
            pr_title="Test PR",
            pr_author="testuser"
        )
        repr_str = repr(review)
        assert "Review" in repr_str
