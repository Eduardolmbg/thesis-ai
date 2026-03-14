"""Configuracoes centrais do thesis-ai."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def save_env(**kwargs: str) -> None:
    """Persiste chave=valor no arquivo .env (cria se nao existir).

    Atualiza linhas existentes e adiciona novas ao final.
    """
    env_path = ROOT_DIR / ".env"

    # Le conteudo atual
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_keys: set[str] = set()

    for key, value in kwargs.items():
        found = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
                lines[i] = f"{key}={value}"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}")
        updated_keys.add(key)

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Atualiza os.environ para que o processo atual ja use os novos valores
    for key, value in kwargs.items():
        os.environ[key] = value

# ── Paths ────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── LLM Provider ─────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

# ── Gemini defaults ──────────────────────────────────────────────────────
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Groq defaults ───────────────────────────────────────────────────────
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── brapi.dev ────────────────────────────────────────────────────────────
BRAPI_TOKEN: str = os.getenv("BRAPI_TOKEN", "")

# ── Research ─────────────────────────────────────────────────────────────
SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "8"))
SEARCH_LANGUAGE: str = "pt-br"
SEARCH_REGION: str = "BR"

# ── App metadata ─────────────────────────────────────────────────────────
APP_NAME = "thesis-ai"
APP_TITLE = "thesis-ai"
APP_SUBTITLE = "AI-Powered Equity Research"
APP_VERSION = "0.1.0"
