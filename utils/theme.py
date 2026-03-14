"""Dark fintech theme — CSS, SVG icons, and styled components."""

from __future__ import annotations


# ── Colors ───────────────────────────────────────────────────────────────

COLORS = {
    "bg": "#0a0a0f",
    "surface": "#12121a",
    "border": "#1e1e2e",
    "accent": "#00d4aa",
    "accent_dim": "rgba(0,212,170,0.12)",
    "text": "#e4e4e7",
    "text_secondary": "#71717a",
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#f59e0b",
    "white": "#ffffff",
}

# ── SVG Icons (Lucide-style, 20px, stroke-width 1.5) ────────────────────

_ICON_STYLE = 'xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"'

ICONS = {
    "trending_up": f'<svg {_ICON_STYLE}><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "search": f'<svg {_ICON_STYLE}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "bar_chart": f'<svg {_ICON_STYLE}><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    "clipboard": f'<svg {_ICON_STYLE}><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg>',
    "download": f'<svg {_ICON_STYLE}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "check_circle": f'<svg {_ICON_STYLE} stroke="#10b981"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "alert_triangle": f'<svg {_ICON_STYLE} stroke="#f59e0b"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "building": f'<svg {_ICON_STYLE}><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
    "newspaper": f'<svg {_ICON_STYLE}><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>',
    "brain": f'<svg {_ICON_STYLE}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>',
    "shield": f'<svg {_ICON_STYLE}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "target": f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "zap": f'<svg {_ICON_STYLE}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "clock": f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "arrow_right": f'<svg {_ICON_STYLE}><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "chevron_right": f'<svg {_ICON_STYLE} width="16" height="16"><polyline points="9 18 15 12 9 6"/></svg>',
    "info": f'<svg {_ICON_STYLE}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "external_link": f'<svg {_ICON_STYLE} width="14" height="14"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
}


def icon(name: str, size: int = 20, color: str | None = None) -> str:
    """Return an SVG icon string, optionally resized / recolored."""
    svg = ICONS.get(name, "")
    if not svg:
        return ""
    if size != 20:
        svg = svg.replace('width="20"', f'width="{size}"').replace(
            'height="20"', f'height="{size}"'
        )
    if color:
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return svg


# ── CSS ──────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── Root / global ──────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: %(bg)s !important;
    color: %(text)s !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"] {
    background-color: %(bg)s !important;
}

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: %(surface)s !important;
    border-right: 1px solid %(border)s !important;
}
section[data-testid="stSidebar"] * {
    color: %(text)s !important;
}

/* ── Text ───────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    color: %(text)s !important;
}

p, li, span, div {
    color: %(text)s !important;
}

small, .stCaption, [data-testid="stCaptionContainer"] {
    color: %(text_secondary)s !important;
}

/* ── Inputs ─────────────────────────────────────────────── */
input[type="text"], input[type="password"],
[data-testid="stTextInput"] input {
    background-color: %(surface)s !important;
    border: 1px solid %(border)s !important;
    color: %(text)s !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 8px !important;
}
input::placeholder {
    color: %(text_secondary)s !important;
    opacity: 0.6 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: %(accent)s !important;
    box-shadow: 0 0 0 1px %(accent)s !important;
}

