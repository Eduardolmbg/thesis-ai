"""Todos os prompts do sistema, organizados por etapa de analise."""

SYSTEM_PROMPT = (
    "Voce e um analista fundamentalista senior especializado em acoes brasileiras (B3). "
    "Responda sempre em portugues brasileiro. Seja objetivo, use dados concretos e "
    "evite linguagem promocional. Quando nao tiver certeza sobre um dado, indique "
    "claramente. Nunca invente numeros.\n\n"
    "IMPORTANTE: NAO use emojis no relatorio. Use texto limpo e profissional. "
    "Para indicar sentimento de noticias, use as palavras POSITIVA, NEGATIVA ou "
    "NEUTRA entre colchetes. Exemplo: [POSITIVA] Empresa anuncia aumento de dividendos."
)

# ── Etapa 1: Perfil da Empresa ──────────────────────────────────────────

PROFILE_SEARCH_QUERY = "{ticker} empresa o que faz setor de atuacao modelo de negocio"

PROFILE_PROMPT_WITH_BRAPI = (
    "Aqui estao os dados cadastrais da empresa {ticker}:\n"
    "Nome: {nome}\n"
    "Setor: {setor}\n"
    "Industria: {industria}\n"
    "Descricao: {descricao}\n\n"
    "Com base nesses dados E em seu conhecimento geral, escreva um perfil "
    "conciso e informativo da empresa para um investidor. Inclua: o que faz, "
    "principais produtos/servicos, mercados de atuacao, posicao competitiva, "
    "e breve historico. Se a descricao acima estiver vazia ou incompleta, "
    "use seu conhecimento para complementar.\n\n"
    "Escreva em paragrafos corridos, sem usar bullet points. "
    "Limite-se a 3-4 paragrafos. NAO use emojis."
)

PROFILE_PROMPT_FALLBACK = (
    "Com base nas informacoes disponiveis, escreva um perfil conciso da empresa "
    "cujo ticker e {ticker}. Inclua:\n"
    "- Nome completo da empresa\n"
    "- Setor e subsetor de atuacao\n"
    "- O que a empresa faz (principais produtos e servicos)\n"
    "- Mercados de atuacao (domestico, exportacao, etc.)\n"
    "- Breve historico (fundacao, IPO, marcos importantes)\n"
    "- Posicao competitiva no mercado\n\n"
    "Escreva em paragrafos corridos, sem usar bullet points. "
    "Limite-se a 3-4 paragrafos. NAO use emojis."
)

# ── Etapa 3: Noticias Recentes ──────────────────────────────────────────

NEWS_SEARCH_QUERY = "{ticker} OR {company_name} acao noticias recentes"

NEWS_PROMPT = (
    "Com base nas informacoes disponiveis, resuma as noticias mais relevantes "
    "e recentes sobre {ticker}.\n\n"
    "Para cada noticia, forneca:\n"
    "1. Titulo/Resumo da noticia (1-2 frases)\n"
    "2. Classificacao: [POSITIVA], [NEGATIVA] ou [NEUTRA] para o investidor\n"
    "3. Breve justificativa da classificacao\n\n"
    "Liste ate 5 noticias, priorizando as mais impactantes para o preco da acao. "
    "Agrupe por classificacao (positivas, negativas, neutras).\n\n"
    "NAO use emojis. Use os marcadores [POSITIVA], [NEGATIVA] ou [NEUTRA] em texto puro."
)

# ── Etapa 4: Sintese de Investimento ────────────────────────────────────

SYNTHESIS_PROMPT = (
    "Aqui estao os dados completos para analise de {ticker}:\n\n"
    "DADOS FINANCEIROS (fonte: brapi.dev, dados oficiais):\n{financials_data}\n\n"
    "PERFIL DA EMPRESA:\n{profile}\n\n"
    "NOTICIAS RECENTES:\n{news}\n\n"
    "Com base em TODOS esses dados, gere uma sintese de investimento contendo:\n\n"
    "1. **Vies Geral**: POSITIVO, NEGATIVO ou NEUTRO — justifique com base nos numeros concretos.\n\n"
    "2. **Pontos Fortes** (3-5 itens):\n"
    "   - Baseados nos indicadores e vantagens competitivas\n\n"
    "3. **Pontos Fracos** (3-5 itens):\n"
    "   - Baseados nos indicadores e vulnerabilidades\n\n"
    "4. **Riscos-Chave** (3-5 itens):\n"
    "   - Riscos especificos: regulatorios, macroeconomicos, setoriais, etc.\n\n"
    "Seja objetivo, use os numeros concretos para justificar cada ponto. "
    "Nao faca recomendacao de compra/venda. NAO use emojis."
)
