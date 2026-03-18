@echo off
chcp 65001 >nul 2>&1
title Verto

:: Verificar se setup foi feito
if not exist ".verto" (
    echo Ambiente virtual nao encontrado. Executando setup primeiro...
    echo.
    call setup.bat
)

:: Verificar .env
if not exist ".env" (
    echo [ERRO] Arquivo .env nao encontrado!
    echo Execute setup.bat primeiro e configure sua API key.
    pause
    exit /b 1
)

:: Ativar .verto e iniciar
call .verto\Scripts\activate.bat
echo Iniciando Verto...
echo Acesse: http://localhost:8501
echo.
streamlit run app.py
