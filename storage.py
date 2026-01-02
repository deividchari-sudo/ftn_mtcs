"""
Módulo de armazenamento local para dados de fitness com SEGURANÇA.

Gerencia leitura e gravação de:
- Configurações do usuário (user_config.json)
- Credenciais do Garmin (garmin_credentials.json) [ENCRIPTADAS]
- Métricas de fitness (fitness_metrics.json)
- Histórico de treinos (workouts_42_dias.json)
- Tokens OAuth do Garmin (garmin_tokens.json/) [PROTEGIDOS]
"""
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

logger = logging.getLogger(__name__)


# Configurações de caminhos
DATA_DIR = Path.home() / ".fitness_metrics"
DATA_DIR.mkdir(exist_ok=True, mode=0o700)  # Apenas owner pode acessar
TOKEN_DIR = Path("garmin_tokens.json")


def _get_encryption_key() -> bytes:
    """Gera chave de encriptação baseada em machine-id (PBKDF2)"""
    try:
        import platform
        machine_id = f"{platform.node()}{platform.system()}"
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'fitness_metrics_salt_v1',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return key
    except Exception as e:
        logger.error(f"Erro ao gerar chave de criptografia: {e}")
        raise


def _encrypt_data(data: str) -> str:
    """Encripta dados usando Fernet (AES-128)"""
    try:
        key = _get_encryption_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Erro ao encriptar dados: {e}")
        raise


def _decrypt_data(encrypted_data: str) -> str:
    """Decripta dados"""
    try:
        key = _get_encryption_key()
        cipher = Fernet(key)
        decrypted = cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Erro ao decriptar dados: {e}")
        raise


def _try_secure_file(path: Path) -> None:
    """Restringe permissões do arquivo para apenas owner ler/escrever (0o600)"""
    try:
        os.chmod(path, 0o600)  # rw------- (owner only)
        logger.debug(f"Permissões seguras aplicadas: {path}")
    except Exception as e:
        logger.warning(f"Aviso: Não foi possível secure {path}: {e}")


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
        # Configurações de Zonas de Treinamento
        "swim_css": 120.0,  # Critical Swim Speed (segundos/100m)
        "bike_ftp": 250,  # Functional Threshold Power (watts)
        "run_lthr": 162,  # Lactate Threshold Heart Rate (bpm)
        "run_threshold_pace": 4.37,  # Threshold pace (min/km)
        "training_model": "polarized",  # polarized, pyramidal, threshold
    }


