"""ReviewDAO für Review-Datenbankoperationen.

Dieses Modul enthält den Data Access Object für Review-Modelle
mit spezialisierten Methoden für die Review-Verwaltung.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.review import Review
from src.repositories.base import BaseDAO


class ReviewDAO(BaseDAO):
    """Data Access Object für Review-Modelle.

    Stellt spezialisierte Methoden für Review-Datenbankoperationen bereit.

    Methods:
        get_by_job_id: Holt ein Review anhand der Job-ID.
        get_recent_reviews: Holt die neuesten Reviews.
        get_reviews_by_repo: Holt alle Reviews eines Repositories.
        create_review: Erstellt ein neues Review.
    """

    model = Review

    async def get_by_job_id(self, job_id: UUID) -> Optional[Review]:
        """Holt ein Review anhand der Job-ID.

        Args:
            job_id: Die ID des zugehörigen Jobs.

        Returns:
            Das gefundene Review oder None.
        """
        result = await self.session.execute(
            select(Review).where(Review.job_id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_recent_reviews(self, limit: int = 100) -> list[Review]:
        """Holt die neuesten Reviews.

        Args:
            limit: Maximale Anzahl der zurückgegebenen Reviews.

        Returns:
            Liste der neuesten Reviews.
        """
        result = await self.session.execute(
            select(Review).order_by(Review.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_reviews_by_repo(self, repo_id: UUID, limit: int = 50) -> list[Review]:
        """Holt alle Reviews eines Repositories.

        Args:
            repo_id: Die ID des Repositories.
            limit: Maximale Anzahl der zurückgegebenen Reviews.

        Returns:
            Liste der Reviews des Repositories.
        """
        from src.models.job import Job
        result = await self.session.execute(
            select(Review)
            .join(Job, Review.job_id == Job.id)
            .where(Job.repo_id == repo_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_review(self, job_id: UUID, pr_number: int, pr_title: str, pr_author: str, **kwargs) -> Review:
        """Erstellt ein neues Review.

        Args:
            job_id: Die ID des zugehörigen Jobs.
            pr_number: Die Nummer des Pull-Requests.
            pr_title: Der Titel des Pull-Requests.
            pr_author: Der Autor des Pull-Requests.
            **kwargs: Zusätzliche Review-Attribute.

        Returns:
            Das erstellte Review.
        """
        return await self.create(
            job_id=job_id,
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author=pr_author,
            **kwargs
        )
