"""
Gerenciador de cache inteligente com SQLite e TTL (Time-To-Live).

Estratégia:
- Atividades: 1 hora
- Métricas de saúde: 6 horas
- Training Status: 2 horas
- Exercícios: 4 horas
- Dispositivos/Config: 24 horas
- Badges/Achievements: 12 horas
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Callable


CACHE_DB = Path.home() / ".fitness_metrics" / "cache.db"
CACHE_DB.parent.mkdir(exist_ok=True)

# Configuração de TTL por tipo de dado (em segundos)
CACHE_TTL = {
    'activities': 3600,           # 1 hora
    'health_metrics': 21600,      # 6 horas
    'training_status': 7200,      # 2 horas
    'exercises': 14400,           # 4 horas
    'vo2_max': 86400,             # 24 horas
    'devices': 86400,             # 24 horas
    'badges': 43200,              # 12 horas
    'body_composition': 21600,    # 6 horas
    'sleep_data': 21600,          # 6 horas
    'stress_data': 21600,         # 6 horas
    'hrv_data': 21600,            # 6 horas
}


def _init_cache_db():
    """Inicializa a tabela de cache se não existir"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                data_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_cached(key: str, data_type: str = 'default') -> Optional[Any]:
    """
    Recupera valor do cache se válido (não expirou).
    
    Args:
        key: Chave única do cache
        data_type: Tipo de dado (define TTL automático)
    
    Returns:
        Valor em cache ou None se expirado/inexistente
    """
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?",
            (key,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            value_str, expires_at = result
            if expires_at:
                expires = datetime.fromisoformat(expires_at)
                if datetime.now() < expires:
                    try:
                        return json.loads(value_str)
                    except json.JSONDecodeError:
                        return value_str
            else:
                # Sem expiração
                try:
                    return json.loads(value_str)
                except json.JSONDecodeError:
                    return value_str
        return None
    except Exception:
        return None


def set_cached(key: str, value: Any, data_type: str = 'default') -> bool:
    """
    Armazena valor em cache com TTL automático.
    
    Args:
        key: Chave única
        value: Valor a armazenar (será serializado como JSON)
        data_type: Tipo de dado (define TTL)
    
    Returns:
        True se sucesso
    """
    try:
        ttl = CACHE_TTL.get(data_type, 3600)
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cache (key, value, data_type, expires_at)
            VALUES (?, ?, ?, ?)
        """, (key, value_str, data_type, expires_at.isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_or_fetch(
    key: str,
    data_type: str,
    fetch_func: Callable,
    *args,
    **kwargs
) -> Optional[Any]:
    """
    Tenta obter do cache, senão executa função de fetch.
    
    Args:
        key: Chave de cache
        data_type: Tipo de dado
        fetch_func: Função a executar se cache inválido
        *args, **kwargs: Argumentos para fetch_func
    
    Returns:
        Valor do cache ou resultado de fetch_func
    """
    cached = get_cached(key, data_type)
    if cached is not None:
        return cached
    
    try:
        result = fetch_func(*args, **kwargs)
        if result is not None:
            set_cached(key, result, data_type)
        return result
    except Exception:
        return None


def invalidate(key: str) -> bool:
    """Remove uma chave do cache"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def invalidate_type(data_type: str) -> bool:
    """Remove todas as chaves de um tipo específico"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE data_type = ?", (data_type,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def clear_expired() -> int:
    """Remove todas as chaves expiradas. Retorna quantidade removida."""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
            (datetime.now().isoformat(),)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
    except Exception:
        return 0


def get_cache_stats() -> dict:
    """Retorna estatísticas do cache"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(LENGTH(value)) FROM cache")
        count, total_size = cursor.fetchone() or (0, 0)
        
        cursor.execute("""
            SELECT data_type, COUNT(*) FROM cache GROUP BY data_type
        """)
        by_type = dict(cursor.fetchall())
        conn.close()
        
        return {
            'total_entries': count,
            'total_size_bytes': total_size or 0,
            'by_type': by_type
        }
    except Exception:
        return {}


# Inicializar BD ao importar
_init_cache_db()
