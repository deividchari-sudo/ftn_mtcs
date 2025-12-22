@echo off
REM Script para iniciar o app Streamlit no Windows

echo ================================
echo Fitness Metrics - Streamlit App
echo ================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não está instalado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 🔍 Verificando dependências...

REM Verificar se streamlit está instalado
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erro ao instalar dependências!
        pause
        exit /b 1
    )
)

echo.
echo ✅ Tudo pronto!
echo.
echo 🚀 Iniciando aplicação...
echo.
echo Acesse em seu navegador: http://localhost:8501
echo.
echo Para parar: Pressione Ctrl+C
echo.

REM Iniciar o app
streamlit run app.py

pause
