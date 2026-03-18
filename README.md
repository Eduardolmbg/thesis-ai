# Verto

**AI-Powered Stock Research Agent** para acoes brasileiras (B3).

> Documentacao tecnica: [ARCHITECTURE.md](ARCHITECTURE.md)

---

### Tela inicial

![Tela inicial com chips de tickers populares](Capture1.PNG)

### Cards de indicadores + grafico de cotacao

![Cards de indicadores financeiros e grafico historico de cotacao](Capture2.PNG)

### Tabela de indicadores fundamentalistas (TTM)

![Tabela completa de indicadores financeiros com labels TTM e YoY](Capture3.PNG)

### Sintese de investimento gerada por IA

![Sintese com vies, pontos fortes, atencao, riscos e catalisadores](Capture4.PNG)

---

## Instalacao Rapida

**Pre-requisitos:** Python 3.10+ e uma API key gratuita do [Gemini](https://aistudio.google.com/apikey) ou [Groq](https://console.groq.com/keys).

### Windows

1. Baixe o projeto e de duplo clique em **`verto.bat`**
2. Configure sua API key direto na sidebar do app e clique "Salvar configuracao"

### Mac / Linux

```bash
git clone https://github.com/Eduardolmbg/Verto.git
cd Verto
./verto.sh
```

Na primeira vez ele instala tudo e abre o app. Configure sua API key na sidebar.

Acesse `http://localhost:8501`, configure o provider na sidebar, digite um ticker e clique em **Gerar Analise**.

## Licenca

MIT
