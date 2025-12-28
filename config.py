"""
Configurações globais do projeto Fitness Metrics Dashboard
"""
from pathlib import Path

# Diretórios e arquivos de dados
DATA_DIR = Path.home() / ".fitness_metrics"
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = DATA_DIR / "user_config.json"
CREDENTIALS_FILE = DATA_DIR / "garmin_credentials.json"
METRICS_FILE = DATA_DIR / "fitness_metrics.json"
WORKOUTS_FILE = DATA_DIR / "workouts_42_dias.json"

# Configurações da aplicação
APP_TITLE = "Fitness Metrics Dashboard"
EXTERNAL_STYLESHEETS = ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"]