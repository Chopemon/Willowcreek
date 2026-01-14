from __future__ import annotations

import os
from urllib.parse import urlsplit, urlunsplit
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
        manage_url: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.model_name = model_name or os.getenv("LM_STUDIO_MODEL", "local-model")
        self.api_url = api_url or os.getenv(
            "LM_STUDIO_API_URL",
            os.getenv("LOCAL_API_URL", "http://localhost:1234/v1/chat/completions"),
        )
        self.manage_url = manage_url or os.getenv("LM_STUDIO_MANAGE_URL", self._derive_manage_url(self.api_url))
        self.timeout = timeout

    @staticmethod
    def _derive_manage_url(api_url: str) -> str:
        parts = urlsplit(api_url)
        cleaned_path = parts.path.rsplit("/v1/chat/completions", 1)[0]
        if cleaned_path.endswith("/v1/chat/completions"):
            cleaned_path = cleaned_path.replace("/v1/chat/completions", "")
        return urlunsplit((parts.scheme, parts.netloc, cleaned_path, "", ""))

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

    def unload_model(self, model_name: str) -> bool:
        endpoint = os.getenv("LM_STUDIO_UNLOAD_ENDPOINT", "/v1/models/unload")
        url = f"{self.manage_url.rstrip('/')}{endpoint}"
        response = requests.post(url, json={"model": model_name}, timeout=self.timeout)
        if response.status_code >= 400:
            raise requests.HTTPError(f"Unload failed: {response.status_code} {response.text}", response=response)
        return True

    def load_model(self, model_name: str) -> bool:
        endpoint = os.getenv("LM_STUDIO_LOAD_ENDPOINT", "/v1/models/load")
        url = f"{self.manage_url.rstrip('/')}{endpoint}"
        response = requests.post(url, json={"model": model_name}, timeout=self.timeout)
        if response.status_code >= 400:
            raise requests.HTTPError(f"Load failed: {response.status_code} {response.text}", response=response)
        return True
