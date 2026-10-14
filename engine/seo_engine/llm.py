from __future__ import annotations

import json
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeLLMClient:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.response = response or {
            "title": "Reduce Owner Dependency | RunRate Advisory",
            "description": (
                "Learn how RunRate Advisory helps owner-led businesses identify recurring "
                "dependencies and improve decision-making."
            ),
        }

    async def generate_structured(
        self, system: str, input: dict[str, Any], response_model: type[T]
    ) -> T:
        return response_model.model_validate(self.response)


class OpenAIModelClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_structured(
        self, system: str, input: dict[str, Any], response_model: type[T]
    ) -> T:
        response = await self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system + " Return a JSON object only."},
                {"role": "user", "content": json.dumps(input, ensure_ascii=False)},
            ],
        )
        return response_model.model_validate_json(response.choices[0].message.content or "{}")
