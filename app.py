"""Verto — AI-Powered Equity Research (Streamlit app)."""

from __future__ import annotations

import time
from datetime import datetime

import streamlit as st

import config
from providers import get_provider
from agents.stock_analyst import StockAnalyst
from reports.generator import generate_report, save_report, report_to_html
from research.yahoo_finance import YFinanceClient
from research.peers import get_peers
from agents.prompts import PEER_COMPARISON_PROMPT, SYSTEM_PROMPT
from utils.formatting import validate_ticker
from utils.theme import (
    inject_css,
    render_header,
    render_sidebar_brand,
    render_empty_state,
    render_footer,
    render_data_cards,
    render_report_header,
    render_bias_badge,
    render_news_with_badges,
    parse_bias,
    icon,
    COLORS,
)

# ── Page config ──────────────────────────────────────────────────────────

from pathlib import Path
from PIL import Image as _PIL_Image

_logo2_path = Path(__file__).resolve().parent / "logo2.png"
_page_icon = _PIL_Image.open(_logo2_path) if _logo2_path.exists() else None

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ──────────────────────────────────────────────────────────────

with st.sidebar:
    render_sidebar_brand()

    st.markdown(
        '<div class="sidebar-section-title">Provider</div>',
        unsafe_allow_html=True,
    )

    _provider_options = ["gemini", "openai", "groq"]
    _saved_provider = config.LLM_PROVIDER.lower()
    _provider_index = _provider_options.index(_saved_provider) if _saved_provider in _provider_options else 0

    provider_name = st.selectbox(
        "LLM Provider",
        options=_provider_options,
        index=_provider_index,
        help="Selecione o provedor de LLM. Apenas Gemini e Groq estao implementados.",
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-section-title">API Key</div>',
        unsafe_allow_html=True,
    )

    api_key = st.text_input(
        "API Key",
        type="password",
        value=config.LLM_API_KEY,
        help="Cole aqui a API key do provider selecionado.",
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-section-title">brapi.dev Token (opcional)</div>',
        unsafe_allow_html=True,
    )

    brapi_token = st.text_input(
        "brapi.dev Token",
        type="password",
        value=config.BRAPI_TOKEN,
        help="Fonte primaria: Yahoo Finance (automatico). brapi.dev e usado como fallback.",
        label_visibility="collapsed",
    )

    if st.button("Salvar configuracao", use_container_width=True):
        st.session_state["provider_name"] = provider_name
        st.session_state["api_key"] = api_key
        st.session_state["brapi_token"] = brapi_token
        config.save_env(
            LLM_PROVIDER=provider_name,
            LLM_API_KEY=api_key,
            BRAPI_TOKEN=brapi_token,
        )
        st.success("Configuracao salva no .env.")

    st.divider()

    st.markdown(
        '<div class="sidebar-section-title">Sobre</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Verto** v{config.APP_VERSION}\n\n"
        "Agente de IA que gera relatorios de analise "
        "fundamentalista de acoes brasileiras.",
        unsafe_allow_html=False,
    )

# Resolve provider/key from session or defaults
active_provider = st.session_state.get("provider_name", provider_name)
active_key = st.session_state.get("api_key", api_key)
active_brapi_token = st.session_state.get("brapi_token", brapi_token)

# ── Main area ────────────────────────────────────────────────────────────

render_header()

ticker_input = st.text_input(
    "Ticker da acao",
    value=st.session_state.pop("chip_ticker", ""),
    placeholder="Digite o ticker: WEGE3",
    max_chars=10,
    help="Codigo da acao na B3.",
    label_visibility="collapsed",
)

analyze_btn = st.button(
    "Gerar Analise",
    type="primary",
    use_container_width=True,
)

# ── Peer comparison helpers ──────────────────────────────────────────────

