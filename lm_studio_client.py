from __future__ import annotations

import os
from dataclasses import dataclass

import requests


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LMStudioClient:
    def __init__(
        self,
        model_name: str | None = None,
        api_url: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.model_name = model_name or os.getenv("LM_STUDIO_MODEL", "local-model")
        self.api_url = api_url or os.getenv(
            "LM_STUDIO_API_URL",
            os.getenv("LOCAL_API_URL", "http://localhost:1234/v1/chat/completions"),
        )
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 120,
        temperature: float = 0.8,
    ) -> LLMResponse:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_new_tokens,
        }
        response = requests.post(self.api_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        token_count = len(content.split())
        return LLMResponse(text=content, tokens=token_count)
