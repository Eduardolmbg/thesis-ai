"""Mapeamento de peers brasileiros por setor para comparacao setorial."""

from __future__ import annotations

SECTOR_PEERS: dict[str, list[str]] = {
    # Bancos
    "ITUB4": ["BBDC4", "BBAS3", "SANB11", "BPAC11"],
    "BBDC4": ["ITUB4", "BBAS3", "SANB11", "BPAC11"],
    "BBAS3": ["ITUB4", "BBDC4", "SANB11", "BPAC11"],
    "SANB11": ["ITUB4", "BBDC4", "BBAS3", "BPAC11"],
    "BPAC11": ["ITUB4", "BBDC4", "BBAS3", "SANB11"],
    # Petróleo e Gás
    "PETR4": ["PRIO3", "RECV3", "RRRP3", "CSAN3"],
    "PETR3": ["PRIO3", "RECV3", "RRRP3", "CSAN3"],
    "PRIO3": ["PETR4", "RECV3", "RRRP3"],
    "RECV3": ["PETR4", "PRIO3", "RRRP3"],
    # Mineração e Siderurgia
    "VALE3": ["CSNA3", "GGBR4", "USIM5", "GOAU4"],
    "CSNA3": ["VALE3", "GGBR4", "USIM5", "GOAU4"],
    "GGBR4": ["VALE3", "CSNA3", "USIM5", "GOAU4"],
    "USIM5": ["VALE3", "CSNA3", "GGBR4", "GOAU4"],
    # Varejo
    "MGLU3": ["LREN3", "AZZA3", "BHIA3", "PETZ3"],
    "LREN3": ["MGLU3", "AZZA3", "BHIA3", "ARZZ3"],
    "AZZA3": ["MGLU3", "LREN3", "ARZZ3"],
    # Energia Elétrica
    "EGIE3": ["EQTL3", "CPFE3", "CMIG4", "TAEE11", "ENGI11"],
    "EQTL3": ["EGIE3", "CPFE3", "CMIG4", "NEOE3"],
    "CMIG4": ["EGIE3", "EQTL3", "CPFE3", "TAEE11"],
    "TAEE11": ["EGIE3", "CMIG4", "TRPL4", "ENGI11"],
    # Alimentos e Bebidas
    "ABEV3": ["JBSS3", "BRFS3", "MDIA3", "SMTO3"],
    "JBSS3": ["BRFS3", "MRFG3", "ABEV3", "BEEF3"],
    "BRFS3": ["JBSS3", "MRFG3", "ABEV3"],
    # Saúde
    "RDOR3": ["HAPV3", "FLRY3", "QUAL3", "ONCO3"],
    "HAPV3": ["RDOR3", "FLRY3", "QUAL3"],
    "FLRY3": ["RDOR3", "HAPV3", "DASA3"],
    # Locação de Veículos
    "RENT3": ["MOVI3", "VAMO3"],
    "MOVI3": ["RENT3", "VAMO3"],
    # Seguros
    "BBSE3": ["PSSA3", "CXSE3", "IRBR3"],
    "PSSA3": ["BBSE3", "CXSE3", "IRBR3"],
    # Shoppings / Real Estate
    "MULT3": ["IGTI11", "ALSO3", "BRML3"],
    "IGTI11": ["MULT3", "ALSO3", "BRML3"],
    # Saneamento
    "SBSP3": ["CSMG3", "SAPR11"],
    # Telecomunicações
    "VIVT3": ["TIMS3", "OIBR3"],
    "TIMS3": ["VIVT3"],
    # Industriais / Bens de Capital
    "WEGE3": ["EMBR3", "RAIZ4", "TUPY3"],
    # Papel e Celulose
    "SUZB3": ["KLBN11", "DXCO3"],
    "KLBN11": ["SUZB3", "DXCO3"],
    # Educação
    "COGN3": ["YDUQ3", "ANIM3", "SEER3"],
    "YDUQ3": ["COGN3", "ANIM3", "SEER3"],
}

_SECTOR_SUGGESTIONS: dict[str, str] = {
    "Financial Services": "ITUB4, BBDC4, BBAS3, SANB11",
    "Energy": "PETR4, PRIO3, RECV3, CSAN3",
    "Basic Materials": "VALE3, CSNA3, GGBR4, SUZB3",
    "Consumer Cyclical": "MGLU3, LREN3, AZZA3",
    "Utilities": "EGIE3, EQTL3, CPFE3, CMIG4",
    "Healthcare": "RDOR3, HAPV3, FLRY3",
    "Industrials": "WEGE3, EMBR3, TUPY3",
    "Communication Services": "VIVT3, TIMS3",
    "Consumer Defensive": "ABEV3, JBSS3, BRFS3",
    "Real Estate": "MULT3, IGTI11, ALSO3",
}


def get_peers(ticker: str) -> list[str]:
    """Retorna lista de peers hardcoded para o ticker (máximo 5)."""
    return SECTOR_PEERS.get(ticker.upper().strip(), [])[:5]


def suggest_peers_from_sector(sector: str) -> str:
    """Retorna sugestão de peers com base no setor do yfinance."""
    return _SECTOR_SUGGESTIONS.get(sector, "")
