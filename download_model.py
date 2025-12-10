#!/usr/bin/env python3
"""
Model Download Helper for Willow Creek
Downloads GGUF models from HuggingFace for local inference.

Usage:
    python download_model.py                    # Download default Qwen3-4B-RPG model
    python download_model.py --list             # List available models
    python download_model.py --model <name>     # Download specific model
    python download_model.py --url <hf_url>     # Download from custom URL
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download, list_repo_files
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False


# Default models directory
MODELS_DIR = Path(__file__).parent / "models"

# Pre-configured models optimized for roleplay/narrative
PRESET_MODELS = {
    "qwen3-4b-rpg": {
        "repo_id": "Chun121/qwen3-4B-rpg-roleplay",
        "filename": "gguf_q4_k_m/qwen3-4B-rpg-roleplay-q4_k_m.gguf",
        "description": "Qwen3 4B RPG Roleplay (Q4_K_M, ~2.5GB) - Great for narrative",
        "size_gb": 2.5
    },
    "qwen3-4b-rpg-v2": {
        "repo_id": "Chun121/Qwen3-4B-RPG-Roleplay-V2",
        "filename": None,  # Will search for GGUF
        "description": "Qwen3 4B RPG Roleplay V2 - Improved version",
        "size_gb": 2.5
    },
    "mistral-7b-instruct": {
        "repo_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "description": "Mistral 7B Instruct (Q4_K_M, ~4.4GB) - General purpose",
        "size_gb": 4.4
    },
    "llama3-8b-instruct": {
        "repo_id": "bartowski/Meta-Llama-3-8B-Instruct-GGUF",
        "filename": "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
        "description": "Llama 3 8B Instruct (Q4_K_M, ~4.9GB) - Meta's latest",
        "size_gb": 4.9
    }
}

DEFAULT_MODEL = "qwen3-4b-rpg"


def ensure_models_dir():
    """Create models directory if it doesn't exist."""
    MODELS_DIR.mkdir(exist_ok=True)

    # Create .gitignore in models dir to avoid committing large files
    gitignore = MODELS_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Ignore model files\n*.gguf\n*.bin\n*.safetensors\n")


def list_models():
    """List available preset models."""
    print("\n" + "=" * 60)
    print("Available Models for Willow Creek")
    print("=" * 60)

    for name, info in PRESET_MODELS.items():
        marker = " [DEFAULT]" if name == DEFAULT_MODEL else ""
        print(f"\n{name}{marker}")
        print(f"  {info['description']}")
        print(f"  Size: ~{info['size_gb']} GB")
        print(f"  Repo: {info['repo_id']}")

    print("\n" + "-" * 60)
    print("To download: python download_model.py --model <name>")
    print("=" * 60 + "\n")


def find_gguf_in_repo(repo_id: str) -> str:
    """Find a GGUF file in a HuggingFace repo."""
    try:
        files = list_repo_files(repo_id)
        gguf_files = [f for f in files if f.endswith('.gguf')]

        # Prefer Q4_K_M quantization
        for f in gguf_files:
            if 'q4_k_m' in f.lower() or 'Q4_K_M' in f:
                return f

        # Otherwise return first GGUF
        if gguf_files:
            return gguf_files[0]

        return None
    except Exception as e:
        print(f"Error listing repo files: {e}")
        return None


def download_model(
    repo_id: str,
    filename: str = None,
    output_name: str = None
) -> Path:
    """
    Download a model from HuggingFace.

    Args:
        repo_id: HuggingFace repo ID (e.g., "Chun121/qwen3-4B-rpg-roleplay")
        filename: Specific file to download (if None, searches for GGUF)
        output_name: Name for the output file

    Returns:
        Path to downloaded model
    """
    if not HF_HUB_AVAILABLE:
        print("ERROR: huggingface-hub not installed!")
        print("Install with: pip install huggingface-hub")
        sys.exit(1)

    ensure_models_dir()

    # Find GGUF file if not specified
    if filename is None:
        print(f"Searching for GGUF file in {repo_id}...")
        filename = find_gguf_in_repo(repo_id)
        if filename is None:
            print(f"ERROR: No GGUF file found in {repo_id}")
            print("This repo may only have safetensors format.")
            print("Use transformers backend instead, or find a GGUF version.")
            sys.exit(1)
        print(f"Found: {filename}")

    # Determine output path
    if output_name is None:
        output_name = filename.split("/")[-1]

    output_path = MODELS_DIR / output_name

    if output_path.exists():
        print(f"\nModel already exists: {output_path}")
        response = input("Re-download? (y/N): ").strip().lower()
        if response != 'y':
            return output_path

    print(f"\nDownloading: {repo_id}/{filename}")
    print(f"Destination: {output_path}")
    print("This may take a while depending on your connection...\n")

    try:
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=MODELS_DIR,
            local_dir_use_symlinks=False
        )

        # Move to final location if needed
        downloaded_path = Path(downloaded)
        if downloaded_path != output_path:
            if downloaded_path.exists():
                downloaded_path.rename(output_path)

        print(f"\nDownload complete: {output_path}")
        print(f"Size: {output_path.stat().st_size / 1e9:.2f} GB")

        return output_path

    except Exception as e:
        print(f"\nERROR downloading model: {e}")
        sys.exit(1)


def download_preset(name: str) -> Path:
    """Download a preset model by name."""
    if name not in PRESET_MODELS:
        print(f"Unknown model: {name}")
        print("Use --list to see available models")
        sys.exit(1)

    info = PRESET_MODELS[name]
    return download_model(
        repo_id=info["repo_id"],
        filename=info["filename"],
        output_name=f"{name}.gguf"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Download LLM models for Willow Creek"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available preset models"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Download a preset model by name"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="HuggingFace repo ID (e.g., 'TheBloke/Mistral-7B-GGUF')"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Specific file to download from repo"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output filename"
    )

    args = parser.parse_args()

    if args.list:
        list_models()
        return

    if args.repo:
        # Custom repo download
        download_model(
            repo_id=args.repo,
            filename=args.file,
            output_name=args.output
        )
    elif args.model:
        # Preset model download
        download_preset(args.model)
    else:
        # Default: download recommended model
        print(f"Downloading default model: {DEFAULT_MODEL}")
        download_preset(DEFAULT_MODEL)

    print("\n" + "=" * 60)
    print("Next steps:")
    print("=" * 60)
    print("1. Run the narrative chat with native mode:")
    print(f"   python narrative_chat.py --mode native --model models/{DEFAULT_MODEL}.gguf")
    print("\n2. Or check your setup:")
    print("   python local_llm.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
