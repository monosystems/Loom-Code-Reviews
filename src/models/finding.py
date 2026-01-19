"""Finding Modell für die Datenbank.

Dieses Modell definiert ORM-Modelle für einzelne Findings, die
bei einem Code-Review gefunden wurden.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class Finding(Base, UUIDMixin, TimestampMixin):
    """Modell für ein gefundenes Problem (Finding).

    Repräsentiert ein einzelnes Problem, das bei der automatischen
    Code-Analyse gefunden wurde.

    Attributes:
        review_id: ID des zugehörigen Reviews.
        pipeline_name: Name der Pipeline, die das Finding generiert hat.
        file_path: Pfad zur betroffenen Datei.
        line_number: Zeilennummer des Problems.
        severity: Schweregrad des Problems (blocker, warning, info).
        category: Kategorie des Problems.
        message: Beschreibung des Problems.
        suggestion: Vorgeschlagene Lösung.
        platform_comment_id: ID des Kommentars auf der Plattform.
        posted_at: Zeitstempel der Veröffentlichung.

    Relationships:
        review: Zugehöriges Review.
    """

    __tablename__ = "findings"

    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    pipeline_name = Column(String(100), nullable=False)
    file_path = Column(Text, nullable=True)
    line_number = Column(Integer, nullable=True)
    severity = Column(String(20), nullable=False)
    category = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    platform_comment_id = Column(String(255), nullable=True)
    posted_at = Column(DateTime, nullable=True)

    review = relationship("Review", back_populates="findings")

    __table_args__ = (
        {"schema": None},
    )
