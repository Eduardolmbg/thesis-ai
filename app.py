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
    col_title, col_cdi, col_ibov, col_period = st.columns([3, 0.6, 0.8, 0.8])
    with col_title:
        st.markdown(
            f'<div class="report-card fade-in chart-title-card">'
            f'<h2>{icon("trending_up", color=COLORS["accent"])} Cotacao — {ticker}</h2>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_cdi:
        st.markdown('<div class="chart-period-wrapper">', unsafe_allow_html=True)
        show_cdi = st.checkbox("CDI", value=False, key=f"cdi_check_{ticker}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_ibov:
        st.markdown('<div class="chart-period-wrapper">', unsafe_allow_html=True)
        show_ibov = st.checkbox("Ibovespa", value=False, key=f"ibov_check_{ticker}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_period:
        st.markdown('<div class="chart-period-wrapper">', unsafe_allow_html=True)
        period = st.selectbox(
            "Periodo",
            options=list(PERIOD_LABELS.keys()),
            format_func=lambda x: PERIOD_LABELS[x],
            index=3,
            label_visibility="collapsed",
            key=f"period_{ticker}",
        )
        st.markdown('</div>', unsafe_allow_html=True)

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
        if result.financials:
            st.markdown(result.financials, unsafe_allow_html=True)
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
