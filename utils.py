"""
Utilitários para o app Fitness Metrics
Contém funções de cache, processamento de dados e helpers
"""

import json
import hashlib
from functools import lru_cache
from pathlib import Path
import os

# Cache global para dados processados
_data_cache = {}
_file_hashes = {}

def get_file_hash(file_path):
    """Calcula hash do arquivo para detectar mudanças"""
    if not file_path.exists():
        return None
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def is_file_changed(file_path):
    """Verifica se arquivo mudou desde último acesso"""
    current_hash = get_file_hash(file_path)
    last_hash = _file_hashes.get(str(file_path))
    if current_hash != last_hash:
        _file_hashes[str(file_path)] = current_hash
        return True
    return False

@lru_cache(maxsize=32)
def compute_tss_cached(activity_json, config_json):
    """Versão cached de compute_tss_variants"""
    from app import compute_tss_variants  # Import aqui para evitar circular import
    activity = json.loads(activity_json)
    config = json.loads(config_json)
    return compute_tss_variants(activity, config)

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

def generate_activity_html(activities, colors, icons, max_activities=3):
    """Gera HTML otimizado para atividades de um dia"""
    if not activities:
        return ""

    html_parts = []
    for act in activities[:max_activities]:
        color = colors.get(act['category'], colors['other'])
        icon = icons.get(act['category'], icons['other'])
        duration_str = format_duration(act['duration'])
        distance_km = act['distance'] / 1000
        name = act['name'][:15].replace("'", "&#39;")
        tss_badge_color = '#10b981' if act['tss'] < 100 else '#f59e0b' if act['tss'] < 150 else '#ef4444'

        html_parts.append(
            f"<div style='background:white;border-left:3px solid {color};border-radius:4px;padding:4px;margin-bottom:6px;box-shadow:0 1px 2px rgba(0,0,0,0.06);transition:all 0.2s ease;position:relative;'>"
            f"<div style='font-size:0.7rem;font-weight:700;color:#1f2937;margin-bottom:1px;'>{icon} {name}</div>"
            f"<div style='font-size:0.62rem;color:#6b7280;'>{duration_str} • {distance_km:.1f}km</div>"
            f"<div style='position:absolute;top:2px;right:2px;background:{tss_badge_color};color:white;padding:1px 3px;border-radius:3px;font-weight:600;font-size:0.52rem;z-index:10;'>{act['tss']:.0f}</div>"
            "</div>"
        )

    # Adicionar indicador de mais atividades se necessário
    if len(activities) > max_activities:
        html_parts.append(f"<div style='text-align:center;color:#9ca3af;font-size:0.6rem;margin-top:2px;'>+{len(activities)-max_activities}</div>")

    return "".join(html_parts)