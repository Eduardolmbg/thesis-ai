"""Cliente Yahoo Finance via yfinance — fonte primaria de dados financeiros."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float))


class YFinanceClient:
    """Cliente para buscar dados financeiros via Yahoo Finance (yfinance)."""

    def get_quote(self, ticker: str) -> dict[str, Any]:
        """Busca dados completos de uma acao brasileira.

        O ticker brasileiro precisa ter .SA no final (ex: PETR4.SA),
        mas o usuario digita sem .SA — a normalizacao e feita aqui.

        Returns:
            Dicionario com dados estruturados ou {} se falhar.
        """
        yahoo_ticker = self._normalize_ticker(ticker)

        try:
            stock = yf.Ticker(yahoo_ticker)
            info = stock.info

            if not info or info.get("regularMarketPrice") is None:
                logger.warning("yfinance retornou dados vazios para %s", yahoo_ticker)
                return {}

            # Buscar lucro liquido da DRE
            net_income = None
            net_income_history: dict[str, float] = {}
            try:
                income_stmt = stock.income_stmt
                if income_stmt is not None and not income_stmt.empty:
                    if "Net Income" in income_stmt.index:
                        latest = income_stmt.iloc[:, 0]
                        net_income = latest.get("Net Income")
                        for col in income_stmt.columns:
                            year = str(col.year) if hasattr(col, "year") else str(col)[:4]
                            ni = income_stmt.loc["Net Income", col]
                            if ni is not None and _is_number(ni) and not pd.isna(ni):
                                net_income_history[year] = float(ni)
            except Exception:
                logger.debug("Nao foi possivel buscar DRE para %s", yahoo_ticker)

            return {
                # Identificacao
                "symbol": ticker.upper().replace(".SA", ""),
                "longName": info.get("longName") or info.get("shortName") or "",
                "shortName": info.get("shortName") or "",
                "logourl": info.get("logo_url") or "",
                # Perfil
                "sector": info.get("sector") or "",
                "industry": info.get("industry") or "",
                "longBusinessSummary": info.get("longBusinessSummary") or "",
                "fullTimeEmployees": info.get("fullTimeEmployees"),
                "website": info.get("website") or "",
                # Mercado
                "regularMarketPrice": info.get("currentPrice")
                or info.get("regularMarketPrice"),
                "regularMarketChangePercent": info.get(
                    "regularMarketChangePercent"
                ),
                "marketCap": info.get("marketCap"),
                "regularMarketVolume": info.get("regularMarketVolume")
                or info.get("volume"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                # Valuation
                "priceEarnings": info.get("trailingPE")
                or info.get("forwardPE"),
                "forwardPE": info.get("forwardPE"),
                "earningsPerShare": info.get("trailingEps"),
                "priceToBook": info.get("priceToBook"),
                "enterpriseToEbitda": info.get("enterpriseToEbitda"),
                "enterpriseToRevenue": info.get("enterpriseToRevenue"),
                "pegRatio": info.get("pegRatio"),
                # Rentabilidade
                "returnOnEquity": info.get("returnOnEquity"),
                "returnOnAssets": info.get("returnOnAssets"),
                # Margens
                "grossMargins": info.get("grossMargins"),
                "ebitdaMargins": info.get("ebitdaMargins"),
                "operatingMargins": info.get("operatingMargins"),
                "profitMargins": info.get("profitMargins"),
                # Financeiro
                "totalRevenue": info.get("totalRevenue"),
                "ebitda": info.get("ebitda"),
                "netIncome": net_income,
                "netIncomeHistory": net_income_history,
                "grossProfits": info.get("grossProfits"),
                "totalCash": info.get("totalCash"),
                "totalDebt": info.get("totalDebt"),
                "debtToEquity": info.get("debtToEquity"),
                "freeCashflow": info.get("freeCashflow"),
                "operatingCashflow": info.get("operatingCashflow"),
                # Crescimento
                "revenueGrowth": info.get("revenueGrowth"),
                "earningsGrowth": info.get("earningsGrowth"),
                # Dividendos (dividendYield vem em % do yfinance, normalizar para ratio)
                "dividendYield": info.get("dividendYield") / 100
                if _is_number(info.get("dividendYield"))
                else None,
                "dividendRate": info.get("dividendRate"),
                "payoutRatio": info.get("payoutRatio"),
                # Meta
                "_data_source": "yfinance",
                "_data_level": "full",
            }

        except Exception:
            logger.exception("Erro yfinance para %s", yahoo_ticker)
            return {}

    def get_history(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Busca historico de precos.

        Args:
            ticker: Codigo da acao (ex: PETR4).
            period: Periodo (1mo, 3mo, 6mo, 1y, 2y, 5y, max).

        Returns:
            DataFrame com Open, High, Low, Close, Volume ou vazio se falhar.
        """
        yahoo_ticker = self._normalize_ticker(ticker)
        try:
            stock = yf.Ticker(yahoo_ticker)
            hist = stock.history(period=period)
            return hist
        except Exception:
            logger.exception("Erro ao buscar historico para %s", yahoo_ticker)
            return pd.DataFrame()

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        """Converte ticker brasileiro para formato Yahoo Finance (adiciona .SA)."""
        ticker = ticker.upper().strip()
        if ticker.endswith(".SA"):
            return ticker
        if len(ticker) >= 4 and ticker[-1].isdigit():
            return f"{ticker}.SA"
        return ticker
