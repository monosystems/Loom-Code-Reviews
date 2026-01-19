"""Basis-Klassen für SQLAlchemy Models.

Dieses Modul enthält wiederverwendbare Mixins und die Basis-Klasse
für alle ORM-Modelle der Anwendung.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin für automatische Zeitstempel-Spalten.

    Fügt created_at und updated_at Spalten hinzu, die automatisch
    bei Erstellung bzw. Aktualisierung eines Datensatzes gesetzt werden.

    Attributes:
        created_at: Zeitstempel der Erstellung (wird automatisch gesetzt).
        updated_at: Zeitstempel der letzten Aktualisierung (wird automatisch aktualisiert).
    """

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin für UUID-basierte Primärschlüssel.

    Fügt eine automatisch generierte UUID-Spalte als Primärschlüssel hinzu.

    Attributes:
        id: UUID Primärschlüssel (wird automatisch generiert).
    """

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
