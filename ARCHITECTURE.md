# Verto — Documentacao Tecnica

## Arquitetura

```
Verto/
├── app.py                       # Interface Streamlit (dark theme)
├── config.py                    # Configuracoes, env vars, persistencia .env
├── providers/                   # Abstracao de LLM providers
│   ├── base.py                  #   Classe abstrata BaseLLMProvider
│   ├── gemini.py                #   Google Gemini (com Search grounding)
│   ├── groq.py                  #   Groq (Llama 3.3 70B)
│   └── openai.py                #   OpenAI GPT (stub)
├── research/                    # Modulo de pesquisa e dados
│   ├── yahoo_finance.py         #   Yahoo Finance via yfinance (fonte primaria)
│   ├── brapi.py                 #   brapi.dev API client (fallback)
│   ├── web_search.py            #   Busca web (Gemini Search / DuckDuckGo)
│   └── peers.py                 #   Mapeamento de peers brasileiros por setor
├── agents/                      # Orquestracao da analise
│   ├── stock_analyst.py         #   Agente principal (5 etapas)
│   └── prompts.py               #   Prompts otimizados para analise
├── reports/                     # Geracao de relatorios
│   ├── generator.py             #   Gerador Markdown/HTML
│   └── templates/               #   Templates de relatorio
├── utils/                       # Helpers
│   ├── theme.py                 #   Dark theme, CSS, SVG icons, componentes visuais
│   └── formatting.py            #   Validacao de ticker, formatacao financeira
└── output/                      # Relatorios gerados
```

## Stack

| Componente | Tecnologia |
|---|---|
| Interface | Streamlit + CSS customizado (dark theme) |
| LLM | Google Gemini / Groq (Llama 3.3) |
| Dados financeiros | Yahoo Finance (yfinance) + brapi.dev (fallback) |
| Graficos | Plotly |
| Busca web | Google Search grounding (Gemini) / DuckDuckGo |
| Icons | SVG inline (Lucide-style) |

## Providers

| Provider | Status | Search nativo | Modelo padrao |
|---|---|---|---|
| Gemini | Implementado | Google Search grounding | gemini-2.5-flash |
| Groq | Implementado | DuckDuckGo (fallback) | llama-3.3-70b-versatile |
| OpenAI | Stub | - | - |

## Dados financeiros

**Fonte primaria: Yahoo Finance (yfinance)** — gratuito, sem token, sem limite.

**Fallback: brapi.dev** — fallback progressivo em 3 niveis de modulos.

| Categoria | Indicadores |
|---|---|
| Mercado | Preco, Market Cap, Volume, Max/Min 52 semanas |
| Valuation | P/L, P/VP, EV/EBITDA, PEG Ratio |
| Rentabilidade | ROE, ROA |
| Margens | EBITDA, Bruta, Operacional, Liquida |
| Financeiro | Receita (TTM), EBITDA (TTM), Lucro Liquido (TTM), Free Cash Flow (TTM), CAPEX (TTM), CAPEX/Receita |
| Endividamento | Divida Total, Caixa Total, Div./Equity |
| Dividendos | Dividend Yield (12m), Payout Ratio |
| Crescimento | Cresc. Receita (YoY), Cresc. Lucro (YoY) |

## Comparacao Setorial

- Peers hardcoded em `research/peers.py` para ~30 tickers principais da B3
- Para tickers fora do mapeamento, LLM sugere concorrentes automaticamente (cacheado na sessao)
- Tabela comparativa com 12 metricas, medianas do setor e coloracao verde/vermelho vs mediana
- Analise comparativa textual gerada pelo LLM

## Grafico de Cotacao

- Periodos: 1M, 3M, 6M, 1A, 2A, 5A
- Modo comparativo com CDI (API Banco Central, SGS serie 12) e Ibovespa (yfinance `^BVSP`)
- Series normalizadas em % base 0 no modo comparativo

## Variaveis de ambiente

| Variavel | Descricao | Padrao |
|---|---|---|
| `LLM_PROVIDER` | Provider de LLM (`gemini`, `groq`) | `gemini` |
| `LLM_API_KEY` | API key do provider selecionado | - |
| `GEMINI_MODEL` | Modelo do Gemini | `gemini-2.5-flash` |
| `GROQ_MODEL` | Modelo do Groq | `llama-3.3-70b-versatile` |
| `BRAPI_TOKEN` | Token brapi.dev (opcional, fallback) | - |
| `SEARCH_MAX_RESULTS` | Max resultados de busca web | `8` |

## Roadmap

- [x] Fase 1 — MVP: agente de pesquisa + relatorio basico
- [x] Fase 2 — Integracao Yahoo Finance + brapi.dev com fallback progressivo
- [x] Fase 3 — Grafico de cotacao interativo com Plotly (CDI + Ibovespa)
- [x] Fase 4 — Dark theme profissional, cards de indicadores, badges de sentimento
- [x] Fase 5 — Comparacao setorial com peers da B3 (hardcoded + deteccao via LLM)
- [x] Fase 6 — CAPEX do fluxo de caixa, labels TTM/YoY, disclaimer de dados
- [ ] Fase 7 — Sistema multi-agente para analises mais profundas