/* ── Selectbox ──────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background-color: %(surface)s !important;
    border-color: %(border)s !important;
}

/* ── Buttons ────────────────────────────────────────────── */
[data-testid="stBaseButton-primary"],
button[kind="primary"] {
    background-color: %(accent)s !important;
    color: #0a0a0f !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stBaseButton-primary"]:hover,
button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stBaseButton-secondary"],
button[kind="secondary"],
[data-testid="stDownloadButton"] button {
    background-color: transparent !important;
    color: %(text)s !important;
    border: 1px solid %(border)s !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stBaseButton-secondary"]:hover,
button[kind="secondary"]:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: %(accent)s !important;
    color: %(accent)s !important;
}

/* ── Progress bar ───────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background-color: %(border)s !important;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, %(accent)s, #3b82f6) !important;
}

/* ── Alerts ─────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background-color: %(surface)s !important;
    border-radius: 8px !important;
}

/* ── Divider ────────────────────────────────────────────── */
[data-testid="stHorizontalBlock"] hr,
hr {
    border-color: %(border)s !important;
}

/* ── Expander ───────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: %(surface)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 8px !important;
}

/* ── Markdown tables ────────────────────────────────────── */
table {
    width: 100%% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
thead tr th {
    background-color: #1a1a2e !important;
    color: %(text)s !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    padding: 12px 16px !important;
    border-bottom: 2px solid %(accent)s !important;
}
tbody tr td {
    background-color: %(surface)s !important;
    color: %(text)s !important;
    padding: 10px 16px !important;
    border-bottom: 1px solid %(border)s !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
}
tbody tr:nth-child(even) td {
    background-color: rgba(18,18,26,0.7) !important;
}
tbody tr:hover td {
    background-color: rgba(0,212,170,0.05) !important;
}

/* ── Card component ─────────────────────────────────────── */
.report-card {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 12px;
    padding: 16px 32px;
    margin-bottom: 20px;
    animation: fadeSlideIn 0.4s ease-out both;
}
.chart-title-card {
    margin-bottom: 10px !important;
}
.chart-period-wrapper {
    display: flex;
    align-items: center;
    height: 100%%;
    padding-top: 4px;
}
.report-card h2 {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    border-bottom: none !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    color: %(text)s !important;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 14px;
    border-bottom: 1px solid %(border)s;
    margin-bottom: 18px !important;
}

/* ── Badges ─────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    vertical-align: middle;
}
.badge-positive { background: rgba(16,185,129,0.15); color: #10b981; }
.badge-negative { background: rgba(239,68,68,0.15); color: #ef4444; }
.badge-neutral  { background: rgba(245,158,11,0.15); color: #f59e0b; }

.badge-lg {
    font-size: 0.95rem;
    padding: 6px 20px;
    border-radius: 8px;
}

/* ── Ticker chips ───────────────────────────────────────── */
.ticker-chip {
    display: inline-block;
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    padding: 8px 18px;
    margin: 4px 6px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    color: %(accent)s;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.ticker-chip:hover {
    background: %(accent_dim)s;
    border-color: %(accent)s;
    transform: translateY(-1px);
}

/* ── Step indicator ─────────────────────────────────────── */
.step-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: %(text_secondary)s;
    padding: 4px 0;
}
.step-item.active {
    color: %(accent)s;
    font-weight: 600;
}

/* ── Header gradient line ───────────────────────────────── */
.gradient-line {
    height: 2px;
    background: linear-gradient(90deg, %(accent)s, #3b82f6, transparent);
    border: none;
    margin: 16px 0 28px 0;
    border-radius: 1px;
}

/* ── Logo ───────────────────────────────────────────────── */
.logo-title {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700;
    font-size: 2.2rem;
    color: %(text)s;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;
    padding: 0;
}
.logo-title .accent {
    color: %(accent)s;
}
.logo-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: %(text_secondary)s;
    font-weight: 400;
    margin-top: 4px;
    letter-spacing: 0.02em;
}

/* ── How-it-works steps ─────────────────────────────────── */
.how-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 18px 0;
    border-bottom: 1px solid %(border)s;
}
.how-step:last-child { border-bottom: none; }
.how-step-num {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1.1rem;
    color: %(accent)s;
    min-width: 28px;
}
.how-step-text {
    color: %(text)s;
    font-size: 0.95rem;
    line-height: 1.5;
}
.how-step-text strong { color: %(accent)s; }

/* ── Footer ─────────────────────────────────────────────── */
.footer {
    text-align: center;
    padding: 32px 0 16px 0;
    color: %(text_secondary)s;
    font-size: 0.78rem;
    border-top: 1px solid %(border)s;
    margin-top: 40px;
}

/* ── Fade-in animation ──────────────────────────────────── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeSlideIn 0.5s ease-out both;
}
.fade-in-delay-1 { animation-delay: 0.1s; }
.fade-in-delay-2 { animation-delay: 0.2s; }
.fade-in-delay-3 { animation-delay: 0.3s; }
.fade-in-delay-4 { animation-delay: 0.4s; }

/* ── Sidebar branding ──────────────────────────────────── */
.sidebar-brand {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 1.2rem;
    color: %(text)s;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 8px;
    margin-bottom: 4px;
}
.sidebar-brand .accent { color: %(accent)s; }

.sidebar-section-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: %(text_secondary)s;
    margin: 20px 0 8px 0;
}

