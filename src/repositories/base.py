"""Basis-DAO-Klasse für Datenbankoperationen.

Dieses Modumenthält die Basisklasse für alle Data Access Objects
mit grundlegenden CRUD-Operationen.
"""

from typing import Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import Base


class BaseDAO:
    """Basisklasse für alle Data Access Objects.

    Stellt grundlegende CRUD-Operationen für alle Modelle bereit.

    Attributes:
        model: Das SQLAlchemy-Modell, für das dieser DAO zuständig ist.
        session: Die aktuelle Async-Datenbanksession.

    Methods:
        get_by_id: Holt einen Datensatz anhand der ID.
        get_all: Holt alle Datensätze mit optionalem Limit und Offset.
        create: Erstellt einen neuen Datensatz.
        update: Aktualisiert einen bestehenden Datensatz.
        delete: Löscht einen Datensatz.
        count: Gibt die Anzahl aller Datensätze zurück.
    """

    model: type[Base] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: Any) -> Base | None:
        """Holt einen Datensatz anhand der ID.

        Args:
            id: Die ID des zu holenden Datensatzes.

        Returns:
            Der gefundene Datensatz oder None, wenn nicht gefunden.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Base]:
        """Holt alle Datensätze mit optionaler Pagination.

        Args:
            limit: Maximale Anzahl der zurückgegebenen Datensätze.
            offset: Anzahl der zu überspringenden Datensätze.

        Returns:
            Liste aller gefundenen Datensätze.
        """
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Base:
        """Erstellt einen neuen Datensatz.

        Args:
            **kwargs: Schlüsselwortargumente für die Modell-Attribute.

        Returns:
            Der erstellte Datensatz.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: Any, **kwargs) -> Base | None:
        """Aktualisiert einen bestehenden Datensatz.

        Args:
            id: Die ID des zu aktualisierenden Datensatzes.
            **kwargs: Schlüsselwortargumente für die zu aktualisierenden Attribute.

        Returns:
            Der aktualisierte Datensatz oder None, wenn nicht gefunden.
        """
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: Any) -> bool:
        """Löscht einen Datensatz.

        Args:
            id: Die ID des zu löschenden Datensatzes.

        Returns:
            True, wenn der Datensatz gelöscht wurde, False otherwise.
        """
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def count(self) -> int:
        """Gibt die Anzahl aller Datensätze zurück.

        Returns:
            Die Gesamtzahl der Datensätze.
        """
        result = await self.session.execute(select(self.model))
        return len(result.scalars().all())
