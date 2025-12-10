# local_llm.py
# Native LLM inference without external servers
# Supports: llama-cpp-python (GGUF) and transformers (safetensors)

import os
from typing import List, Dict, Optional
from pathlib import Path

# Try to import llama-cpp-python (preferred for GGUF models)
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# Try to import transformers (fallback for safetensors)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class LocalLLM:
    """
    Native LLM inference class supporting multiple backends.

    Supported backends:
    - llama_cpp: For GGUF quantized models (recommended, lower memory)
    - transformers: For safetensors/pytorch models (requires more VRAM)

    Usage:
        # For GGUF models
        llm = LocalLLM(model_path="./models/qwen3-4b-rpg.gguf", backend="llama_cpp")

        # For HuggingFace models
        llm = LocalLLM(model_path="Chun121/Qwen3-4B-RPG-Roleplay-V2", backend="transformers")

        response = llm.chat(messages, temperature=0.85, max_tokens=800)
    """

    def __init__(
        self,
        model_path: str,
        backend: str = "auto",
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,  # -1 = use all GPU layers if available
        verbose: bool = False
    ):
        """
        Initialize the local LLM.

        Args:
            model_path: Path to GGUF file or HuggingFace model ID
            backend: "llama_cpp", "transformers", or "auto" (detect from file)
            n_ctx: Context window size (default 8192)
            n_gpu_layers: Number of layers to offload to GPU (-1 = all)
            verbose: Print loading progress
        """
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.verbose = verbose

        # Auto-detect backend
        if backend == "auto":
            if model_path.endswith(".gguf"):
                backend = "llama_cpp"
            elif "/" in model_path or Path(model_path).is_dir():
                backend = "transformers"
            else:
                backend = "llama_cpp"  # Default to llama_cpp

        self.backend = backend
        self.model = None
        self.tokenizer = None

        self._load_model(n_gpu_layers)

    def _load_model(self, n_gpu_layers: int):
        """Load the model based on backend."""

        if self.backend == "llama_cpp":
            if not LLAMA_CPP_AVAILABLE:
                raise ImportError(
                    "llama-cpp-python is not installed. Install with:\n"
                    "  pip install llama-cpp-python\n"
                    "For GPU support:\n"
                    "  CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python"
                )

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Model file not found: {self.model_path}\n"
                    "Download a GGUF model first. See download_model.py"
                )

            if self.verbose:
                print(f"Loading GGUF model: {self.model_path}")

            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=self.verbose,
                chat_format="chatml"  # Qwen uses ChatML format
            )

            if self.verbose:
                print("Model loaded successfully!")

        elif self.backend == "transformers":
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "transformers/torch not installed. Install with:\n"
                    "  pip install transformers torch accelerate"
                )

            if self.verbose:
                print(f"Loading HuggingFace model: {self.model_path}")

            # Determine device
            if torch.cuda.is_available():
                device_map = "auto"
                torch_dtype = torch.float16
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device_map = "mps"
                torch_dtype = torch.float16
            else:
                device_map = "cpu"
                torch_dtype = torch.float32

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch_dtype,
                device_map=device_map,
                trust_remote_code=True
            )

            if self.verbose:
                print(f"Model loaded on: {device_map}")
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.85,
        max_tokens: int = 800,
        top_p: float = 0.9,
        repeat_penalty: float = 1.1
    ) -> str:
        """
        Generate a response from the model.

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            repeat_penalty: Penalty for repeating tokens

        Returns:
            Generated text response
        """

        if self.backend == "llama_cpp":
            return self._chat_llama_cpp(messages, temperature, max_tokens, top_p, repeat_penalty)
        elif self.backend == "transformers":
            return self._chat_transformers(messages, temperature, max_tokens, top_p, repeat_penalty)

    def _chat_llama_cpp(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_p: float,
        repeat_penalty: float
    ) -> str:
        """Generate using llama-cpp-python."""

        response = self.model.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            repeat_penalty=repeat_penalty
        )

        return response["choices"][0]["message"]["content"]

    def _chat_transformers(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_p: float,
        repeat_penalty: float
    ) -> str:
        """Generate using transformers."""

        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repeat_penalty,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode only the new tokens
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()

    def unload(self):
        """Unload the model to free memory."""
        if self.backend == "transformers" and self.model is not None:
            del self.model
            del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        elif self.backend == "llama_cpp" and self.model is not None:
            del self.model

        self.model = None
        self.tokenizer = None


def get_available_backends() -> List[str]:
    """Return list of available backends."""
    backends = []
    if LLAMA_CPP_AVAILABLE:
        backends.append("llama_cpp")
    if TRANSFORMERS_AVAILABLE:
        backends.append("transformers")
    return backends


def check_dependencies():
    """Print status of LLM dependencies."""
    print("=" * 50)
    print("Local LLM Dependency Check")
    print("=" * 50)

    print(f"\nllama-cpp-python: {'INSTALLED' if LLAMA_CPP_AVAILABLE else 'NOT INSTALLED'}")
    if not LLAMA_CPP_AVAILABLE:
        print("  Install with: pip install llama-cpp-python")
        print("  For GPU:      CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python")

    print(f"\ntransformers:    {'INSTALLED' if TRANSFORMERS_AVAILABLE else 'NOT INSTALLED'}")
    if not TRANSFORMERS_AVAILABLE:
        print("  Install with: pip install transformers torch accelerate")

    if TRANSFORMERS_AVAILABLE:
        import torch
        print(f"\nPyTorch device:")
        if torch.cuda.is_available():
            print(f"  CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("  Apple Silicon MPS available")
        else:
            print("  CPU only (slower inference)")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    check_dependencies()
