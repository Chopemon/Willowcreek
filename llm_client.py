from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LocalLLMClient:
    def __init__(self, model_name: str | None = None, device: str = "auto") -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        resolved_model = model_name or os.getenv("LOCAL_MODEL_NAME", "gpt2")
        local_files_only = False
        if resolved_model:
            candidate_path = Path(resolved_model)
            if candidate_path.exists():
                if candidate_path.suffix.lower() == ".gguf":
                    raise RuntimeError(
                        "GGUF models are not supported by transformers. "
                        "Use a local Llama.cpp server or a Hugging Face model path."
                    )
                resolved_model = str(candidate_path.resolve())
                local_files_only = True
        self.model_name = resolved_model
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
        outputs: List[dict] = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
        )
        text = outputs[0]["generated_text"]
        token_count = len(self.tokenizer.encode(text))
        return LLMResponse(text=text, tokens=token_count)
