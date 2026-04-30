"""Configurações centralizadas."""
import os

# API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

__all__ = ['GROQ_API_KEY']
