"""Cliente da API brapi.dev — dados financeiros estruturados de acoes brasileiras."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

BRAPI_BASE_URL = "https://brapi.dev/api"

# Niveis de dados retornados pela brapi
DATA_LEVEL_FULL = "full"
DATA_LEVEL_PROFILE = "basic_with_profile"
DATA_LEVEL_MINIMAL = "minimal"


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

    def _fetch(
        self, ticker: str, modules: str | None = None
    ) -> dict[str, Any] | None:
        """Faz uma requisicao a brapi.dev.

        Returns:
            Dicionario com dados da acao ou None se nao encontrou resultados.

        Raises:
            BrapiTickerNotFound: Ticker nao existe.
            BrapiTokenRequired: Token necessario.
            BrapiError: Erro generico ou HTTP != 200.
        """
        url = f"{BRAPI_BASE_URL}/quote/{ticker.upper()}"
        params: dict[str, str] = {}
        if modules:
            params["modules"] = modules
        if self.token:
            params["token"] = self.token

        try:
            resp = requests.get(url, params=params, timeout=15)
        except requests.RequestException as e:
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
            return None

        return results[0]

    def get_quote(self, ticker: str) -> dict[str, Any]:
        """Busca cotacao com fallback progressivo de modulos.

        Nivel 1: todos os modulos (summaryProfile + financialData + defaultKeyStatistics)
        Nivel 2: so summaryProfile (sempre funciona com token gratuito)
        Nivel 3: sem modulos (dados basicos de mercado)

        Returns:
            Dicionario com dados da acao e campo '_data_level' indicando
            o nivel de dados obtido.

        Raises:
            BrapiTickerNotFound: Ticker nao existe.
            BrapiTokenRequired: Token necessario para este ticker.
            BrapiError: brapi.dev indisponivel.
        """
        ticker = ticker.upper()

        # Nivel 1: todos os modulos
        try:
            data = self._fetch(
                ticker,
                modules="summaryProfile,financialData,defaultKeyStatistics",
            )
            if data:
                data["_data_level"] = DATA_LEVEL_FULL
                return data
        except (BrapiTickerNotFound, BrapiTokenRequired):
            raise
        except BrapiError:
            logger.info(
                "brapi nivel 1 (full) falhou para %s, tentando summaryProfile",
                ticker,
            )

        # Nivel 2: so summaryProfile
        try:
            data = self._fetch(ticker, modules="summaryProfile")
            if data:
                data["_data_level"] = DATA_LEVEL_PROFILE
                return data
        except (BrapiTickerNotFound, BrapiTokenRequired):
            raise
        except BrapiError:
            logger.info(
                "brapi nivel 2 (profile) falhou para %s, tentando sem modulos",
                ticker,
            )

        # Nivel 3: sem modulos
        data = self._fetch(ticker, modules=None)
        if data:
            data["_data_level"] = DATA_LEVEL_MINIMAL
            return data

        raise BrapiTickerNotFound(
            f"Ticker {ticker} nao retornou resultados na brapi.dev."
        )


def extract_structured_data(quote: dict[str, Any]) -> dict[str, Any]:
    """Extrai dados estruturados de um quote (brapi ou yfinance).

    Detecta automaticamente a fonte pelo campo '_data_source'.
    Todos os campos usam 'N/D' como fallback quando nao disponivel.
    """
    source = quote.get("_data_source", "brapi")

    if source == "yfinance":
        return _extract_yfinance(quote)
    return _extract_brapi(quote)


def _extract_yfinance(quote: dict[str, Any]) -> dict[str, Any]:
    """Extrai dados do formato yfinance (campos no nivel raiz)."""

    def _v(val: Any) -> Any:
        """Retorna o valor ou 'N/D' se None/vazio."""
        if val is None or val == "":
            return "N/D"
        return val

    return {
        "_data_level": quote.get("_data_level", DATA_LEVEL_FULL),
        "_data_source": "yfinance",
        "nome": quote.get("longName") or "N/D",
        "nome_curto": quote.get("shortName") or "N/D",
        "setor": quote.get("sector") or "N/D",
        "industria": quote.get("industry") or "N/D",
        "descricao": quote.get("longBusinessSummary") or "N/D",
        "logo_url": quote.get("logourl") or "",
        "website": quote.get("website") or "N/D",
        "funcionarios": _v(quote.get("fullTimeEmployees")),
        "preco_atual": _v(quote.get("regularMarketPrice")),
        "variacao_dia": _v(quote.get("regularMarketChangePercent")),
        "market_cap": _v(quote.get("marketCap")),
        "volume": _v(quote.get("regularMarketVolume")),
        "max_52sem": _v(quote.get("fiftyTwoWeekHigh")),
        "min_52sem": _v(quote.get("fiftyTwoWeekLow")),
        "preco_lucro": _v(quote.get("priceEarnings")),
        "preco_lucro_forward": _v(quote.get("forwardPE")),
        "lpa": _v(quote.get("earningsPerShare")),
        "pvp": _v(quote.get("priceToBook")),
        "ev_ebitda": _v(quote.get("enterpriseToEbitda")),
        "peg_ratio": _v(quote.get("pegRatio")),
        "dividend_yield": _v(quote.get("dividendYield")),
        "payout_ratio": _v(quote.get("payoutRatio")),
        "ebitda": _v(quote.get("ebitda")),
        "margem_ebitda": _v(quote.get("ebitdaMargins")),
        "margem_operacional": _v(quote.get("operatingMargins")),
        "margem_lucro": _v(quote.get("profitMargins")),
        "margem_bruta": _v(quote.get("grossMargins")),
        "roe": _v(quote.get("returnOnEquity")),
        "roa": _v(quote.get("returnOnAssets")),
        "divida_equity": _v(quote.get("debtToEquity")),
        "receita_total": _v(quote.get("totalRevenue")),
        "lucro_bruto": _v(quote.get("grossProfits")),
        "caixa_total": _v(quote.get("totalCash")),
        "divida_total": _v(quote.get("totalDebt")),
        "free_cashflow": _v(quote.get("freeCashflow")),
        "lucro_liquido": _v(quote.get("netIncome")),
        "lucro_liquido_historico": quote.get("netIncomeHistory") or {},
        "crescimento_receita": _v(quote.get("revenueGrowth")),
        "crescimento_lucro": _v(quote.get("earningsGrowth")),
    }


def _extract_brapi(quote: dict[str, Any]) -> dict[str, Any]:
    """Extrai dados do formato brapi (campos aninhados em modulos)."""
    fin = quote.get("financialData") or {}
    stats = quote.get("defaultKeyStatistics") or {}
    profile = quote.get("summaryProfile") or {}

    return {
        "_data_level": quote.get("_data_level", DATA_LEVEL_MINIMAL),
        "_data_source": "brapi",
        "nome": quote.get("longName") or "N/D",
        "nome_curto": quote.get("shortName") or "N/D",
        "setor": profile.get("sector") or "N/D",
        "industria": profile.get("industry") or "N/D",
        "descricao": profile.get("longBusinessSummary") or "N/D",
        "logo_url": quote.get("logourl") or "",
        "preco_atual": quote.get("regularMarketPrice", "N/D"),
        "variacao_dia": quote.get("regularMarketChangePercent", "N/D"),
        "market_cap": quote.get("marketCap", "N/D"),
        "volume": quote.get("regularMarketVolume", "N/D"),
        "max_52sem": quote.get("fiftyTwoWeekHigh", "N/D"),
        "min_52sem": quote.get("fiftyTwoWeekLow", "N/D"),
        "preco_lucro": quote.get("priceEarnings", "N/D"),
        "lpa": quote.get("earningsPerShare", "N/D"),
        "pvp": stats.get("priceToBook", "N/D"),
        "ev_ebitda": stats.get("enterpriseToEbitda", "N/D"),
        "dividend_yield": quote.get("dividendYield")
        or stats.get("dividendYield", "N/D"),
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