/* ── Disclaimer ─────────────────────────────────────────── */
.disclaimer {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.15);
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.8rem;
    color: %(text_secondary)s;
    margin-top: 12px;
    line-height: 1.5;
}

/* ── Generation timer ───────────────────────────────────── */
.gen-timer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: %(text_secondary)s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* ── Data cards grid ────────────────────────────────────── */
.data-cards-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 20px 0 30px 0;
}
@media (max-width: 768px) {
    .data-cards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
.data-card {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.data-card-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
}
.data-card-icon.market  { background: rgba(59,130,246,0.15); color: #3b82f6; }
.data-card-icon.profit  { background: rgba(16,185,129,0.15); color: #10b981; }
.data-card-icon.risk    { background: rgba(245,158,11,0.15); color: #f59e0b; }
.data-card-icon.growth  { background: rgba(139,92,246,0.15); color: #8b5cf6; }
.data-card-label {
    font-size: 11px;
    font-weight: 500;
    color: %(text_secondary)s !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.data-card-value {
    font-size: 22px;
    font-weight: 700;
    color: %(text)s !important;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.2;
}
.data-card-detail {
    font-size: 12px;
    color: %(text_secondary)s !important;
}
.data-card-detail.positive { color: #10b981 !important; }
.data-card-detail.negative { color: #ef4444 !important; }

/* ── Report header ─────────────────────────────────────── */
.report-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
    animation: fadeSlideIn 0.4s ease-out both;
}
.report-header img {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    background: %(surface)s;
    padding: 4px;
    border: 1px solid %(border)s;
}
.report-header-text h1 {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 1.6rem !important;
    line-height: 1.3 !important;
}
.report-header-meta {
    color: %(text_secondary)s !important;
    font-size: 0.78rem;
}

/* ── Viés badge (large) ────────────────────────────────── */
.bias-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    font-family: 'DM Sans', sans-serif;
    margin-bottom: 12px;
}
.bias-badge.positive { background: #10b981; color: #fff; }
.bias-badge.negative { background: #ef4444; color: #fff; }
.bias-badge.neutral  { background: #f59e0b; color: #000; }

/* ── News item ─────────────────────────────────────────── */
.news-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 10px;
    line-height: 1.5;
}
.news-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    margin-top: 2px;
    flex-shrink: 0;
}
.news-badge.positive { background: #10b981; color: #fff; }
.news-badge.negative { background: #ef4444; color: #fff; }
.news-badge.neutral  { background: #f59e0b; color: #000; }
.news-text {
    color: %(text)s !important;
    font-size: 14px;
}
.news-link {
    color: %(text_secondary)s !important;
    text-decoration: none !important;
    transition: color 0.2s;
    vertical-align: middle;
    margin-left: 4px;
}
.news-link:hover {
    color: %(accent)s !important;
}
.news-link svg {
    vertical-align: middle;
}

/* ── Misc ───────────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] a {
    color: %(accent)s !important;
}
</style>
""" % COLORS


def inject_css() -> None:
    """Inject the global CSS into the Streamlit page."""
    import streamlit as st

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Component helpers ────────────────────────────────────────────────────

def render_header() -> None:
    """Render the app header with logo and gradient line."""
    import streamlit as st

    st.markdown(
        f"""
        <div class="fade-in">
            <div class="logo-title">
                {icon("trending_up", color=COLORS["accent"])}
                thesis<span class="accent">-ai</span>
            </div>
            <div class="logo-subtitle">AI-Powered Equity Research</div>
            <div class="gradient-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Render sidebar branding."""
    import streamlit as st

    st.markdown(
        f"""
        <div class="sidebar-brand">
            {icon("trending_up", size=18, color=COLORS["accent"])}
            thesis<span class="accent">-ai</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    """Render the empty state before any analysis is generated."""
    import streamlit as st

    st.markdown(
        f"""
        <div class="report-card fade-in" style="text-align:center;padding:48px 32px;">
            <div style="margin-bottom:24px;">
                {icon("search", size=40, color=COLORS["text_secondary"])}
            </div>
            <div style="font-size:1.15rem;font-weight:500;color:{COLORS["text"]};margin-bottom:8px;">
                Digite um ticker acima para iniciar a analise
            </div>
            <div style="font-size:0.9rem;color:{COLORS["text_secondary"]};">
                Exemplos de tickers populares:
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ticker chips
    st.markdown(
        f"""
        <div style="text-align:center;margin-bottom:32px;" class="fade-in fade-in-delay-1">
            <span class="ticker-chip">VALE3</span>
            <span class="ticker-chip">PETR4</span>
            <span class="ticker-chip">WEGE3</span>
            <span class="ticker-chip">ITUB4</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # How it works
    st.markdown(
        f"""
        <div class="report-card fade-in fade-in-delay-2">
            <h2>{icon("info", color=COLORS["accent"])} Como funciona</h2>
            <div class="how-step">
                <span class="how-step-num">01</span>
                <span class="how-step-text"><strong>Configure</strong> sua API key na sidebar — obtenha gratuitamente no Google AI Studio</span>
            </div>
            <div class="how-step">
                <span class="how-step-num">02</span>
                <span class="how-step-text"><strong>Digite</strong> o ticker de uma acao brasileira (ex: WEGE3, PETR4, VALE3)</span>
            </div>
            <div class="how-step">
                <span class="how-step-num">03</span>
                <span class="how-step-text"><strong>Receba</strong> um relatorio completo de analise fundamentalista gerado por IA</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(version: str) -> None:
    """Render the app footer."""
    import streamlit as st

    st.markdown(
        f"""
        <div class="footer">
            thesis-ai v{version} &middot; Nao constitui recomendacao de investimento
        </div>
        """,
        unsafe_allow_html=True,
    )


def sentiment_badge(sentiment: str, large: bool = False) -> str:
    """Return an HTML badge for a sentiment string."""
    s = sentiment.strip().upper()
    size_class = "badge badge-lg" if large else "badge"
    if "POSITIV" in s:
        return f'<span class="{size_class} badge-positive">POSITIVO</span>'
    if "NEGATIV" in s:
        return f'<span class="{size_class} badge-negative">NEGATIVO</span>'
    return f'<span class="{size_class} badge-neutral">NEUTRO</span>'


# ── Data cards ───────────────────────────────────────────────────────────

def _card_html(icon_text: str, icon_class: str, label: str, value: str, detail: str = "") -> str:
    """Build HTML for a single data card."""
    detail_html = ""
    if detail:
        # Detect positive/negative for coloring
        css_class = "data-card-detail"
        if detail.startswith("+") or detail.startswith("Var: +"):
            css_class += " positive"
        elif detail.startswith("-") or detail.startswith("Var: -"):
            css_class += " negative"
        detail_html = f'<div class="{css_class}">{detail}</div>'

    return (
        f'<div class="data-card">'
        f'<div class="data-card-icon {icon_class}">{icon_text}</div>'
        f'<div class="data-card-label">{label}</div>'
        f'<div class="data-card-value">{value}</div>'
        f'{detail_html}'
        f'</div>'
    )


def render_data_cards(data: dict) -> None:
    """Render a grid of financial data cards from structured data."""
    import streamlit as st
    from utils.formatting import (
        format_market_cap, format_currency, format_percent, format_multiple,
        _is_number,
    )

    def _val(key: str) -> bool:
        return _is_number(data.get(key))

    # Row 1 — Mercado
    price = format_currency(data.get("preco_atual")) if _val("preco_atual") else "N/D"
    var = data.get("variacao_dia")
    var_detail = ""
    if _is_number(var):
        sign = "+" if var >= 0 else ""
        var_detail = f"Var: {sign}{var:.2f}%"

    mcap = format_market_cap(data.get("market_cap"))
    pl = format_multiple(data.get("preco_lucro")) if _val("preco_lucro") else "N/D"
    ev_ebitda = format_multiple(data.get("ev_ebitda")) if _val("ev_ebitda") else "N/D"

    # Row 2 — Rentabilidade
    roe = format_percent(data.get("roe")) if _val("roe") else "N/D"
    me = format_percent(data.get("margem_ebitda")) if _val("margem_ebitda") else "N/D"
    ml = format_percent(data.get("margem_lucro")) if _val("margem_lucro") else "N/D"
    dy = format_percent(data.get("dividend_yield")) if _val("dividend_yield") else "N/D"

    # Row 3 — Endividamento e Crescimento
    de = data.get("divida_equity")
    de_str = format_percent(de, is_ratio=False) if _is_number(de) else "N/D"

    ll = data.get("lucro_liquido")
    ll_str = format_currency(ll) if _is_number(ll) else "N/D"
    ll_detail = ""
    ll_hist = data.get("lucro_liquido_historico") or {}
    if _is_number(ll) and len(ll_hist) >= 2:
        years = sorted(ll_hist.keys(), reverse=True)
        if len(years) >= 2:
            curr = ll_hist[years[0]]
            prev = ll_hist[years[1]]
            if _is_number(curr) and _is_number(prev) and prev != 0:
                yoy = ((curr - prev) / abs(prev)) * 100
                sign = "+" if yoy >= 0 else ""
                ll_detail = f"{sign}{yoy:.1f}% YoY"

    fcf = data.get("free_cashflow")
    fcf_str = format_currency(fcf) if _is_number(fcf) else "N/D"

    cr = data.get("crescimento_receita")
    if _is_number(cr):
        sign = "+" if cr >= 0 else ""
        cr_str = f"{sign}{cr*100:.1f}%"
    else:
        cr_str = "N/D"

    row1 = (
        _card_html("R$", "market", "Preco", price, var_detail)
        + _card_html("MC", "market", "Market Cap", mcap)
        + _card_html("P/L", "market", "Preco/Lucro", pl)
        + _card_html("EV", "market", "EV/EBITDA", ev_ebitda)
    )
    row2 = (
        _card_html("ROE", "profit", "Ret. s/ Patrimonio", roe)
        + _card_html("ME", "profit", "Margem EBITDA", me)
        + _card_html("ML", "profit", "Margem Liquida", ml)
        + _card_html("DY", "profit", "Dividend Yield", dy)
    )
    row3 = (
        _card_html("LL", "profit", "Lucro Liquido", ll_str, ll_detail)
        + _card_html("D/E", "risk", "Div./Equity", de_str)
        + _card_html("FCF", "growth", "Free Cash Flow", fcf_str)
        + _card_html("CR", "growth", "Cresc. Receita", cr_str)
    )

    html = (
        f'<div class="data-cards-grid fade-in fade-in-delay-1">{row1}</div>'
        f'<div class="data-cards-grid fade-in fade-in-delay-2">{row2}</div>'
        f'<div class="data-cards-grid fade-in fade-in-delay-3">{row3}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_report_header(
    ticker: str,
    company_name: str,
    logo_url: str,
    date_str: str,
    provider_name: str,
) -> None:
    """Render the report title with company logo."""
    import streamlit as st

    logo_html = ""
    if logo_url:
        logo_html = (
            f'<img src="{logo_url}" alt="{ticker}" '
            f'onerror="this.style.display=\'none\'">'
        )

    st.markdown(
        f'<div class="report-header">'
        f'{logo_html}'
        f'<div class="report-header-text">'
        f'<h1>Analise: {company_name} ({ticker})</h1>'
        f'<span class="report-header-meta">'
        f'Gerado em {date_str} por thesis-ai | Provider: {provider_name}'
        f'</span>'
        f'</div>'
        f'</div>'
        f'<div class="gradient-line"></div>',
        unsafe_allow_html=True,
    )


# ── Sentiment parsing ────────────────────────────────────────────────────

import re as _re


def parse_bias(synthesis_text: str) -> str:
    """Parse the bias (POSITIVO/NEGATIVO/NEUTRO) from synthesis output.

    Searches for patterns like 'VIES: POSITIVO', 'Vies Geral: NEGATIVO',
    or just the word after known markers.
    """
    text_upper = synthesis_text.upper()

    # Pattern 1: "VIES: POSITIVO" or "VIÉS: NEUTRO"
    match = _re.search(r'VI[EÉ]S[:\s]+\[?(POSITIVO|NEGATIVO|NEUTRO)\]?', text_upper)
    if match:
        return match.group(1)

    # Pattern 2: standalone after "**Viés" markdown
    match = _re.search(r'\*\*VI[EÉ]S.*?\*\*[:\s]*(POSITIVO|NEGATIVO|NEUTRO)', text_upper)
    if match:
        return match.group(1)

    # Pattern 3: first occurrence of the keyword
    for keyword in ["POSITIVO", "NEGATIVO", "NEUTRO"]:
        if keyword in text_upper[:300]:
            return keyword

    return "NEUTRO"


def render_bias_badge(bias: str) -> str:
    """Return HTML for the large bias badge."""
    b = bias.strip().upper()
    if "POSITIV" in b:
        return '<span class="bias-badge positive">POSITIVO</span>'
    if "NEGATIV" in b:
        return '<span class="bias-badge negative">NEGATIVO</span>'
    return '<span class="bias-badge neutral">NEUTRO</span>'


def render_news_with_badges(news_text: str) -> str:
    """Parse news text with [POSITIVA]/[NEGATIVA]/[NEUTRA] tags and render with badges."""
    if not news_text:
        return ""

    lines = news_text.strip().split("\n")
    items: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Strip leading markdown bullets/numbers
        clean = _re.sub(r'^[\d]+[\.\)]\s*', '', line)
        clean = _re.sub(r'^[-\*]\s*', '', clean)

        # Match sentiment tag
        match = _re.match(r'\[?(POSITIVA|NEGATIVA|NEUTRA)\]?\s*[:\-–]?\s*(.*)', clean, _re.IGNORECASE)
        if match:
            sentiment = match.group(1).upper()
            text = match.group(2).strip()
            if not text:
                continue

            if "POSITIV" in sentiment:
                badge_class = "positive"
                badge_text = "POSITIVA"
            elif "NEGATIV" in sentiment:
                badge_class = "negative"
                badge_text = "NEGATIVA"
            else:
                badge_class = "neutral"
                badge_text = "NEUTRA"

            # Extract URL if present (format: "summary | URL: https://...")
            link_html = ""
            url_match = _re.search(r'\|\s*URL:\s*(https?://\S+)', text)
            if url_match:
                url = url_match.group(1).rstrip(".,;)")
                text = text[:url_match.start()].strip()
                link_html = (
                    f' <a href="{url}" target="_blank" rel="noopener noreferrer" '
                    f'class="news-link" title="Abrir fonte">'
                    f'{icon("external_link", size=14)}</a>'
                )

            items.append(
                f'<div class="news-item">'
                f'<span class="news-badge {badge_class}">{badge_text}</span>'
                f'<span class="news-text">{text}{link_html}</span>'
                f'</div>'
            )
        elif clean and len(clean) > 10:
            # Lines without tags — render as plain text if substantial
            # Skip section headers like "Positivas:", "Negativas:"
            if _re.match(r'^(positiva|negativa|neutra|noticia)s?[:\s]*$', clean, _re.IGNORECASE):
                continue
            items.append(
                f'<div class="news-item">'
                f'<span class="news-text">{clean}</span>'
                f'</div>'
            )

    return "\n".join(items) if items else news_text
