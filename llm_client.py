import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class CallBudget:
    max_llm_calls_per_tick: int
    cooldown_sec: float
    calls_this_tick: int = 0
    last_call_ts: Optional[float] = None

    def reset_tick(self) -> None:
        self.calls_this_tick = 0

    def can_call(self, now: Optional[float] = None) -> bool:
        current_time = time.time() if now is None else now
        if self.calls_this_tick >= self.max_llm_calls_per_tick:
            return False
        if self.last_call_ts is None:
            return True
        return (current_time - self.last_call_ts) >= self.cooldown_sec

    def record_call(self, now: Optional[float] = None) -> None:
        current_time = time.time() if now is None else now
        self.calls_this_tick += 1
        self.last_call_ts = current_time


class LLMClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_sec: float = 30.0,
    ) -> None:
        env_base_url = os.getenv("LOCAL_LLM_URL")
        self.base_url = base_url or env_base_url or "http://localhost:1234/v1"
        self.model = model or os.getenv("LOCAL_LLM_MODEL", "local-model")
        self.timeout_sec = timeout_sec

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        response = requests.post(url, json=payload, timeout=self.timeout_sec)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        content = self.generate(prompt)
        cleaned = self._clean_json_text(content)
        return self._parse_json(cleaned)

    def _clean_json_text(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()
        return stripped

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
        return {}
