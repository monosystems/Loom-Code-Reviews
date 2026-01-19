"""Job Modell für die Datenbank.

Dieses Modell definiert ORM-Modelle für Code-Review-Jobs, die
einzelne Pull-Request-Reviews repräsentieren.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class Job(Base, UUIDMixin, TimestampMixin):
    """Modell für einen Code-Review-Job.

    Repräsentiert einen einzelnen Review-Auftrag für einen Pull-Request.

    Attributes:
        repo_id: ID des zugehörigen Repositories.
        platform_pr_id: Externe PR-ID auf der Plattform.
        pr_number: Nummer des Pull-Requests.
        head_sha: Git-Commit-Hash des PR-Heads.
        status: Aktueller Status des Jobs (queued, in_progress, completed, failed).
        priority: Priorität des Jobs (niedrigere Zahl = höhere Priorität).
        started_at: Zeitstempel des Job-Starts.
        completed_at: Zeitstempel der Job-Fertigstellung.
        error_message: Fehlermeldung bei fehlgeschlagenen Jobs.
        retry_count: Anzahl der bisherigen Wiederholungsversuche.
        job_metadata: Zusätzliche Metadaten als JSON.

    Relationships:
        repository: Zugehöriges Repository.
        review: Zugehörige Review (1:1 Beziehung).
    """

    __tablename__ = "jobs"

    repo_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    platform_pr_id = Column(String(255), nullable=False)
    pr_number = Column(Integer, nullable=False)
    head_sha = Column(String(64), nullable=False)
    status = Column(String(20), default="queued", nullable=False)
    priority = Column(Integer, default=5, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    job_metadata = Column(JSONB, nullable=True)

    repository = relationship("Repository", back_populates="jobs")
    review = relationship("Review", back_populates="job", uselist=False)

    __table_args__ = (
        {"schema": None},
    )
