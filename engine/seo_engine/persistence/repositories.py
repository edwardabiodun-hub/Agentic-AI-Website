from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seo_engine.domain.models import NormalizedObservation

from .db import ObservationRow, RunRow


class RunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def start(self, site_id: str, fingerprint: str) -> UUID:
        existing = await self.session.scalar(
            select(RunRow).where(RunRow.site_id == site_id, RunRow.fingerprint == fingerprint)
        )
        if existing:
            return UUID(existing.id)
        row = RunRow(site_id=site_id, fingerprint=fingerprint)
        self.session.add(row)
        await self.session.commit()
        return UUID(row.id)

    async def has_fingerprint(self, site_id: str, fingerprint: str) -> bool:
        return bool(
            await self.session.scalar(
                select(RunRow.id).where(
                    RunRow.site_id == site_id, RunRow.fingerprint == fingerprint
                )
            )
        )

    async def finish(self, run_id: UUID, status: str, errors: list[str]) -> None:
        row = await self.session.get(RunRow, str(run_id))
        if row is None:
            raise ValueError(f"unknown run: {run_id}")
        row.status = status
        row.errors = errors
        await self.session.commit()


class ObservationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def insert_many(self, run_id: UUID, observations: list[NormalizedObservation]) -> int:
        rows = [
            ObservationRow(
                run_id=str(run_id),
                source=observation.source,
                observed_at=observation.observed_at,
                dimensions=observation.dimensions,
                metrics=observation.metrics,
                evidence_ref=observation.evidence_ref,
            )
            for observation in observations
        ]
        self.session.add_all(rows)
        await self.session.commit()
        return len(rows)
