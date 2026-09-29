from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeLLMClient:
    async def generate_structured(
        self, system: str, input: dict[str, Any], response_model: type[T]
    ) -> T:
        return response_model.model_validate(input["response"])
