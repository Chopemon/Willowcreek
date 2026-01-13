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
        context_size: int | None = None,
    ) -> None:
        resolved_context = self._resolve_context_size(context_size)
        resolved_model = model_name or os.getenv("LOCAL_MODEL_NAME", "gpt2")
        local_files_only = False
        gguf_path = None
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

            self._llama = Llama(model_path=gguf_path, n_ctx=resolved_context)
            self.tokenizer = None
            self.model = None
            self.generator = None
        else:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

            resolved_device = self._resolve_device(device, torch)
            pipeline_device = self._resolve_pipeline_device(resolved_device)
            torch_dtype = (
                torch.float16
                if resolved_device in {"cuda", "mps"} or resolved_device.startswith("cuda:")
                else None
            )

            self.tokenizer = AutoTokenizer.from_pretrained(
                resolved_model,
                local_files_only=local_files_only,
            )
            self.tokenizer.model_max_length = resolved_context
            self.model = AutoModelForCausalLM.from_pretrained(
                resolved_model,
                local_files_only=local_files_only,
                torch_dtype=torch_dtype,
            )
            if resolved_device != "cpu":
                self.model.to(resolved_device)
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=pipeline_device,
            )

    @staticmethod
    def _resolve_context_size(context_size: int | None) -> int:
        if context_size:
            return max(int(context_size), 1)
        env_value = os.getenv("LLM_CONTEXT_SIZE")
        if not env_value:
            return 2048
        try:
            return max(int(env_value), 1)
        except ValueError:
            return 2048

    @staticmethod
    def _resolve_device(requested: str, torch_module) -> str:
        env_device = os.getenv("LLM_DEVICE")
        if env_device:
            return env_device
        if requested and requested != "auto":
            return requested
        if torch_module.cuda.is_available():
            return "cuda"
        if torch_module.backends.mps.is_available():
            return "mps"
        return "cpu"

    @staticmethod
    def _resolve_pipeline_device(device: str) -> int | str:
        if device.startswith("cuda"):
            if ":" in device:
                return int(device.split(":", 1)[1])
            return 0
        if device == "mps":
            return "mps"
        return -1

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