def save_config(config: dict) -> None:
    """Salva configurações de fitness no armazenamento local"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    _try_secure_file(CONFIG_FILE)


# === CREDENCIAIS GARMIN ===

def load_credentials() -> dict:
    """Carrega e descriptografa credenciais do Garmin"""
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                data = json.load(f)
            
            # Suporte retroativo para versão antiga (sem encriptação)
            if "password" in data and "password_encrypted" not in data:
                logger.warning("⚠️ Credenciais antigas detectadas (não encriptadas)")
                return data
            
            # Versão nova (encriptada)
            if "password_encrypted" in data:
                try:
                    decrypted_password = _decrypt_data(data["password_encrypted"])
                    return {
                        "email": data.get("email", ""),
                        "password": decrypted_password
                    }
                except Exception as e:
                    logger.error(f"❌ Erro ao descriptografar credenciais: {e}")
                    return {"email": "", "password": ""}
            
            return data
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            return {"email": "", "password": ""}
    
    return {"email": "", "password": ""}


def save_credentials(email: str, password: str) -> None:
    """Salva credenciais do Garmin (senha encriptada com AES)"""
    if not email or not password:
        raise ValueError("❌ Email e senha não podem estar vazios")
    
    if not isinstance(email, str) or not isinstance(password, str):
        raise TypeError("❌ Email e senha devem ser strings")
    
    # Limitar tamanho para prevenir ataques de memória
    if len(password) > 256 or len(email) > 256:
        raise ValueError("❌ Email ou senha muito longos (máx 256 caracteres)")
    
    try:
        encrypted_password = _encrypt_data(password)
        credentials = {
            "email": email,
            "password_encrypted": encrypted_password,
            "encrypted_at": datetime.now().isoformat()
        }
        
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f, indent=2)
        
        _try_secure_file(CREDENTIALS_FILE)
        logger.info("✅ Credenciais salvas com segurança (senha encriptada AES-128)")
    except Exception as e:
        logger.error(f"Erro ao salvar credenciais: {e}")
        raise


# === TOKENS GARMIN (OAuth) ===

def validate_garmin_tokens_locally() -> bool:
    """Valida tokens localmente com verificações rigorosas de segurança"""
    try:
        token_dir = TOKEN_DIR
        
        # Validar existência
        if not token_dir.exists() or not token_dir.is_dir():
            return False
        
        # Validar permissões (devem ser 0o700 ou 0o600, sem acesso de outros)
        stat_info = os.stat(token_dir)
        if (stat_info.st_mode & 0o077) != 0:  # Verifica se others/group têm acesso
            logger.warning(f"⚠️ Aviso de segurança: {token_dir} tem permissões inseguras")
            # Corrigir automaticamente
            try:
                os.chmod(token_dir, 0o700)
            except Exception:
                pass
        
        oauth1_path = token_dir / "oauth1_token.json"
        oauth2_path = token_dir / "oauth2_token.json"
        
        if not oauth1_path.exists() or not oauth2_path.exists():
            return False
        
        # Validar permissões dos arquivos individuais
        for token_file in [oauth1_path, oauth2_path]:
            stat_info = os.stat(token_file)
            if (stat_info.st_mode & 0o077) != 0:
                logger.warning(f"⚠️ Corrigindo permissões inseguras: {token_file}")
                try:
                    os.chmod(token_file, 0o600)
                except Exception:
                    pass
        
        # Carregar e validar estrutura básica dos tokens
        with open(oauth1_path, "r") as f:
            oauth1 = json.load(f)
        
        with open(oauth2_path, "r") as f:
            oauth2 = json.load(f)
        
        # Verificar se OAuth1 tem campos obrigatórios
        required_oauth1 = ["oauth_token", "oauth_token_secret"]
        if not all(key in oauth1 for key in required_oauth1):
            logger.warning("❌ OAuth1 token incompleto")
            return False
        
        # Verificar se OAuth2 tem campos obrigatórios
        required_oauth2 = ["access_token", "token_type", "expires_in", "refresh_token", "expires_at"]
        if not all(key in oauth2 for key in required_oauth2):
            logger.warning("❌ OAuth2 token incompleto")
            return False
        
        # Verificar se tokens não estão vazios
        if not oauth1.get("oauth_token") or not oauth2.get("access_token"):
            logger.warning("❌ Tokens vazios")
            return False
        
        # Verificar expiração (com margem de segurança de 1 hora)
        try:
            expires_at = datetime.fromisoformat(oauth2.get("expires_at", "2000-01-01T00:00:00"))
            if datetime.now() + timedelta(hours=1) > expires_at:
                logger.info("⚠️ Tokens expirados ou prestes a expirar")
                return False
        except ValueError as e:
            logger.warning(f"❌ Formato de data inválido nos tokens: {e}")
            return False
        
        logger.debug("✅ Tokens validados com sucesso")
        return True
    
    except Exception as e:
        logger.debug(f"Erro ao validar tokens: {e}")
        return False


def save_garmin_tokens(garmin_client) -> bool:
    """Salva tokens do Garmin com proteção máxima (permissões 0o700)"""
    try:
        token_dir = TOKEN_DIR
        
        # Remover diretório antigo se existir (para recriar com permissões seguras)
        if token_dir.exists():
            import shutil
            shutil.rmtree(token_dir)
        
        # Criar com permissões restritas (apenas owner)
        token_dir.mkdir(exist_ok=True, mode=0o700)
        
        # Dumpar tokens do cliente garmin
        garmin_client.garth.dump(str(token_dir))
        
        # Garantir permissões restritas em todos os arquivos de token
        for token_file in token_dir.glob("*.json"):
            os.chmod(token_file, 0o600)
        
        logger.info(f"✅ Tokens salvos com segurança em {token_dir} (permissões 0o700)")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar tokens: {e}")
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


# === DADOS DE SAÚDE (Health Metrics) ===

def load_health_metrics() -> dict:
    """Carrega dados de saúde (HRV, Stress, Sleep, VO2, Composição Corporal)"""
    if HEALTH_DATA_FILE.exists():
        try:
            with open(HEALTH_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_health_metrics(health_data: dict) -> None:
    """Salva dados de saúde agregados"""
    with open(HEALTH_DATA_FILE, "w") as f:
        json.dump(health_data, f, indent=4)
    _try_secure_file(HEALTH_DATA_FILE)


# === TRAINING STATUS ===

def load_training_status() -> dict:
    """Carrega últimos dados de training status"""
    if TRAINING_STATUS_FILE.exists():
        try:
            with open(TRAINING_STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_training_status(status_data: dict) -> None:
    """Salva training status do Garmin"""
    with open(TRAINING_STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)
    _try_secure_file(TRAINING_STATUS_FILE)


# === EXERCÍCIOS (Exercises) ===

def load_exercises() -> dict:
    """Carrega histórico de exercícios (por activity_id)"""
    if EXERCISES_FILE.exists():
        try:
            with open(EXERCISES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_exercises(exercises_data: dict) -> None:
    """Salva histórico de exercícios"""
    with open(EXERCISES_FILE, "w") as f:
        json.dump(exercises_data, f, indent=4)
    _try_secure_file(EXERCISES_FILE)

