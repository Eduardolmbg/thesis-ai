#!/usr/bin/env bash
set -e

# Se ja tem venv e .env, vai direto pro app
if [ -d ".verto" ] && [ -f ".env" ]; then
    source .verto/bin/activate
    echo "Iniciando Verto..."
    echo "Acesse: http://localhost:8501"
    echo ""
    streamlit run app.py
    exit 0
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║      Verto - Setup Automatico        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &>/dev/null; then
    echo "[ERRO] Python 3 nao encontrado!"
    echo ""
    echo "Instale com:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  macOS:         brew install python3"
    echo ""
    exit 1
fi

PYVER=$(python3 --version 2>&1)
echo "[OK] $PYVER encontrado"
echo ""

# Criar ambiente virtual
if [ ! -d ".verto" ]; then
    echo "[1/3] Criando ambiente virtual..."
    python3 -m venv .verto
    echo "      Ambiente virtual criado."
else
    echo "[1/3] Ambiente virtual ja existe."
fi
echo ""

# Instalar dependencias
echo "[2/3] Instalando dependencias..."
source .verto/bin/activate
pip install -r requirements.txt --quiet
echo "      Dependencias instaladas."
echo ""

# Configurar .env
if [ ! -f ".env" ]; then
    echo "[3/3] Criando arquivo .env..."
    cp .env.example .env
    echo "      Arquivo .env criado."
else
    echo "[3/3] Arquivo .env ja existe."
fi

echo ""
echo "Iniciando Verto..."
echo "Acesse: http://localhost:8501"
echo ""
streamlit run app.py
