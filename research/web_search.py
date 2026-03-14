"""Módulo de busca web — abstrai a fonte de pesquisa para o resto do sistema."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ddgs import DDGS

import config

if TYPE_CHECKING:
    from providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


# ── Busca via DuckDuckGo (fallback universal) ────────────────────────────

def search_duckduckgo(query: str, max_results: int | None = None) -> list[dict]:
    """Busca no DuckDuckGo e retorna lista de resultados.

    Cada resultado é ``{"title": str, "url": str, "snippet": str}``.
    """
    max_results = max_results or config.SEARCH_MAX_RESULTS
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    region="pt-br",
                    max_results=max_results,
                )
            )
        # Se pt-br retornou vazio, tenta sem region
        if not results:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(query, max_results=max_results)
                )
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in results
        ]
    except Exception:
        logger.exception("Erro na busca DuckDuckGo para: %s", query)
        return []


def format_search_results(results: list[dict]) -> str:
    """Formata resultados de busca em texto legível para o LLM."""
    if not results:
        return "Nenhum resultado encontrado."
    parts: list[str] = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r['title']}\n    URL: {r['url']}\n    {r['snippet']}"
        )
    return "\n\n".join(parts)


# ── Interface unificada ──────────────────────────────────────────────────

def research(
    query: str,
    provider: BaseLLMProvider,
    *,
    synthesis_prompt: str,
    system_prompt: str | None = None,
) -> str:
    """Pesquisa um tema e retorna a síntese gerada pelo LLM.

    Estratégia:
    1. Se o provider suporta search nativo (ex: Gemini), usa direto.
    2. Caso contrário, faz busca via DuckDuckGo + síntese pelo LLM.

    Args:
        query: Termo de busca.
        provider: Instância do LLM provider.
        synthesis_prompt: Prompt para o LLM sintetizar os dados encontrados.
        system_prompt: System prompt opcional.

    Returns:
        Texto sintetizado pelo LLM.
    """
    if provider.supports_search:
        full_prompt = f"{synthesis_prompt}\n\nBusque informações sobre: {query}"
        try:
            text = provider.generate_with_search(
                full_prompt, system_prompt=system_prompt
            )
            if text and text.strip():
                return text
        except Exception:
            logger.warning(
                "Search grounding falhou para '%s', tentando fallback DuckDuckGo",
                query,
            )

    # Fallback: busca DuckDuckGo → contexto → LLM
    results = search_duckduckgo(query)
    context = format_search_results(results)
    full_prompt = (
        f"{synthesis_prompt}\n\n"
        f"Dados encontrados na web:\n\n{context}"
    )
    return provider.generate(full_prompt, system_prompt=system_prompt)
