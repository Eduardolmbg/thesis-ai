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

## Instalacao

**Pre-requisitos:** Python 3.10+ e uma API key do [Gemini](https://aistudio.google.com/apikey) ou [Groq](https://console.groq.com/keys).

```bash
git clone https://github.com/seu-usuario/Verto.git
cd Verto

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz:

```env
LLM_PROVIDER=gemini
LLM_API_KEY=sua_api_key_aqui
```

## Uso

```bash
streamlit run app.py
```

Acesse `http://localhost:8501`, configure o provider na sidebar, digite um ticker e clique em **Gerar Analise**.

## Licenca

MIT
