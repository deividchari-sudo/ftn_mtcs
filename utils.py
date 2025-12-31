"""Utilitários pequenos usados pelo app."""

def format_duration(seconds):
    """Formata duração em hh:mm:ss"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_hours_decimal(decimal_hours):
    """Formata horas decimais em hh:mm:ss"""
    total_seconds = int(decimal_hours * 3600)
    return format_duration(total_seconds)

