"""
Módulo de armazenamento local para dados de fitness.

Gerencia leitura e gravação de:
- Configurações do usuário (user_config.json)
- Credenciais do Garmin (garmin_credentials.json)
- Métricas de fitness (fitness_metrics.json)
- Histórico de treinos (workouts_42_dias.json)
- Tokens OAuth do Garmin (garmin_tokens.json/)
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


# Configurações de caminhos
DATA_DIR = Path.home() / ".fitness_metrics"
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = DATA_DIR / "user_config.json"
CREDENTIALS_FILE = DATA_DIR / "garmin_credentials.json"
METRICS_FILE = DATA_DIR / "fitness_metrics.json"
WORKOUTS_FILE = DATA_DIR / "workouts_42_dias.json"
SYNC_FILE = DATA_DIR / "sync_state.json"


def _try_secure_file(path: Path) -> None:
    """Best-effort: restringe permissões do arquivo (quando suportado)."""
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


# === ESTADO DE SINCRONIZAÇÃO ===

def load_sync_state() -> dict:
    """Carrega estado de sincronização (ex.: última sync com Garmin)."""
    if SYNC_FILE.exists():
        try:
            with open(SYNC_FILE, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def save_sync_state(state: dict) -> None:
    """Salva estado de sincronização."""
    with open(SYNC_FILE, "w") as f:
        json.dump(state or {}, f, indent=4)
    _try_secure_file(SYNC_FILE)


# === CONFIGURAÇÕES ===

def load_config() -> dict:
    """Carrega configurações de fitness do armazenamento local"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "age": 29,
        "ftp": 250,
        "pace_threshold": "4:22",
        "swim_pace_threshold": "2:01",
        "hr_rest": 50,
        "hr_max": 191,
        "hr_threshold": 162,
        "weekly_distance_goal": 50.0,
        "weekly_tss_goal": 300,
        "weekly_hours_goal": 7.0,
        "weekly_activities_goal": 5,
        "monthly_distance_goal": 200.0,
        "monthly_tss_goal": 1200,
        "monthly_hours_goal": 30.0,
        "monthly_activities_goal": 20,
        "target_ctl": 50,
        "target_atl_max": 80,
    }


def save_config(config: dict) -> None:
    """Salva configurações de fitness no armazenamento local"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    _try_secure_file(CONFIG_FILE)


# === CREDENCIAIS GARMIN ===

def load_credentials() -> dict:
    """Carrega credenciais do Garmin do armazenamento local"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return {"email": "", "password": ""}


def save_credentials(email: str, password: str) -> None:
    """Salva credenciais do Garmin no armazenamento local (apenas no device)"""
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f, indent=4)
    try:
        os.chmod(CREDENTIALS_FILE, 0o600)
    except:
        pass


# === TOKENS GARMIN (OAuth) ===

def validate_garmin_tokens_locally() -> bool:
    """Valida tokens localmente sem conectar ao servidor (útil para PythonAnywhere)"""
    try:
        token_dir = Path("garmin_tokens.json")
        if not token_dir.exists() or not token_dir.is_dir():
            return False
            
        oauth1_path = token_dir / "oauth1_token.json"
        oauth2_path = token_dir / "oauth2_token.json"
        
        if not oauth1_path.exists() or not oauth2_path.exists():
            return False
            
        # Carregar e validar estrutura básica dos tokens
        with open(oauth1_path, "r") as f:
            oauth1 = json.load(f)
            
        with open(oauth2_path, "r") as f:
            oauth2 = json.load(f)
            
        # Verificar se OAuth1 tem campos obrigatórios
        if not all(key in oauth1 for key in ["oauth_token", "oauth_token_secret"]):
            return False
            
        # Verificar se OAuth2 tem campos obrigatórios e não expirou
        required_oauth2 = ["access_token", "token_type", "expires_in", "refresh_token"]
        if not all(key in oauth2 for key in required_oauth2):
            return False
            
        # Verificar expiração (com margem de segurança de 1 hora)
        expires_at = datetime.fromisoformat(oauth2.get("expires_at", "2000-01-01T00:00:00"))
        if datetime.now() + timedelta(hours=1) > expires_at:
            return False
            
        return True
        
    except Exception:
        return False


def save_garmin_tokens(garmin_client) -> bool:
    """Salva tokens do Garmin após autenticação bem-sucedida"""
    try:
        token_dir = Path("garmin_tokens.json")
        token_dir.mkdir(exist_ok=True)
        
        # Dumpar tokens do cliente garmin
        garmin_client.garth.dump(str(token_dir))
        return True
    except Exception as e:
        return False


# === MÉTRICAS DE FITNESS ===

def load_metrics() -> list:
    """Carrega métricas de fitness do armazenamento local"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    return []


def save_metrics(metrics: list) -> None:
    """Salva métricas de fitness no armazenamento local"""
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)
    _try_secure_file(METRICS_FILE)


# === HISTÓRICO DE TREINOS ===

def load_workouts() -> list:
    """Carrega lista de workouts do armazenamento local"""
    if WORKOUTS_FILE.exists():
        with open(WORKOUTS_FILE, "r") as f:
            return json.load(f)
    return []


def save_workouts(workouts: list) -> None:
    """Salva lista de workouts no armazenamento local"""
    with open(WORKOUTS_FILE, "w") as f:
        json.dump(workouts, f, indent=4)
    _try_secure_file(WORKOUTS_FILE)
