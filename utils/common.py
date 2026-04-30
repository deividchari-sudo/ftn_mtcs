"""
Funções utilitárias comuns extraídas de múltiplos módulos.

Este módulo contém funções que eram duplicadas em app.py e outros módulos,
centralizando-as em um único lugar para manutenção.
"""
from datetime import datetime, timedelta
from typing import Any, Optional


def parse_start_time(value: str) -> Optional[datetime]:
    """
    Parse string de data/hora para datetime.
    
    Aceita múltiplos formatos comuns.
    
    Args:
        value: String de data/hora
        
    Returns:
        datetime object ou None se inválido
    """
    if not value:
        return None
    
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    
    return None


def type_key(workout: dict) -> str:
    """
    Extrai o tipo de atividade de um workout.
    
    Args:
        workout: Dicionário com dados do workout
        
    Returns:
        String com o tipo de atividade ou string vazia
    """
    try:
        activity_type = workout.get("activityType", {}) or {}
        return activity_type.get("typeKey", "") or ""
    except Exception:
        return ""


def modality_bucket(type_key: str) -> Optional[str]:
    """
    Classifica tipo de atividade em modalidade (swim, bike, run).
    
    Args:
        type_key: Tipo de atividade (ex: 'running', 'cycling')
        
    Returns:
        'swim', 'bike', 'run' ou None
    """
    key = (type_key or "").lower()
    
    if any(k in key for k in ["swim", "natação", "natacao"]):
        return "swim"
    elif any(k in key for k in ["bike", "cycling", "ride", "ciclismo"]):
        return "bike"
    elif any(k in key for k in ["run", "running", "corrida"]):
        return "run"
    
    return None


def tri_bucket(type_key: str) -> Optional[str]:
    """
    Classifica tipo em bucket de triathlon (swim, bike, run, strength).
    
    Similar a modality_bucket mas inclui strength training.
    
    Args:
        type_key: Tipo de atividade
        
    Returns:
        'swim', 'bike', 'run', 'strength' ou None
    """
    key = (type_key or "").lower()
    
    if any(k in key for k in ["swim", "natação", "natacao"]):
        return "swim"
    elif any(k in key for k in ["bike", "cycling", "ride", "ciclismo"]):
        return "bike"
    elif any(k in key for k in ["run", "running", "corrida"]):
        return "run"
    elif any(k in key for k in ["strength", "weight", "hiit", "crossfit"]):
        return "strength"
    
    return None


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    """
    Shift months by delta, handling year boundaries.
    
    Args:
        year: Ano base
        month: Mês base (1-12)
        delta: Meses a adicionar (positivo) ou subtrair (negativo)
        
    Returns:
        Tuple (novo_ano, novo_mes)
    """
    month_index = (year * 12 + (month - 1)) + delta
    new_year = month_index // 12
    new_month = (month_index % 12) + 1
    return new_year, new_month


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Converte valor para float de forma segura.
    
    Args:
        value: Valor a converter
        default: Valor padrão se conversão falhar
        
    Returns:
        float convertido ou default
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Converte valor para int de forma segura.
    
    Args:
        value: Valor a converter
        default: Valor padrão se conversão falhar
        
    Returns:
        int convertido ou default
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def clamp_percentage(value: float, target: float) -> int:
    """
    Calcula percentual clamped entre 0 e 100.
    
    Args:
        value: Valor atual
        target: Valor alvo
        
    Returns:
        Percentual entre 0 e 100
    """
    try:
        if target <= 0:
            return 0
        pct = (value / target) * 100
        return int(max(0, min(100, pct)))
    except Exception:
        return 0


def format_hours_decimal(seconds: float) -> str:
    """
    Formata segundos em formato decimal de horas (ex: 1.5 = 1h30min).
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada como horas decimais
    """
    if not seconds or seconds <= 0:
        return "0.0"
    
    hours = seconds / 3600
    return f"{hours:.1f}h"
