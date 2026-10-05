from __future__ import annotations

import os
import platform
import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def runtime_executable() -> Path:
    root = app_root() / "runtime" / "llama"
    system = platform.system()
    if system == "Windows":
        return root / "windows" / "llama-server.exe"
    if system == "Darwin":
        return root / "macos" / "llama-server"
    return root / "linux" / "llama-server"


def default_model_path() -> Path:
    override = os.environ.get("LIRICO_AI_MODEL")
    if override:
        return Path(override)
    return app_root() / "models" / "lirico-default.gguf"
