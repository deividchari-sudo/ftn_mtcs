"""
Configurações do aplicativo.

Carrega de arquivo JSON ou usa defaults.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

# Diretório de dados
DATA_DIR = Path.home() / ".fitness_metrics"

# Arquivos de configuração
CONFIG_FILE = DATA_DIR / "user_config.json"


def get_default_config() -> Dict[str, Any]:
    """Retorna configurações padrão."""
    return {
        # FTP e thresholds
        "ftp": 250,
        "threshold_pace_running": 300,  # 5:00/km em segundos
        "threshold_pace_swimming": 100,  # 1:40/100m em segundos
        
        # FC
        "lthr": 170,
        "hr_max": 185,
        "hr_rest": 50,
        
        # Preferências
        "gender": "male",  # ou "female"
        "units": "metric",  # ou "imperial"
        
        # Alertas
        "enable_alerts": True,
        "tsb_warning_threshold": -20,
        
        # Integrações
        "garmin_auto_sync": False,
    }


def load_config() -> Dict[str, Any]:
    """Carrega configurações do arquivo ou retorna defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            # Merge com defaults para garantir todas as chaves
            defaults = get_default_config()
            defaults.update(config)
            return defaults
        except (json.JSONDecodeError, IOError):
            return get_default_config()
    return get_default_config()


def save_config(config: Dict[str, Any]) -> None:
    """Salva configurações no arquivo."""
    DATA_DIR.mkdir(exist_ok=True, mode=0o700)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
