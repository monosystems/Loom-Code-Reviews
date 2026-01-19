"""Repository Modell für die Datenbank.

Dieses Modul definiert das ORM-Modell für Repositories, die von der
Code-Review-Plattform überwacht werden.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Repository(Base, UUIDMixin, TimestampMixin):
    """Modell für ein zu überwachendes Repository.

    Speichert Informationen über Repositories, die für automatische
    Code-Reviews konfiguriert sind.

    Attributes:
        platform: Die Plattform des Repositories (z.B. 'github', 'gitlab').
        platform_id: Die externe ID des Repositories auf der Plattform.
        full_name: Der vollständige Name (org/repo) des Repositories.
        webhook_secret: Geheimer Schlüssel für Webhook-Authentifizierung.
        is_active: Gibt an, ob das Repository aktiv überwacht wird.
        config_cache: Gecachete Konfiguration des Repositories.
        config_cache_updated_at: Zeitstempel der letzten Konfigurationsaktualisierung.
        jobs: Zugehörige Jobs (1:n Beziehung).

    Relationships:
        jobs: Alle zu diesem Repository gehörenden Jobs.
    """

    __tablename__ = "repositories"

    platform = Column(String(50), nullable=False)
    platform_id = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, unique=True)
    webhook_secret = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    config_cache = Column(JSONB, nullable=True)
    config_cache_updated_at = Column(DateTime, nullable=True)

    jobs = relationship("Job", back_populates="repository", cascade="all, delete-orphan")

    __table_args__ = (
        {"schema": None},
    )
