"""Agente de analise fundamentalista — orquestra todas as etapas."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from agents import prompts
from providers.base import BaseLLMProvider
from research.brapi import (
    BrapiClient,
    BrapiError,
    extract_structured_data,
)
from research.yahoo_finance import YFinanceClient
from research.web_search import research
from utils.formatting import build_indicators_table, structured_data_summary

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado completo de uma analise de acao."""

    ticker: str
    company_name: str = ""
    profile: str = ""
    financials: str = ""
    news: str = ""
    synthesis: str = ""
    brapi_data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return bool(self.profile or self.financials or self.synthesis)


# Tipo para o callback de progresso
ProgressCallback = Callable[[str, float], None]


def _noop_progress(msg: str, pct: float) -> None:
    """Callback padrao que nao faz nada."""


class StockAnalyst:
    """Agente que executa a analise fundamentalista passo a passo."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        on_progress: ProgressCallback = _noop_progress,
        brapi_token: str | None = None,
    ) -> None:
        self.provider = provider
        self.on_progress = on_progress
        self.brapi = BrapiClient(token=brapi_token)
        self.yahoo = YFinanceClient()

    def analyze(self, ticker: str) -> AnalysisResult:
        """Executa a analise completa para o ticker informado."""
        ticker = ticker.strip().upper()
        result = AnalysisResult(ticker=ticker)

        # Etapa 0 — Dados estruturados (yfinance primario, brapi fallback)
        self.on_progress("Buscando dados financeiros...", 0.0)
        self._step_fetch_data(ticker, result)

        # Etapa 1 — Perfil da Empresa
        self.on_progress("Pesquisando perfil da empresa...", 0.20)
        result.profile = self._step_profile(ticker, result)

        # Nome da empresa (dados ou extraido do perfil)
        if not result.company_name:
            result.company_name = self._extract_company_name(ticker, result.profile)

        # Etapa 2 — Indicadores Financeiros (tabela direta dos dados)
        self.on_progress("Montando indicadores financeiros...", 0.40)
        result.financials = self._step_financials(ticker, result)

        # Etapa 3 — Noticias Recentes
        self.on_progress("Buscando noticias recentes...", 0.60)
        result.news = self._step_news(ticker, result)

        # Etapa 4 — Sintese
        self.on_progress("Gerando sintese de investimento...", 0.80)
        result.synthesis = self._step_synthesis(ticker, result)

        self.on_progress("Analise concluida!", 1.0)
        return result

    # ── Etapas individuais ───────────────────────────────────────────────

    def _step_fetch_data(self, ticker: str, result: AnalysisResult) -> None:
        """Etapa 0: busca dados estruturados (yfinance -> brapi -> web only)."""

        # Tentativa 1: yfinance (primario)
        try:
            quote = self.yahoo.get_quote(ticker)
            if quote and quote.get("regularMarketPrice") is not None:
                result.brapi_data = extract_structured_data(quote)
                result.company_name = (
                    result.brapi_data.get("nome")
                    if result.brapi_data.get("nome") != "N/D"
                    else ""
                ) or ""
                logger.info("Dados obtidos via yfinance para %s", ticker)
                return
        except Exception as e:
            logger.warning("yfinance falhou para %s: %s", ticker, e)

        # Tentativa 2: brapi.dev (fallback)
        try:
            quote = self.brapi.get_quote(ticker)
            result.brapi_data = extract_structured_data(quote)
            result.company_name = (
                result.brapi_data.get("nome")
                if result.brapi_data.get("nome") != "N/D"
                else ""
            ) or ""
            logger.info("Dados obtidos via brapi.dev para %s", ticker)
            return
        except BrapiError as e:
            logger.warning("brapi.dev tambem falhou para %s: %s", ticker, e)
            result.errors["dados"] = (
                f"Yahoo Finance e brapi.dev indisponiveis. "
                f"Usando apenas busca web. ({e})"
            )

    def _step_profile(self, ticker: str, result: AnalysisResult) -> str:
        """Etapa 1: perfil da empresa (dados estruturados + web search)."""
        try:
            data = result.brapi_data
            if data and data.get("nome") != "N/D":
                prompt = prompts.PROFILE_PROMPT_WITH_BRAPI.format(
                    ticker=ticker,
                    nome=data.get("nome", "N/D"),
                    setor=data.get("setor", "N/D"),
                    industria=data.get("industria", "N/D"),
                    descricao=data.get("descricao", "N/D"),
                )
            else:
                prompt = prompts.PROFILE_PROMPT_FALLBACK.format(ticker=ticker)

            query = prompts.PROFILE_SEARCH_QUERY.format(ticker=ticker)
            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa de perfil para %s", ticker)
            result.errors["profile"] = str(e)
            return ""

    def _step_financials(self, ticker: str, result: AnalysisResult) -> str:
        """Etapa 2: indicadores financeiros (tabela direta dos dados)."""
        try:
            if result.brapi_data:
                table = build_indicators_table(result.brapi_data)
                source = result.brapi_data.get("_data_source", "brapi")
                source_label = (
                    "Yahoo Finance" if source == "yfinance" else "brapi.dev"
                )
                source_note = f"\n\n*Fonte: {source_label}*"
                return table + source_note

            # Fallback: sem dados estruturados, usa LLM + web search
            logger.info(
                "Sem dados estruturados para %s, usando fallback web",
                ticker,
            )
            query = f"{ticker} indicadores fundamentalistas P/L ROE margem EBITDA dividend yield"
            prompt = (
                f"Com base nos dados disponiveis sobre {ticker}, extraia e organize os "
                "principais indicadores financeiros.\n\n"
                "Apresente em formato de tabela Markdown com as colunas: Indicador | Valor\n\n"
                "NAO invente valores. Indique a fonte quando possivel. NAO use emojis."
            )
            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa financeira para %s", ticker)
            result.errors["financials"] = str(e)
            return ""

    def _step_news(self, ticker: str, result: AnalysisResult) -> str:
        """Etapa 3: noticias recentes (web search + LLM)."""
        try:
            company = result.company_name or ticker
            query = prompts.NEWS_SEARCH_QUERY.format(
                ticker=ticker, company_name=company
            )
            prompt = prompts.NEWS_PROMPT.format(ticker=ticker, nome=company)
            return research(
                query=query,
                provider=self.provider,
                synthesis_prompt=prompt,
                system_prompt=prompts.SYSTEM_PROMPT,
            )
        except Exception as e:
            logger.exception("Erro na etapa de noticias para %s", ticker)
            result.errors["news"] = str(e)
            return ""

    def _step_synthesis(self, ticker: str, result: AnalysisResult) -> str:
        """Etapa 4: sintese de investimento (LLM com todos os dados)."""
        try:
            # Monta resumo dos dados financeiros para contexto do LLM
            if result.brapi_data:
                financials_ctx = structured_data_summary(result.brapi_data)
                data_level = result.brapi_data.get("_data_level", "minimal")
                if data_level != "full":
                    financials_ctx += (
                        "\n\nNota: alguns indicadores financeiros nao estavam "
                        "disponiveis via API. Baseie sua analise nos dados concretos "
                        "fornecidos e complemente com informacoes da busca web quando "
                        "disponivel. NAO invente numeros — se nao tiver o dado, nao cite."
                    )
            else:
                financials_ctx = result.financials or "Nao disponivel."

            prompt = prompts.SYNTHESIS_PROMPT.format(
                ticker=ticker,
                nome=result.company_name or ticker,
                financials_data=financials_ctx,
                profile=result.profile or "Nao disponivel.",
                news=result.news or "Nao disponivel.",
            )
            return self.provider.generate(
                prompt, system_prompt=prompts.SYSTEM_PROMPT
            )
        except Exception as e:
            logger.exception("Erro na sintese para %s", ticker)
            result.errors["synthesis"] = str(e)
            return ""

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _extract_company_name(ticker: str, profile: str) -> str:
        """Tenta extrair o nome da empresa do perfil gerado."""
        if not profile:
            return ticker
        for line in profile.split("\n"):
            line = line.strip()
            if line and len(line) > 3:
                return line[:60].split(".")[0].strip()
        return ticker
