from __future__ import annotations

import os
import importlib.util
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LocalLLMClient:
    def __init__(
        self,
        model_name: str | None = None,
        device: str = "auto",
        context_window: int | None = None,
    ) -> None:
        resolved_model = model_name or os.getenv("LOCAL_MODEL_NAME", "gpt2")
        local_files_only = False
        gguf_path = None
        if context_window is None:
            context_window = int(os.getenv("LOCAL_GGUF_CONTEXT_WINDOW", "2048"))
        context_window = max(2048, context_window)
        if resolved_model:
            candidate_path = Path(resolved_model)
            if candidate_path.exists():
                resolved_model = str(candidate_path.resolve())
                local_files_only = True
                if candidate_path.suffix.lower() == ".gguf":
                    gguf_path = resolved_model
        self.model_name = resolved_model
        self._llama = None
        if gguf_path:
            if not importlib.util.find_spec("llama_cpp"):
                raise RuntimeError(
                    "GGUF models require the llama-cpp-python package. "
                    "Install it or choose a Hugging Face model directory."
                )
            from llama_cpp import Llama

            try:
                self._llama = Llama(model_path=gguf_path, n_ctx=context_window)
            except ValueError as exc:
                message = (
                    f"Failed to load GGUF model at {gguf_path}. "
                    "This usually means llama-cpp-python is too old for the model's architecture. "
                    "Upgrade llama-cpp-python or use a GGUF built for your installed llama.cpp version. "
                    f"Original error: {exc}"
                )
                raise RuntimeError(message) from exc
            self.tokenizer = None
            self.model = None
            self.generator = None
        else:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            self.tokenizer = AutoTokenizer.from_pretrained(
                resolved_model,
                local_files_only=local_files_only,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                resolved_model,
                local_files_only=local_files_only,
            )
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=device,
            )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 120,
        temperature: float = 0.8,
    ) -> LLMResponse:
        if self._llama:
            result = self._llama(
                prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
            )
            text = result["choices"][0]["text"]
            token_count = len(text.split())
        else:
            outputs: List[dict] = self.generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
            )
            text = outputs[0]["generated_text"]
            token_count = len(self.tokenizer.encode(text))
        return LLMResponse(text=text, tokens=token_count)
