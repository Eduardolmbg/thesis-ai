"""thesis-ai — AI-Powered Equity Research (Streamlit app)."""

from __future__ import annotations

import time

import streamlit as st

import config
from providers import get_provider
from agents.stock_analyst import StockAnalyst
from reports.generator import generate_report, save_report, report_to_html
from utils.formatting import validate_ticker
from utils.theme import (
    inject_css,
    render_header,
    render_sidebar_brand,
    render_empty_state,
    render_footer,
    icon,
    COLORS,
)

# ── Page config ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=None,
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

    provider_name = st.selectbox(
        "LLM Provider",
        options=["gemini", "openai", "groq"],
        index=0,
        help="Selecione o provedor de LLM. Apenas Gemini esta implementado no momento.",
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
        '<div class="sidebar-section-title">brapi.dev Token</div>',
        unsafe_allow_html=True,
    )

    brapi_token = st.text_input(
        "brapi.dev Token",
        type="password",
        value=config.BRAPI_TOKEN,
        help="Gratuito em brapi.dev. Sem token, funciona para PETR4, MGLU3, VALE3, ITUB4.",
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
        f"**thesis-ai** v{config.APP_VERSION}\n\n"
        "Agente de IA que gera relatorios de analise "
        "fundamentalista de acoes brasileiras.",
        unsafe_allow_html=False,
    )
    st.markdown(
        f'<div class="disclaimer">'
        f"{icon('alert_triangle', size=16)} "
        f"Este sistema nao constitui recomendacao de investimento. "
        f"Faca sua propria analise."
        f"</div>",
        unsafe_allow_html=True,
    )

# Resolve provider/key from session or defaults
active_provider = st.session_state.get("provider_name", provider_name)
active_key = st.session_state.get("api_key", api_key)
active_brapi_token = st.session_state.get("brapi_token", brapi_token)

# ── Main area ────────────────────────────────────────────────────────────

render_header()

ticker_input = st.text_input(
    "Ticker da acao",
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

# ── Analysis flow ────────────────────────────────────────────────────────

STEP_LABELS = [
    "1/5  Buscando dados na brapi.dev...",
    "2/5  Pesquisando perfil da empresa...",
    "3/5  Montando indicadores financeiros...",
    "4/5  Analisando noticias recentes...",
    "5/5  Gerando sintese de investimento...",
]

if analyze_btn:
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

    # Gera relatorio
    report_md = generate_report(result, provider_name=active_provider)

    # Salva no disco
    saved_path = save_report(report_md, ticker)

    # Status com timer
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

    # ── Render report in cards ───────────────────────────────────────────
    st.markdown('<div class="fade-in fade-in-delay-1">', unsafe_allow_html=True)

    # Section 1: Company profile
    st.markdown(
        f'<div class="report-card">'
        f'<h2>{icon("building", color=COLORS["accent"])} Visao Geral da Empresa</h2>'
        f"</div>",
        unsafe_allow_html=True,
    )
    if result.profile:
        st.markdown(result.profile)
    else:
        st.caption("Informacao nao disponivel.")

    # Section 2: Financial indicators
    st.markdown(
        f'<div class="report-card">'
        f'<h2>{icon("bar_chart", color=COLORS["accent"])} Indicadores Financeiros</h2>'
        f"</div>",
        unsafe_allow_html=True,
    )
    if result.financials:
        st.markdown(result.financials, unsafe_allow_html=True)
    else:
        st.caption("Informacao nao disponivel.")

    # Section 3: News
    st.markdown(
        f'<div class="report-card">'
        f'<h2>{icon("newspaper", color=COLORS["accent"])} Noticias Recentes</h2>'
        f"</div>",
        unsafe_allow_html=True,
    )
    if result.news:
        st.markdown(result.news, unsafe_allow_html=True)
    else:
        st.caption("Informacao nao disponivel.")

    # Section 4: Investment synthesis
    st.markdown(
        f'<div class="report-card">'
        f'<h2>{icon("brain", color=COLORS["accent"])} Sintese de Investimento</h2>'
        f"</div>",
        unsafe_allow_html=True,
    )
    if result.synthesis:
        st.markdown(result.synthesis, unsafe_allow_html=True)
    else:
        st.caption("Informacao nao disponivel.")

    st.markdown("</div>", unsafe_allow_html=True)

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

    st.caption(f"Relatorio salvo em: `{saved_path}`")

    render_footer(config.APP_VERSION)

# ── Empty state ──────────────────────────────────────────────────────────

elif not ticker_input:
    render_empty_state()
    render_footer(config.APP_VERSION)