_PEER_METRICS = [
    {"key": "regularMarketPrice", "label": "Preco",          "format": "price",      "lower_is_better": False},
    {"key": "marketCap",          "label": "Market Cap",     "format": "market_cap", "lower_is_better": False},
    {"key": "priceEarnings",      "label": "P/L",            "format": "multiple",   "lower_is_better": True},
    {"key": "enterpriseToEbitda", "label": "EV/EBITDA",      "format": "multiple",   "lower_is_better": True},
    {"key": "priceToBook",        "label": "P/VP",           "format": "multiple",   "lower_is_better": True},
    {"key": "returnOnEquity",     "label": "ROE",            "format": "percent",    "lower_is_better": False},
    {"key": "ebitdaMargins",      "label": "Margem EBITDA",  "format": "percent",    "lower_is_better": False},
    {"key": "profitMargins",      "label": "Margem Liquida", "format": "percent",    "lower_is_better": False},
    {"key": "dividendYield",      "label": "Div. Yield",     "format": "percent",    "lower_is_better": False},
    {"key": "debtToEquity",       "label": "Div./Equity",    "format": "debt_equity","lower_is_better": True},
    {"key": "revenueGrowth",      "label": "Cresc. Receita", "format": "percent",    "lower_is_better": False},
    {"key": "capex_receita",      "label": "CAPEX/Receita",  "format": "multiple",   "lower_is_better": None},
]


def _fmt_metric(val: object, fmt: str) -> str:
    """Formata valor de métrica para célula da tabela."""
    if val is None or not isinstance(val, (int, float)):
        return '<span style="color:#3f3f46;">N/D</span>'
    if fmt == "price":
        return f"R$ {val:.2f}"
    if fmt == "market_cap":
        if val >= 1e12:
            return f"R$ {val/1e12:.1f}T"
        if val >= 1e9:
            return f"R$ {val/1e9:.1f}B"
        if val >= 1e6:
            return f"R$ {val/1e6:.0f}M"
        return f"R$ {val:,.0f}"
    if fmt == "multiple":
        return f"{val:.1f}x"
    if fmt == "percent":
        return f"{val * 100:.1f}%"
    if fmt == "debt_equity":
        # yfinance retorna debtToEquity em %, converter para multiplicador
        return f"{val / 100:.2f}x"
    return f"{val:.2f}"


def _peer_medians(companies: list[dict]) -> dict[str, float]:
    """Calcula medianas de cada métrica entre todos os peers + empresa principal."""
    medians: dict[str, float] = {}
    for m in _PEER_METRICS:
        vals = sorted(
            v for c in companies
            if isinstance(v := c.get(m["key"]), (int, float))
        )
        if vals:
            mid = len(vals) // 2
            medians[m["key"]] = (vals[mid - 1] + vals[mid]) / 2 if len(vals) % 2 == 0 else vals[mid]
    return medians


