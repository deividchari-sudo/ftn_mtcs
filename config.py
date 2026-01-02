"""Configuração com segurança - carrega apenas de variáveis de ambiente"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carregar .env apenas em desenvolvimento (não em produção)
if os.getenv("ENV", "development") == "development":
    load_dotenv()

# Validar API key obrigatória
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    logger.warning(
        "⚠️ GROQ_API_KEY não configurada! Funcionalidades de IA desabilitadas. "
        "Configure: export GROQ_API_KEY='sua_chave_aqui'"
    )

# Validar comprimento da chave (chaves Groq têm ~40 caracteres)
if GROQ_API_KEY and len(GROQ_API_KEY) < 10:
    logger.error("❌ GROQ_API_KEY parece inválida (muito curta)")
    GROQ_API_KEY = ""
