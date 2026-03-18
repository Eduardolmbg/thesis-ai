@echo off
chcp 65001 >nul 2>&1
title Verto

:: Se ja tem venv e .env, vai direto pro app
if exist ".verto\Scripts\activate.bat" if exist ".env" goto :start

echo.
echo  ╔══════════════════════════════════════╗
echo  ║      Verto - Setup Automatico        ║
echo  ╚══════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale o Python 3.10+ em: https://www.python.org/downloads/
    echo IMPORTANTE: Marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% encontrado
echo.

:: Criar ambiente virtual
if not exist ".verto" (
    echo [1/3] Criando ambiente virtual...
    python -m venv .verto
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo       Ambiente virtual criado.
) else (
    echo [1/3] Ambiente virtual ja existe.
)
echo.

:: Instalar dependencias
echo [2/3] Instalando dependencias...
call .verto\Scripts\activate.bat
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo       Dependencias instaladas.
echo.

:: Configurar .env
if not exist ".env" (
    echo [3/3] Criando arquivo .env...
    copy .env.example .env >nul
    echo       Arquivo .env criado.
) else (
    echo [3/3] Arquivo .env ja existe.
)

echo.
echo Setup concluido!
echo.

:start
call .verto\Scripts\activate.bat
echo Iniciando Verto...
echo Acesse: http://localhost:8501
echo.
streamlit run app.py
