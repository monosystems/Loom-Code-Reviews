"""RepositoryDAO für Repository-Datenbankoperationen.

Dieses Modul enthält den Data Access Object für Repository-Modelle
mit spezialisierten Repository-spezifischen Methoden.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.repository import Repository
from src.repositories.base import BaseDAO


class RepositoryDAO(BaseDAO):
    """Data Access Object für Repository-Modelle.

    Stellt spezialisierte Methoden für Repository-Datenbankoperationen bereit.

    Methods:
        get_by_platform_and_id: Holt ein Repository nach Plattform und Plattform-ID.
        get_by_full_name: Holt ein Repository nach vollständigem Namen.
        get_active_repositories: Holt alle aktiven Repositories.
        enable_repository: Aktiviert ein Repository.
        disable_repository: Deaktiviert ein Repository.
        update_config_cache: Aktualisiert den Konfigurations-Cache.
    """

    model = Repository

    async def get_by_platform_and_id(self, platform: str, platform_id: str) -> Optional[Repository]:
        """Holt ein Repository anhand der Plattform und Plattform-ID.

        Args:
            platform: Die Plattform (z.B. 'github', 'gitlab').
            platform_id: Die externe ID auf der Plattform.

        Returns:
            Das gefundene Repository oder None.
        """
        result = await self.session.execute(
            select(Repository).where(
                Repository.platform == platform,
                Repository.platform_id == platform_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_full_name(self, full_name: str) -> Optional[Repository]:
        """Holt ein Repository anhand des vollständigen Namens.

        Args:
            full_name: Der vollständige Name (org/repo).

        Returns:
            Das gefundene Repository oder None.
        """
        result = await self.session.execute(
            select(Repository).where(Repository.full_name == full_name)
        )
        return result.scalar_one_or_none()

    async def get_active_repositories(self) -> list[Repository]:
        """Holt alle aktiven Repositories.

        Returns:
            Liste aller aktiven Repositories.
        """
        result = await self.session.execute(
            select(Repository).where(Repository.is_active == True)
        )
        return list(result.scalars().all())

    async def enable_repository(self, repo_id: UUID) -> Repository | None:
        """Aktiviert ein Repository.

        Args:
            repo_id: Die ID des zu aktivierenden Repositories.

        Returns:
            Das aktualisierte Repository oder None.
        """
        return await self.update(repo_id, is_active=True)

    async def disable_repository(self, repo_id: UUID) -> Repository | None:
        """Deaktiviert ein Repository.

        Args:
            repo_id: Die ID des zu deaktivierenden Repositories.

        Returns:
            Das aktualisierte Repository oder None.
        """
        return await self.update(repo_id, is_active=False)

    async def update_config_cache(self, repo_id: UUID, config: dict) -> Repository | None:
        """Aktualisiert den Konfigurations-Cache eines Repositories.

        Args:
            repo_id: Die ID des Repositories.
            config: Die neue Konfiguration als Dictionary.

        Returns:
            Das aktualisierte Repository oder None.
        """
        from datetime import datetime
        return await self.update(
            repo_id,
            config_cache=config,
            config_cache_updated_at=datetime.utcnow()
        )
