"""Cliente da API brapi.dev — dados financeiros estruturados de acoes brasileiras."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

BRAPI_BASE_URL = "https://brapi.dev/api"


class BrapiError(Exception):
    """Erro generico da brapi."""


class BrapiTickerNotFound(BrapiError):
    """Ticker nao encontrado na brapi."""


class BrapiTokenRequired(BrapiError):
    """Token necessario para acessar este ticker."""


class BrapiClient:
    """Cliente para a API brapi.dev."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def get_quote(self, ticker: str) -> dict[str, Any]:
        """Busca cotacao e dados completos de uma acao.

        Args:
            ticker: Codigo da acao (ex: PETR4, VALE3).

        Returns:
            Dicionario com dados da acao.

        Raises:
            BrapiTickerNotFound: Ticker nao existe.
            BrapiTokenRequired: Token necessario para este ticker.
            BrapiError: Erro generico da API.
        """
        url = f"{BRAPI_BASE_URL}/quote/{ticker.upper()}"
        params: dict[str, str] = {
            "modules": "summaryProfile,financialData,defaultKeyStatistics",
        }
        if self.token:
            params["token"] = self.token

        try:
            resp = requests.get(url, params=params, timeout=15)
        except requests.RequestException as e:
            logger.warning("brapi.dev indisponivel: %s", e)
            raise BrapiError(f"brapi.dev indisponivel: {e}") from e

        if resp.status_code == 404:
            raise BrapiTickerNotFound(
                f"Ticker {ticker} nao encontrado. "
                "Verifique se o codigo esta correto (ex: PETR4, nao PETR)."
            )
        if resp.status_code in (401, 403):
            raise BrapiTokenRequired(
                f"Token brapi.dev necessario para o ticker {ticker}. "
                "Cadastre-se gratuitamente em https://brapi.dev"
            )
        if resp.status_code != 200:
            raise BrapiError(
                f"Erro na brapi.dev (HTTP {resp.status_code}): {resp.text[:200]}"
            )

        data = resp.json()
        results = data.get("results")
        if not results:
            raise BrapiTickerNotFound(
                f"Ticker {ticker} nao retornou resultados na brapi.dev."
            )

        return results[0]


def extract_structured_data(quote: dict[str, Any]) -> dict[str, Any]:
    """Extrai dados estruturados do JSON retornado pela brapi.

    Todos os campos usam 'N/D' como fallback quando nao disponivel.
    """
    fin = quote.get("financialData") or {}
    stats = quote.get("defaultKeyStatistics") or {}
    profile = quote.get("summaryProfile") or {}

    return {
        # Cadastrais
        "nome": quote.get("longName") or "N/D",
        "nome_curto": quote.get("shortName") or "N/D",
        "setor": profile.get("sector") or "N/D",
        "industria": profile.get("industry") or "N/D",
        "descricao": profile.get("longBusinessSummary") or "N/D",
        "logo_url": quote.get("logourl") or "",
        # Mercado
        "preco_atual": quote.get("regularMarketPrice", "N/D"),
        "variacao_dia": quote.get("regularMarketChangePercent", "N/D"),
        "market_cap": quote.get("marketCap", "N/D"),
        "volume": quote.get("regularMarketVolume", "N/D"),
        "max_52sem": quote.get("fiftyTwoWeekHigh", "N/D"),
        "min_52sem": quote.get("fiftyTwoWeekLow", "N/D"),
        # Valuation
        "preco_lucro": quote.get("priceEarnings", "N/D"),
        "lpa": quote.get("earningsPerShare", "N/D"),
        "pvp": stats.get("priceToBook", "N/D"),
        "ev_ebitda": stats.get("enterpriseToEbitda", "N/D"),
        "dividend_yield": quote.get("dividendYield")
        or stats.get("dividendYield", "N/D"),
        # financialData
        "ebitda": fin.get("ebitda", "N/D"),
        "margem_ebitda": fin.get("ebitdaMargins", "N/D"),
        "margem_lucro": fin.get("profitMargins", "N/D"),
        "margem_bruta": fin.get("grossMargins", "N/D"),
        "roe": fin.get("returnOnEquity", "N/D"),
        "roa": fin.get("returnOnAssets", "N/D"),
        "divida_equity": fin.get("debtToEquity", "N/D"),
        "receita_total": fin.get("totalRevenue", "N/D"),
        "lucro_bruto": fin.get("grossProfits", "N/D"),
        "caixa_total": fin.get("totalCash", "N/D"),
        "divida_total": fin.get("totalDebt", "N/D"),
        "crescimento_receita": fin.get("revenueGrowth", "N/D"),
        "crescimento_lucro": fin.get("earningsGrowth", "N/D"),
    }
