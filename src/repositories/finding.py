"""FindingDAO für Finding-Datenbankoperationen.

Dieses Modul enthält den Data Access Object für Finding-Modelle
mit spezialisierten Methoden für die Finding-Verwaltung.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.finding import Finding
from src.repositories.base import BaseDAO


class Severity:
    """Konstanten für Finding-Schweregrade."""
    BLOCKER = "blocker"
    WARNING = "warning"
    INFO = "info"


class FindingDAO(BaseDAO):
    """Data Access Object für Finding-Modelle.

    Stellt spezialisierte Methoden für Finding-Datenbankoperationen bereit.

    Methods:
        get_by_review_id: Holt alle Findings eines Reviews.
        get_by_severity: Holt Findings nach Schweregrad.
        create_findings: Erstellt mehrere Findings gleichzeitig.
        mark_posted: Markiert ein Finding als veröffentlicht.
    """

    model = Finding

    async def get_by_review_id(self, review_id: UUID) -> list[Finding]:
        """Holt alle Findings eines Reviews.

        Ergebnisse werden nach Schweregrad (absteigend) und Zeilennummer sortiert.

        Args:
            review_id: Die ID des zugehörigen Reviews.

        Returns:
            Liste aller Findings des Reviews.
        """
        result = await self.session.execute(
            select(Finding)
            .where(Finding.review_id == review_id)
            .order_by(
                Finding.severity.desc(),
                Finding.line_number
            )
        )
        return list(result.scalars().all())

    async def get_by_severity(self, review_id: UUID, severity: str) -> list[Finding]:
        """Holt Findings eines Reviews nach Schweregrad.

        Args:
            review_id: Die ID des zugehörigen Reviews.
            severity: Der gewünschte Schweregrad.

        Returns:
            Liste der gefilterten Findings.
        """
        result = await self.session.execute(
            select(Finding)
            .where(Finding.review_id == review_id, Finding.severity == severity)
            .order_by(Finding.line_number)
        )
        return list(result.scalars().all())

    async def create_findings(self, review_id: UUID, findings_list: list[dict]) -> list[Finding]:
        """Erstellt mehrere Findings gleichzeitig.

        Args:
            review_id: Die ID des zugehörigen Reviews.
            findings_list: Liste von Dictionaries mit Finding-Daten.

        Returns:
            Liste der erstellten Findings.
        """
        findings = [
            Finding(review_id=review_id, **finding)
            for finding in findings_list
        ]
        self.session.add_all(findings)
        await self.session.flush()
        for finding in findings:
            await self.session.refresh(finding)
        return findings

    async def mark_posted(self, finding_id: UUID, comment_id: str) -> Finding | None:
        """Markiert ein Finding als auf der Plattform veröffentlicht.

        Args:
            finding_id: Die ID des Findings.
            comment_id: Die ID des Kommentars auf der Plattform.

        Returns:
            Das aktualisierte Finding oder None.
        """
        from datetime import datetime
        return await self.update(
            finding_id,
            platform_comment_id=comment_id,
            posted_at=datetime.utcnow()
        )