def _render_peer_table(main_ticker: str, all_companies: list[dict]) -> None:
    """Renderiza tabela comparativa de peers como HTML."""
    medians = _peer_medians(all_companies)

    # ── Header ───────────────────────────────────────────────────────────
    th_base = "padding:10px 14px;font-size:12px;font-weight:600;white-space:nowrap;"
    header_cells = f'<th style="{th_base}text-align:left;color:#71717a;">Indicador</th>'
    for c in all_companies:
        sym = c.get("symbol", "").upper()
        is_main = sym == main_ticker.upper()
        bg = "background:#1d4ed8;" if is_main else "background:#18181b;"
        header_cells += (
            f'<th style="{th_base}text-align:center;{bg}color:#f4f4f5;">'
            f'{sym}</th>'
        )
    header_cells += f'<th style="{th_base}text-align:center;color:#52525b;font-style:italic;">Mediana</th>'

    # ── Rows ─────────────────────────────────────────────────────────────
    rows_html = ""
    for i, m in enumerate(_PEER_METRICS):
        bg_row = "rgba(255,255,255,0.025)" if i % 2 == 0 else "transparent"
        td_base = f"padding:9px 14px;background:{bg_row};white-space:nowrap;"

        row = (
            f'<td style="{td_base}color:#a1a1aa;font-size:13px;">'
            f'{m["label"]}</td>'
        )

        median_val = medians.get(m["key"])
        for c in all_companies:
            val = c.get(m["key"])
            sym = c.get("symbol", "").upper()
            is_main = sym == main_ticker.upper()
            formatted = _fmt_metric(val, m["format"])

            color = "#e4e4e7"
            if (m["lower_is_better"] is not None
                    and isinstance(val, (int, float))
                    and isinstance(median_val, float)):
                better = val < median_val if m["lower_is_better"] else val > median_val
                worse  = val > median_val * 1.2 if m["lower_is_better"] else val < median_val * 0.8
                if better:
                    color = "#10b981"
                elif worse:
                    color = "#ef4444"

            fw = "700" if is_main else "400"
            row += (
                f'<td style="{td_base}text-align:center;color:{color};'
                f'font-family:JetBrains Mono,monospace;font-size:13px;font-weight:{fw};">'
                f'{formatted}</td>'
            )

        med_fmt = _fmt_metric(median_val, m["format"])
        row += (
            f'<td style="{td_base}text-align:center;color:#52525b;'
            f'font-family:JetBrains Mono,monospace;font-size:13px;font-style:italic;">'
            f'{med_fmt}</td>'
        )
        rows_html += f"<tr>{row}</tr>"

    html = (
        '<div style="overflow-x:auto;margin:16px 0;">'
        '<table style="width:100%;border-collapse:collapse;'
        'border:1px solid #1e1e2e;border-radius:8px;overflow:hidden;">'
        f'<thead><tr style="background:#12121a;border-bottom:2px solid #1e1e2e;">'
        f'{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _format_comparison_for_llm(main_ticker: str, all_companies: list[dict]) -> tuple[str, str]:
    """Retorna (tabela_txt, medianas_txt) para o prompt do LLM."""
    medians = _peer_medians(all_companies)

    # Tabela em texto
    cols = ["Indicador"] + [c.get("symbol", "?") for c in all_companies]
    lines = [" | ".join(cols)]
    lines.append(" | ".join(["---"] * len(cols)))
    for m in _PEER_METRICS:
        row = [m["label"]]
        for c in all_companies:
            row.append(_fmt_metric(c.get(m["key"]), m["format"]).replace('<span style="color:#3f3f46;">', "").replace("</span>", ""))
        lines.append(" | ".join(row))
    table_txt = "\n".join(lines)

    # Medianas
    _nd_span = '<span style="color:#3f3f46;">'
    med_lines = []
    for m in _PEER_METRICS:
        val = medians.get(m["key"])
        formatted = _fmt_metric(val, m["format"]).replace(_nd_span, "").replace("</span>", "")
        med_lines.append(f"- {m['label']}: {formatted}")
    medianas_txt = "\n".join(med_lines)

    return table_txt, medianas_txt


def _get_peers_auto(ticker: str, company_name: str, sector: str, industry: str, provider) -> list[str]:
    """Usa o LLM para identificar peers quando não estão no mapeamento hardcoded."""
    import re
    prompt = (
        f"Identifique os 4-5 principais concorrentes de {company_name} ({ticker}) listados na B3.\n\n"
        f"Setor: {sector}\nIndustria: {industry}\n\n"
        "Responda APENAS com os tickers da B3 separados por virgula, nada mais.\n"
        "Exemplo: ITUB4, BBDC4, BBAS3, SANB11"
    )
    try:
        raw = provider.generate(prompt) or ""
        # Regex extrai padrões de ticker brasileiro: 4 letras + 1-2 dígitos
        found = re.findall(r'\b([A-Z]{4}\d{1,2})\b', raw.upper())
        return [t for t in dict.fromkeys(found) if t != ticker.upper()][:5]
    except Exception:
        return []


def _render_peer_comparison_section(ticker: str, result_brapi_data: dict, provider) -> None:
    """Renderiza a seção de Comparação Setorial (chamada dentro de um expander)."""
    sector = result_brapi_data.get("setor", "") if result_brapi_data else ""
    industry = result_brapi_data.get("industria", "") if result_brapi_data else ""
    company_name = result_brapi_data.get("nome", ticker) if result_brapi_data else ticker

    # 1. Hardcoded (mais confiável)
    peers_list = get_peers(ticker)
    peers_source = "curado"

    # 2. Fallback via LLM (cacheado por sessão)
    if not peers_list:
        auto_key = f"peers_auto_{ticker}"
        if auto_key not in st.session_state:
            with st.spinner("Identificando peers via IA..."):
                st.session_state[auto_key] = _get_peers_auto(
                    ticker, company_name, sector, industry, provider
                )
        peers_list = st.session_state[auto_key]
        peers_source = "ia"

    # Indicador de fonte
    source_label = (
        "Peers: mapeamento curado"
        if peers_source == "curado"
        else "Peers: sugeridos por IA (edite se necessario)"
    )
    st.markdown(
        f'<p style="color:#52525b;font-size:11px;margin:0 0 6px 0;">{source_label}</p>',
        unsafe_allow_html=True,
    )

    # Pré-popular session_state explicitamente — Streamlit usa session_state como
    # fonte de verdade para widgets com key=; o parâmetro value= é ignorado se a
    # key já existir. Só definimos na primeira vez para não sobrescrever edições do usuário.
    input_key = f"peers_input_{ticker}"
    if input_key not in st.session_state:
        st.session_state[input_key] = ", ".join(peers_list)

    peers_input = st.text_input(
        "Peers para comparacao (separados por virgula)",
        placeholder="Ex: ITUB4, BBDC4, BBAS3, SANB11",
        key=input_key,
    )
    edited_peers = [p.strip().upper() for p in peers_input.split(",") if p.strip()][:5]

    if st.button("Carregar Comparacao", key=f"load_peers_{ticker}", type="primary"):
        if not edited_peers:
            st.warning("Informe ao menos um peer para comparar.")
            return

        with st.spinner("Buscando dados dos peers..."):
            yahoo = YFinanceClient()

            main_key = f"peer_main_{ticker}"
            if main_key not in st.session_state:
                st.session_state[main_key] = yahoo.get_quote(ticker)
            main_data = st.session_state[main_key]

            if not main_data or not main_data.get("regularMarketPrice"):
                st.error("Nao foi possivel obter dados do ticker principal.")
                return

            peers_key = f"peer_data_{ticker}_{'_'.join(edited_peers)}"
            if peers_key not in st.session_state:
                st.session_state[peers_key] = yahoo.get_peers_data(edited_peers)
            peers_data = st.session_state[peers_key]

            if not peers_data:
                st.warning("Nao foi possivel obter dados dos peers selecionados.")
                return

            # Enriquecer cada empresa com capex_receita calculado
        def _enrich(d: dict) -> dict:
            capex = d.get("capitalExpenditure")
            rev = d.get("totalRevenue")
            if isinstance(capex, (int, float)) and isinstance(rev, (int, float)) and rev > 0:
                d["capex_receita"] = capex / rev
            return d

        all_companies = [_enrich(main_data)] + [_enrich(p) for p in peers_data]

        # Nota de referência TTM
        st.markdown(
            '<p style="color:#52525b;font-size:12px;font-style:italic;margin:4px 0 12px 0;">'
            'Indicadores fundamentalistas: TTM (ultimos 12 meses) · Fonte: Yahoo Finance</p>',
            unsafe_allow_html=True,
        )

        _render_peer_table(ticker, all_companies)

        st.markdown(
            '<p style="font-size:11px;color:#52525b;margin-top:4px;">'
            '<span style="color:#10b981;">&#9632;</span> Acima da mediana do setor &nbsp;'
            '<span style="color:#ef4444;">&#9632;</span> Abaixo da mediana do setor &nbsp;'
            'Coluna em azul = empresa analisada</p>',
            unsafe_allow_html=True,
        )

        with st.spinner("Gerando analise comparativa..."):
            table_txt, medianas_txt = _format_comparison_for_llm(ticker, all_companies)
            prompt = PEER_COMPARISON_PROMPT.format(
                ticker=ticker,
                tabela=table_txt,
                medianas=medianas_txt,
            )
            try:
                analysis = provider.generate(prompt, system_prompt=SYSTEM_PROMPT)
                st.markdown("**Analise Comparativa**")
                st.markdown(analysis)
            except Exception:
                st.warning("Nao foi possivel gerar a analise comparativa.")


# ── Chart helper ─────────────────────────────────────────────────────────

def _render_price_chart(ticker: str) -> None:
    """Render interactive price chart with period selector and optional benchmarks."""
    import plotly.graph_objects as go

    PERIOD_LABELS = {
        "1mo": "1M",
        "3mo": "3M",
        "6mo": "6M",
        "1y": "1A",
        "2y": "2A",
        "5y": "5A",
    }

    # ── Header row: título | CDI checkbox | IBOV checkbox | período ──
    col_title, col_cdi, col_ibov, col_period = st.columns([2, 1, 1, 2])
    with col_title:
        st.markdown(
            f'<p style="font-size:16px;font-weight:600;color:#e4e4e7;margin:8px 0 0 0;'
            f'font-family:Plus Jakarta Sans,sans-serif;">'
            f'Cotacao — {ticker}</p>',
            unsafe_allow_html=True,
        )
    with col_cdi:
        show_cdi = st.checkbox("CDI", value=False, key=f"cdi_check_{ticker}")
    with col_ibov:
        show_ibov = st.checkbox("Ibovespa", value=False, key=f"ibov_check_{ticker}")
    with col_period:
        period_selected = st.segmented_control(
            "Periodo",
            options=list(PERIOD_LABELS.keys()),
            format_func=lambda x: PERIOD_LABELS[x],
            default="1y",
            label_visibility="collapsed",
            key=f"period_{ticker}",
        )
        period = period_selected or "1y"

    yahoo = YFinanceClient()

    # Histórico do ativo (sempre necessário)
    hist_key = f"hist_{ticker}_{period}"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = yahoo.get_history(ticker, period=period)
    hist = st.session_state[hist_key]

    if hist.empty:
        st.caption("Historico de precos nao disponivel.")
        return

    # Benchmarks (cachear por período)
    ibov_df = None
    cdi_df = None

    if show_ibov:
        ibov_key = f"ibov_{period}"
        if ibov_key not in st.session_state:
            st.session_state[ibov_key] = yahoo.get_benchmark_history("^BVSP", period)
        ibov_df = st.session_state[ibov_key]

    if show_cdi:
        cdi_key = f"cdi_{period}"
        if cdi_key not in st.session_state:
            st.session_state[cdi_key] = yahoo.get_cdi_history(period)
        cdi_df = st.session_state[cdi_key]

    # ── Montar figura ────────────────────────────────────────────────
    fig = go.Figure()
    comparative = show_cdi or show_ibov
    cdi_aligned = None  # inicializar para uso posterior no resumo

    if comparative:
        # Modo comparativo: tudo em variação % desde o início
        ativo_pct = ((hist["Close"] / hist["Close"].iloc[0]) - 1) * 100
        variacao = float(ativo_pct.iloc[-1])

        fig.add_trace(go.Scatter(
            x=ativo_pct.index,
            y=ativo_pct.values,
            mode="lines",
            name=ticker,
            line=dict(color="#3b82f6", width=2.5),
            hovertemplate=f"{ticker}: " + "%{y:.1f}%<extra></extra>",
        ))

        if show_ibov and ibov_df is not None and not ibov_df.empty:
            ibov_pct = ((ibov_df["Close"] / ibov_df["Close"].iloc[0]) - 1) * 100
            ibov_pct = ibov_pct.reindex(ativo_pct.index, method="ffill")
            fig.add_trace(go.Scatter(
                x=ibov_pct.index,
                y=ibov_pct.values,
                mode="lines",
                name="Ibovespa",
                line=dict(color="#f59e0b", width=1.5, dash="dot"),
                hovertemplate="Ibovespa: %{y:.1f}%<extra></extra>",
            ))

        if show_cdi and cdi_df is not None and not cdi_df.empty:
            import pandas as _pd
            cdi_series = cdi_df["cdi_acumulado"].copy()

            # Normalizar CDI para índice date-only (sem hora, sem timezone)
            cdi_series.index = _pd.to_datetime(cdi_series.index).normalize().tz_localize(None)

            # Normalizar índice do ativo para date-only também
            ativo_dates = _pd.to_datetime(ativo_pct.index).normalize().tz_localize(None)

            # Subtrair valor do CDI no primeiro dia do ativo (base = 0%)
            first_date = ativo_dates[0]
            cdi_base = cdi_series.asof(first_date)
            # Se asof retornar NaN (data antes do CDI), usar o primeiro valor disponível
            if _pd.isna(cdi_base):
                cdi_base = cdi_series.iloc[0]
            cdi_aligned = cdi_series - cdi_base

            # Reindex para os mesmos dias do ativo, preenchendo gaps com ffill
            cdi_aligned = cdi_aligned.reindex(ativo_dates, method="ffill")
            cdi_aligned.index = ativo_pct.index  # restaurar índice original para o plot
            fig.add_trace(go.Scatter(
                x=cdi_aligned.index,
                y=cdi_aligned.values,
                mode="lines",
                name="CDI",
                line=dict(color="#10b981", width=1.5, dash="dash"),
                hovertemplate="CDI: %{y:.1f}%<extra></extra>",
            ))

        fig.add_hline(y=0, line_color="rgba(255,255,255,0.12)", line_width=1)

        yaxis_cfg = dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            showline=False,
            color="#71717a",
            tickfont=dict(size=11),
            ticksuffix="%",
            zeroline=False,
        )
    else:
        # Modo simples: preço em R$ com fill
        variacao = float(((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100)

        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name=ticker,
            line=dict(color="#3b82f6", width=2),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.08)",
            hovertemplate="R$ %{y:,.2f}<extra></extra>",
        ))

        yaxis_cfg = dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            showline=False,
            color="#71717a",
            tickfont=dict(size=11),
            tickprefix="R$ ",
        )

    fig.update_layout(
        title=None,
        title_text="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#e4e4e7"),
        xaxis=dict(showgrid=False, showline=False, color="#71717a", tickfont=dict(size=11)),
        yaxis=yaxis_cfg,
        margin=dict(l=0, r=0, t=10, b=0),
        height=380,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1e1e2e", font_size=12, font_family="JetBrains Mono"),
        showlegend=comparative,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#a1a1aa"),
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    # ── Resumo de performance ────────────────────────────────────────
    if comparative:
        perf_parts = []

        cor = "#10b981" if variacao >= 0 else "#ef4444"
        sinal = "+" if variacao >= 0 else ""
        perf_parts.append(
            f'<span style="color:{cor};">{ticker}: {sinal}{variacao:.1f}%</span>'
        )

        if show_ibov and ibov_df is not None and not ibov_df.empty:
            ibov_var = float(((ibov_df["Close"].iloc[-1] / ibov_df["Close"].iloc[0]) - 1) * 100)
            cor_i = "#10b981" if ibov_var >= 0 else "#ef4444"
            sinal_i = "+" if ibov_var >= 0 else ""
            perf_parts.append(
                f'<span style="color:{cor_i};">IBOV: {sinal_i}{ibov_var:.1f}%</span>'
            )

        if show_cdi and cdi_aligned is not None and not cdi_aligned.dropna().empty:
            cdi_var = float(cdi_aligned.dropna().iloc[-1])
            perf_parts.append(f'<span style="color:#10b981;">CDI: +{cdi_var:.1f}%</span>')

        st.markdown(
            f'<p style="text-align:right;font-size:13px;font-family:JetBrains Mono,monospace;'
            f'margin-top:-10px;">{" &nbsp;|&nbsp; ".join(perf_parts)}</p>',
            unsafe_allow_html=True,
        )
    else:
        cor = "#10b981" if variacao >= 0 else "#ef4444"
        sinal = "+" if variacao >= 0 else ""
        st.markdown(
            f'<p style="text-align:right;color:{cor};font-size:13px;'
            f'font-family:JetBrains Mono,monospace;margin-top:-10px;">'
            f'{sinal}{variacao:.1f}% no periodo</p>',
            unsafe_allow_html=True,
        )

