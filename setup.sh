#!/usr/bin/env bash
set -e

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
    echo "  Ubuntu/Debian: sudo apt install python3 python3-.verto python3-pip"
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
    python3 -m .verto .verto
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
    echo "      Arquivo .env criado a partir do template."
    echo ""
    echo "══════════════════════════════════════════════"
    echo " IMPORTANTE: Abra o arquivo .env e configure"
    echo " sua API key antes de iniciar o Verto."
    echo ""
    echo " APIs gratuitas:"
    echo "   Gemini: https://aistudio.google.com/apikey"
    echo "   Groq:   https://console.groq.com/keys"
    echo "══════════════════════════════════════════════"
else
    echo "[3/3] Arquivo .env ja existe."
fi

echo ""
echo "══════════════════════════════════════════════════"
echo " Setup concluido! Para iniciar o Verto:"
echo ""
echo "   ./start.sh"
echo ""
echo " Ou manualmente:"
echo "   source .verto/bin/activate"
echo "   streamlit run app.py"
echo "══════════════════════════════════════════════════"
echo ""
