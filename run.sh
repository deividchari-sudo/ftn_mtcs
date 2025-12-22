#!/bin/bash
# Script para iniciar o app Streamlit no Android via Termux

echo "================================"
echo "Fitness Metrics - Streamlit App"
echo "================================"
echo ""

# Verificar se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não está instalado!"
    echo "Execute: pkg install python"
    exit 1
fi

# Verificar se as dependências estão instaladas
echo "🔍 Verificando dependências..."
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

echo ""
echo "✅ Tudo pronto!"
echo ""
echo "🚀 Iniciando aplicação..."
echo ""
echo "Acesse em seu navegador: http://localhost:8501"
echo ""
echo "Para parar: Pressione Ctrl+C"
echo ""

# Iniciar o app
streamlit run app.py