# ── Analysis flow ────────────────────────────────────────────────────────

STEP_LABELS = [
    "1/5  Buscando dados financeiros...",
    "2/5  Pesquisando perfil da empresa...",
    "3/5  Montando indicadores financeiros...",
    "4/5  Analisando noticias recentes...",
    "5/5  Gerando sintese de investimento...",
]

auto_analyze = st.session_state.pop("auto_analyze", False)

if analyze_btn or auto_analyze:
    # Validacoes
    if not active_key:
        st.error("Configure sua API key na sidebar antes de gerar analises.")
        st.stop()

    is_valid, ticker_or_msg = validate_ticker(ticker_input)
    if not is_valid:
        st.error(ticker_or_msg)
        st.stop()

    ticker = ticker_or_msg

    # Inicializa provider
    try:
        provider = get_provider(active_provider, api_key=active_key)
    except (ValueError, NotImplementedError) as e:
        st.error(str(e))
        st.stop()

    # Container de progresso
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    _step_counter = {"i": 0}

    def update_progress(_msg: str, pct: float) -> None:
        progress_bar.progress(min(pct, 1.0))
        idx = _step_counter["i"]
        if pct < 1.0 and idx < len(STEP_LABELS):
            status_text.markdown(
                f'<div class="step-item active">{STEP_LABELS[idx]}</div>',
                unsafe_allow_html=True,
            )
            _step_counter["i"] = idx + 1
        elif pct >= 1.0:
            status_text.markdown(
                '<div class="step-item active">Analise concluida.</div>',
                unsafe_allow_html=True,
            )

    # Executa analise
    t_start = time.time()
    with st.spinner("Iniciando analise..."):
        analyst = StockAnalyst(
            provider=provider,
            on_progress=update_progress,
            brapi_token=active_brapi_token or None,
        )
        result = analyst.analyze(ticker)
    elapsed = time.time() - t_start

    # Limpa progresso
    progress_bar.empty()
    status_text.empty()

    if not result.success:
        st.error(
            "Nao foi possivel gerar a analise. Verifique sua API key e tente novamente."
        )
        if result.errors:
            with st.expander("Detalhes dos erros"):
                for step, err in result.errors.items():
                    st.error(f"**{step}**: {err}")
        st.stop()

    # Salva resultado no session_state para o seletor de periodo nao re-rodar a analise
    st.session_state["last_result"] = result
    st.session_state["last_ticker"] = ticker
    st.session_state["last_elapsed"] = elapsed
    st.session_state["last_provider"] = active_provider

