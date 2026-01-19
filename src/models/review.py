"""Review Modell für die Datenbank.

Dieses Modell definiert ORM-Modelle für Code-Reviews, die die
Ergebnisse von automatischen Code-Analysen speichern.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class Review(Base, UUIDMixin, TimestampMixin):
    """Modell für einen Code-Review.

    Speichert die Ergebnisse eines automatischen Code-Reviews
    einschließlich aller gefundenen Probleme.

    Attributes:
        job_id: ID des zugehörigen Jobs.
        pr_number: Nummer des Pull-Requests.
        pr_title: Titel des Pull-Requests.
        pr_author: Autor des Pull-Requests.
        summary: Zusammenfassung des Reviews.
        total_findings: Gesamtzahl der gefundenen Probleme.
        blocker_count: Anzahl kritischer Blocker-Probleme.
        warning_count: Anzahl der Warnungen.
        info_count: Anzahl informativer Hinweise.
        llm_provider: Verwendeter LLM-Provider.
        llm_model: Verwendetes LLM-Modell.
        llm_tokens_used: Anzahl verbrauchter LLM-Tokens.
        duration_ms: Dauer des Reviews in Millisekunden.

    Relationships:
        job: Zugehöriger Job (1:1 Beziehung).
        findings: Zugehörige Findings (1:n Beziehung).
    """

    __tablename__ = "reviews"

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    pr_number = Column(Integer, nullable=False)
    pr_title = Column(Text, nullable=False)
    pr_author = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    total_findings = Column(Integer, default=0, nullable=False)
    blocker_count = Column(Integer, default=0, nullable=False)
    warning_count = Column(Integer, default=0, nullable=False)
    info_count = Column(Integer, default=0, nullable=False)
    llm_provider = Column(String(100), nullable=True)
    llm_model = Column(String(100), nullable=True)
    llm_tokens_used = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    job = relationship("Job", back_populates="review")
    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )
