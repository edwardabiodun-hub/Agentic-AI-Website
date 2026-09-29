from __future__ import annotations

from typing import Any, Protocol, TypeVar

from .models import CollectionResult, DateWindow, FileChange, SiteScope

T = TypeVar("T")


class DataConnector(Protocol):
    name: str

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult: ...


class TargetRepository(Protocol):
    def read_files(self, paths: list[str]) -> dict[str, str]: ...

    def write_files(self, changes: list[FileChange]) -> None: ...


class LLMClient(Protocol):
    async def generate_structured(
        self, system: str, input: dict[str, Any], response_model: type[T]
    ) -> T: ...
