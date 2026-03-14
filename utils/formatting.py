"""Helpers de formatacao e validacao."""

from __future__ import annotations

import re
from typing import Any


def validate_ticker(ticker: str) -> tuple[bool, str]:
    """Valida se o ticker parece ser uma acao brasileira valida.

    Returns:
        Tupla (is_valid, message).
    """
    ticker = ticker.strip().upper()
    if not ticker:
        return False, "Digite um ticker."

    # Padrao: 4 letras + 1-2 digitos (ex: WEGE3, PETR4, BOVA11)
    pattern = r"^[A-Z]{4}\d{1,2}$"
    if not re.match(pattern, ticker):
        return False, (
            f"'{ticker}' nao parece ser um ticker valido. "
            "Use o formato: 4 letras + numero (ex: WEGE3, PETR4, VALE3)."
        )

    return True, ticker


def truncate(text: str, max_length: int = 500) -> str:
    """Trunca texto mantendo palavras inteiras."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(" ", 1)[0]
    return truncated + "..."


# ── Formatacao financeira ────────────────────────────────────────────────

def _is_number(value: Any) -> bool:
    """Checa se o valor e numerico (nao 'N/D')."""
    return isinstance(value, (int, float))


def format_market_cap(value: Any) -> str:
    """Formata market cap em formato legivel (B, M, T)."""
    if not _is_number(value):
        return "N/D"
    v = float(value)
    if v >= 1e12:
        return f"R$ {v / 1e12:.1f}T"
    if v >= 1e9:
        return f"R$ {v / 1e9:.1f}B"
    if v >= 1e6:
        return f"R$ {v / 1e6:.1f}M"
    return f"R$ {v:,.0f}"


def format_currency(value: Any) -> str:
    """Formata valor monetario."""
    if not _is_number(value):
        return "N/D"
    v = float(value)
    if abs(v) >= 1e9:
        return f"R$ {v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"R$ {v / 1e6:.1f}M"
    return f"R$ {v:,.2f}"


def format_percent(value: Any, is_ratio: bool = True) -> str:
    """Formata percentual. Se is_ratio=True, multiplica por 100."""
    if not _is_number(value):
        return "N/D"
    v = float(value)
    if is_ratio:
        v *= 100
    return f"{v:.1f}%"


def format_multiple(value: Any, suffix: str = "x") -> str:
    """Formata multiplo (ex: 12.3x)."""
    if not _is_number(value):
        return "N/D"
    return f"{float(value):.1f}{suffix}"


def build_indicators_table(data: dict[str, Any]) -> str:
    """Monta tabela Markdown de indicadores a partir dos dados estruturados da brapi.

    Filtra automaticamente indicadores com valor 'N/D'.
    """
    rows: list[tuple[str, str]] = [
        ("Preco Atual", format_currency(data.get("preco_atual")) if _is_number(data.get("preco_atual")) else "N/D"),
        ("Variacao Dia", format_percent(data.get("variacao_dia"), is_ratio=False) if _is_number(data.get("variacao_dia")) else "N/D"),
        ("Market Cap", format_market_cap(data.get("market_cap"))),
        ("P/L", format_multiple(data.get("preco_lucro"))),
        ("P/VP", format_multiple(data.get("pvp"))),
        ("EV/EBITDA", format_multiple(data.get("ev_ebitda"))),
        ("LPA", format_currency(data.get("lpa")) if _is_number(data.get("lpa")) else "N/D"),
        ("Dividend Yield", format_percent(data.get("dividend_yield"))),
        ("ROE", format_percent(data.get("roe"))),
        ("ROA", format_percent(data.get("roa"))),
        ("Margem EBITDA", format_percent(data.get("margem_ebitda"))),
        ("Margem Liquida", format_percent(data.get("margem_lucro"))),
        ("Margem Bruta", format_percent(data.get("margem_bruta"))),
        ("Div. Liq./Equity", format_percent(data.get("divida_equity"), is_ratio=False) if _is_number(data.get("divida_equity")) else "N/D"),
        ("Receita Total", format_currency(data.get("receita_total"))),
        ("EBITDA", format_currency(data.get("ebitda"))),
        ("Lucro Bruto", format_currency(data.get("lucro_bruto"))),
        ("Caixa Total", format_currency(data.get("caixa_total"))),
        ("Divida Total", format_currency(data.get("divida_total"))),
        ("Cresc. Receita", format_percent(data.get("crescimento_receita"))),
        ("Cresc. Lucro", format_percent(data.get("crescimento_lucro"))),
        ("Max. 52 semanas", format_currency(data.get("max_52sem")) if _is_number(data.get("max_52sem")) else "N/D"),
        ("Min. 52 semanas", format_currency(data.get("min_52sem")) if _is_number(data.get("min_52sem")) else "N/D"),
    ]

    # Filtra N/D
    rows = [(label, val) for label, val in rows if val != "N/D"]

    if not rows:
        return "_Dados financeiros nao disponiveis._"

    lines = ["| Indicador | Valor |", "|-----------|-------|"]
    for label, val in rows:
        lines.append(f"| {label} | {val} |")

    return "\n".join(lines)


def structured_data_summary(data: dict[str, Any]) -> str:
    """Formata dados estruturados como texto legivel para contexto do LLM."""
    lines: list[str] = []
    mapping = [
        ("Preco Atual", "preco_atual", lambda v: format_currency(v)),
        ("Variacao Dia", "variacao_dia", lambda v: format_percent(v, is_ratio=False)),
        ("Market Cap", "market_cap", format_market_cap),
        ("P/L", "preco_lucro", lambda v: format_multiple(v)),
        ("P/VP", "pvp", lambda v: format_multiple(v)),
        ("EV/EBITDA", "ev_ebitda", lambda v: format_multiple(v)),
        ("Dividend Yield", "dividend_yield", lambda v: format_percent(v)),
        ("ROE", "roe", lambda v: format_percent(v)),
        ("ROA", "roa", lambda v: format_percent(v)),
        ("Margem EBITDA", "margem_ebitda", lambda v: format_percent(v)),
        ("Margem Liquida", "margem_lucro", lambda v: format_percent(v)),
        ("Div./Equity", "divida_equity", lambda v: format_percent(v, is_ratio=False)),
        ("Receita Total", "receita_total", format_currency),
        ("EBITDA", "ebitda", format_currency),
        ("Caixa Total", "caixa_total", format_currency),
        ("Divida Total", "divida_total", format_currency),
        ("Cresc. Receita", "crescimento_receita", lambda v: format_percent(v)),
        ("Cresc. Lucro", "crescimento_lucro", lambda v: format_percent(v)),
    ]
    for label, key, fmt in mapping:
        val = data.get(key)
        if _is_number(val):
            lines.append(f"- {label}: {fmt(val)}")

    return "\n".join(lines) if lines else "Dados financeiros nao disponiveis."
