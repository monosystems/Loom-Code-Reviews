"""JobDAO für Job-Datenbankoperationen.

Dieses Modul enthält den Data Access Object für Job-Modelle
mit spezialisierten Methoden für die Job-Verwaltung.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.job import Job
from src.repositories.base import BaseDAO


class JobStatus:
    """Konstanten für Job-Status."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class JobDAO(BaseDAO):
    """Data Access Object für Job-Modelle.

    Stellt spezialisierte Methoden für Job-Datenbankoperationen bereit.

    Methods:
        get_pending_jobs: Holt ausstehende Jobs für die Verarbeitung.
        get_jobs_by_status: Holt alle Jobs mit einem bestimmten Status.
        create_job: Erstellt einen neuen Job.
        update_status: Aktualisiert den Status eines Jobs.
        mark_started: Markiert einen Job als gestartet.
        mark_completed: Markiert einen Job als abgeschlossen.
        mark_failed: Markiert einen Job als fehlgeschlagen.
        increment_retry: Inkrementiert den Retry-Count eines Jobs.
    """

    model = Job

    async def get_pending_jobs(self, limit: int = 10) -> list[Job]:
        """Holt ausstehende Jobs für die Verarbeitung.

        Jobs werden nach Priorität (absteigend) und Erstellungsdatum sortiert.

        Args:
            limit: Maximale Anzahl der zurückgegebenen Jobs.

        Returns:
            Liste der ausstehenden Jobs.
        """
        result = await self.session.execute(
            select(Job)
            .where(Job.status == JobStatus.QUEUED)
            .order_by(Job.priority.desc(), Job.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_jobs_by_status(self, status: str) -> list[Job]:
        """Holt alle Jobs mit einem bestimmten Status.

        Args:
            status: Der gewünschte Job-Status.

        Returns:
            Liste der gefundenen Jobs.
        """
        result = await self.session.execute(
            select(Job).where(Job.status == status).order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_job(self, repo_id: UUID, platform_pr_id: str, pr_number: int, head_sha: str, **kwargs) -> Job:
        """Erstellt einen neuen Job.

        Args:
            repo_id: ID des zugehörigen Repositories.
            platform_pr_id: Externe PR-ID auf der Plattform.
            pr_number: Nummer des Pull-Requests.
            head_sha: Git-Commit-Hash des PR-Heads.
            **kwargs: Zusätzliche Job-Attribute.

        Returns:
            Der erstellte Job.
        """
        return await self.create(
            repo_id=repo_id,
            platform_pr_id=platform_pr_id,
            pr_number=pr_number,
            head_sha=head_sha,
            **kwargs
        )

    async def update_status(self, job_id: UUID, status: str) -> Job | None:
        """Aktualisiert den Status eines Jobs.

        Args:
            job_id: Die ID des Jobs.
            status: Der neue Status.

        Returns:
            Der aktualisierte Job oder None.
        """
        return await self.update(job_id, status=status)

    async def mark_started(self, job_id: UUID) -> Job | None:
        """Markiert einen Job als gestartet.

        Setzt den Status auf 'in_progress' und speichert den Startzeitpunkt.

        Args:
            job_id: Die ID des Jobs.

        Returns:
            Der aktualisierte Job oder None.
        """
        from datetime import datetime
        return await self.update(job_id, status=JobStatus.IN_PROGRESS, started_at=datetime.utcnow())

    async def mark_completed(self, job_id: UUID) -> Job | None:
        """Markiert einen Job als erfolgreich abgeschlossen.

        Setzt den Status auf 'completed' und speichert den Abschlusszeitpunkt.

        Args:
            job_id: Die ID des Jobs.

        Returns:
            Der aktualisierte Job oder None.
        """
        from datetime import datetime
        return await self.update(
            job_id,
            status=JobStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )

    async def mark_failed(self, job_id: UUID, error_message: str) -> Job | None:
        """Markiert einen Job als fehlgeschlagen.

        Setzt den Status auf 'failed', speichert den Abschlusszeitpunkt
        und die Fehlermeldung.

        Args:
            job_id: Die ID des Jobs.
            error_message: Die Fehlermeldung.

        Returns:
            Der aktualisierte Job oder None.
        """
        from datetime import datetime
        return await self.update(
            job_id,
            status=JobStatus.FAILED,
            error_message=error_message,
            completed_at=datetime.utcnow()
        )

    async def increment_retry(self, job_id: UUID) -> Job | None:
        """Inkrementiert den Retry-Count eines Jobs.

        Args:
            job_id: Die ID des Jobs.

        Returns:
            Der aktualisierte Job oder None, wenn der Job nicht existiert.
        """
        job = await self.get_by_id(job_id)
        if job:
            return await self.update(job_id, retry_count=job.retry_count + 1)
        return None
