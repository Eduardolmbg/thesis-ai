#!/usr/bin/env bash
set -e

# Verificar se setup foi feito
if [ ! -d ".verto" ]; then
    echo "Ambiente virtual nao encontrado. Executando setup primeiro..."
    echo ""
    bash setup.sh
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "[ERRO] Arquivo .env nao encontrado!"
    echo "Execute ./setup.sh primeiro e configure sua API key."
    exit 1
fi

# Ativar .verto e iniciar
source .verto/bin/activate
echo "Iniciando Verto..."
echo "Acesse: http://localhost:8501"
echo ""
streamlit run app.py