# ── Render report (from session_state or fresh) ──────────────────────────

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    ticker = st.session_state["last_ticker"]
    elapsed = st.session_state["last_elapsed"]
    active_provider = st.session_state.get("last_provider", active_provider)

    # Gera relatorio (markdown para export)
    report_md = generate_report(result, provider_name=active_provider)
    saved_path = save_report(report_md, ticker)

    # Status bar
    if result.errors:
        st.warning(
            f"Analise de **{ticker}** concluida com avisos. "
            f"Etapas com problemas: {', '.join(result.errors.keys())}"
        )
        with st.expander("Detalhes dos avisos"):
            for step, err in result.errors.items():
                st.warning(f"**{step}**: {err}")
    else:
        st.markdown(
            f'<div class="report-card fade-in" style="display:flex;align-items:center;gap:12px;">'
            f'{icon("check_circle")}'
            f'<span style="font-weight:600;">Analise de {ticker} concluida com sucesso</span>'
            f'<span class="gen-timer" style="margin-left:auto;">'
            f'{icon("clock", size=14)} {elapsed:.1f}s</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Report header with logo ──────────────────────────────────────────
    logo_url = result.brapi_data.get("logo_url", "") if result.brapi_data else ""
    date_str = datetime.now().strftime("%d/%m/%Y as %H:%M")

    render_report_header(
        ticker=ticker,
        company_name=result.company_name or ticker,
        logo_url=logo_url,
        date_str=date_str,
        provider_name=active_provider,
    )

    # ── Data cards ───────────────────────────────────────────────────────
    if result.brapi_data:
        render_data_cards(result.brapi_data)
        data_level = result.brapi_data.get("_data_level", "minimal")
        if data_level != "full":
            st.caption(
                "Dados fundamentalistas limitados. Para dados completos, "
                "use PETR4, MGLU3, VALE3 ou ITUB4, ou configure um plano brapi.dev Pro."
            )

    # ── Price chart ──────────────────────────────────────────────────────
    _render_price_chart(ticker)

    # ── Section 1: Company profile ───────────────────────────────────────
    with st.expander("Visao Geral da Empresa", expanded=True):
        if result.profile:
            st.markdown(result.profile)
        else:
            st.caption("Informacao nao disponivel.")

    # ── Section 2: Financial indicators ──────────────────────────────────
    with st.expander("Indicadores Financeiros", expanded=True):
        st.markdown(
            f'<p style="color:#71717a;font-size:12px;font-style:italic;margin:4px 0 12px 0;'
            f'font-family:Plus Jakarta Sans,sans-serif;">'
            f'Dados fundamentalistas: TTM (ultimos 12 meses) \u00b7 '
            f'Cotacao: {datetime.now().strftime("%d/%m/%Y")} \u00b7 Fonte: Yahoo Finance</p>',
            unsafe_allow_html=True,
        )
        if result.financials:
            st.markdown(result.financials, unsafe_allow_html=True)
            st.markdown(
                '<p style="color:#52525b;font-size:11px;font-style:italic;margin:8px 0 0 0;">'
                'TTM = Trailing Twelve Months (ultimos 12 meses). YoY = Year over Year (variacao anual). '
                'Dados podem apresentar divergencias pontuais. Para decisoes de investimento, '
                'consulte os demonstrativos oficiais no site de RI da empresa.</p>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Informacao nao disponivel.")

    # ── Section 3: News with badges ──────────────────────────────────────
    with st.expander("Noticias Recentes", expanded=True):
        if result.news:
            news_html = render_news_with_badges(result.news)
            st.markdown(news_html, unsafe_allow_html=True)
        else:
            st.caption("Informacao nao disponivel.")

    # ── Section 4: Synthesis with bias badge ─────────────────────────────
    with st.expander("Sintese de Investimento", expanded=True):
        if result.synthesis:
            bias = parse_bias(result.synthesis)
            badge_html = render_bias_badge(bias)
            st.markdown(badge_html, unsafe_allow_html=True)
            st.markdown(result.synthesis, unsafe_allow_html=True)
        else:
            st.caption("Informacao nao disponivel.")

    # ── Section 5: Peer comparison (on-demand) ───────────────────────────
    st.markdown("---")
    with st.expander("Comparacao Setorial", expanded=False):
        provider = get_provider(active_provider, api_key=active_key)
        _render_peer_comparison_section(ticker, result.brapi_data, provider)

    # ── Export buttons ───────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Copiar Markdown",
            data=report_md,
            file_name=f"{ticker}_analise.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        html_report = report_to_html(report_md)
        st.download_button(
            label="Download HTML",
            data=html_report,
            file_name=f"{ticker}_analise.html",
            mime="text/html",
            use_container_width=True,
        )

    # Data source indicator
    data_source = result.brapi_data.get("_data_source", "web") if result.brapi_data else "web"
    source_label = {
        "yfinance": "Yahoo Finance via yfinance",
        "brapi": "brapi.dev",
    }.get(data_source, "busca web")
    st.caption(
        f"Dados: {source_label} | Relatorio salvo em: `{saved_path}`"
    )
    render_footer(config.APP_VERSION)

# ── Empty state ──────────────────────────────────────────────────────────

elif not ticker_input:
    render_empty_state()

    # Ticker chips clicáveis
    _CHIPS = ["VALE3", "PETR4", "WEGE3", "ITUB4", "BBAS3", "RENT3"]
    _chip_cols = st.columns(len(_CHIPS))
    for _col, _t in zip(_chip_cols, _CHIPS):
        with _col:
            if st.button(_t, key=f"chip_{_t}", use_container_width=True):
                st.session_state["chip_ticker"] = _t
                st.session_state["auto_analyze"] = True
                st.rerun()

    render_footer(config.APP_VERSION)
