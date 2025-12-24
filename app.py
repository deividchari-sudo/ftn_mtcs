import streamlit as st
import json
import os
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pathlib import Path
import time
import numpy as np
from functools import lru_cache
import hashlib

# Importar utilitários
from utils import (
    format_duration, format_hours_decimal, generate_activity_html,
    get_file_hash, is_file_changed
)

# Configuração da página
st.set_page_config(
    page_title="Fitness Metrics",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - Tema Claro Moderno
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
<style>
    /* ========== TEMA BASE ========== */
    * {
        transition: all 0.3s ease !important;
    }
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        color: #212529 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    [data-testid="stSidebar"] * {
        color: #212529 !important;
    }
    [data-testid="stSidebar"] h1 {
        color: #0d6efd !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(13,110,253,0.1) !important;
    }
    
    /* Radio buttons no menu */
    [data-testid="stSidebar"] .stRadio > label {
        color: #212529 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: #fff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 4px 0 !important;
        cursor: pointer !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        border-color: #0d6efd !important;
        background: #e7f1ff !important;
        transform: translateX(4px) !important;
    }
    
    /* ========== HEADER & FOOTER ========== */
    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.95) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }
    footer {
        background: #f8f9fa !important;
        color: #6c757d !important;
        border-top: 1px solid #e9ecef !important;
    }
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, h4, h5, h6 {
        color: #212529 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    h1 {
        font-size: 1.8rem !important;
        background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    h2 {
        font-size: 1.4rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    
    /* ========== INPUTS ========== */
    input, textarea, select {
        background: #fff !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    input:focus, textarea:focus, select:focus {
        border-color: #0d6efd !important;
        box-shadow: 0 0 0 0.25rem rgba(13,110,253,0.15) !important;
        outline: none !important;
    }
    
    [data-baseweb="input"] input,
    [data-baseweb="input"] textarea {
        background: #fff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    /* ========== LABELS ========== */
    label, [data-testid="stWidgetLabel"] label {
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 8px !important;
    }
    
    /* ========== BOTÕES ========== */
    .stButton > button {
        background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        box-shadow: 0 4px 12px rgba(13,110,253,0.25) !important;
        cursor: pointer !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0b5ed7 0%, #0aa2c0 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(13,110,253,0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(13,110,253,0.3) !important;
    }
    
    /* ========== TABELAS ========== */
    .stDataFrame, [data-testid="stDataFrame"] {
        background: #fff !important;
        border-radius: 12px !important;
        border: 1px solid #e9ecef !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    .stDataFrame thead th {
        background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%) !important;
        color: #fff !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 14px !important;
        border: none !important;
    }
    .stDataFrame tbody td {
        background: #fff !important;
        color: #212529 !important;
        padding: 12px !important;
        border-bottom: 1px solid #f8f9fa !important;
    }
    .stDataFrame tbody tr:hover td {
        background: #e7f1ff !important;
    }
    
    /* ========== EXPANDER ========== */
    [data-testid="stExpander"] {
        background: #fff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        margin: 16px 0 !important;
    }
    [data-testid="stExpander"] > div:first-child {
        background: linear-gradient(135deg, #e7f1ff 0%, #cfe2ff 100%) !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    [data-testid="stExpander"] button {
        background: transparent !important;
        color: #0d6efd !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border: none !important;
    }
    [data-testid="stExpander"] svg {
        color: #0d6efd !important;
    }
    
    /* ========== ALERTAS ========== */
    .stAlert, [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left: 4px solid !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    /* ========== MÉTRICAS ========== */
    [data-testid="stMetric"] {
        background: #fff !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
        border: 2px solid #e9ecef !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
        border-color: #0d6efd !important;
    }
    [data-testid="stMetric"] label {
        color: #6c757d !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0d6efd !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    
    /* ========== CARDS BOOTSTRAP ========== */
    .card {
        background: #fff !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
    }
    .card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.12) !important;
        border-color: #0d6efd !important;
    }
    
    /* ========== SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 10px !important;
        height: 10px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f8f9fa !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%) !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #0b5ed7 0%, #0aa2c0 100%) !important;
    }
    
    /* ========== RESPONSIVE ========== */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        .stButton > button {
            width: 100% !important;
            padding: 14px !important;
        }
        [data-testid="stMetric"] {
            padding: 16px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Diretório para armazenar credenciais localmente
LOCAL_STORAGE_DIR = Path.home() / ".fitness_metrics"
LOCAL_STORAGE_DIR.mkdir(exist_ok=True)

CONFIG_FILE = LOCAL_STORAGE_DIR / "user_config.json"
CREDENTIALS_FILE = LOCAL_STORAGE_DIR / "garmin_credentials.json"
METRICS_FILE = LOCAL_STORAGE_DIR / "fitness_metrics.json"
WORKOUTS_FILE = LOCAL_STORAGE_DIR / "workouts_42_dias.json"

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

@lru_cache(maxsize=1)
def load_config_cached():
    """Carrega configurações com cache"""
    return load_config()

@lru_cache(maxsize=1)
def load_workouts_cached():
    """Carrega workouts com cache baseado em hash do arquivo"""
    if is_file_changed(WORKOUTS_FILE):
        _data_cache['workouts'] = load_workouts()
        _data_cache['workouts_processed'] = None  # Invalidar cache processado
    return _data_cache.get('workouts', [])

@lru_cache(maxsize=1)
def load_metrics_cached():
    """Carrega métricas com cache baseado em hash do arquivo"""
    if is_file_changed(METRICS_FILE):
        _data_cache['metrics'] = load_metrics()
    return _data_cache.get('metrics', [])

@lru_cache(maxsize=32)
def compute_tss_cached(activity_json, config_json):
    """Versão cached de compute_tss_variants"""
    activity = json.loads(activity_json)
    config = json.loads(config_json)
    return compute_tss_variants(activity, config)

def get_processed_workouts():
    """Processa workouts uma vez e armazena em cache"""
    if _data_cache.get('workouts_processed') is None:
        workouts = load_workouts_cached()
        config = load_config_cached()

        if not workouts:
            _data_cache['workouts_processed'] = []
            return []

        processed = []
        config_json = json.dumps(config, sort_keys=True)

        for workout in workouts:
            # Calcular TSS uma vez
            activity_json = json.dumps(workout, sort_keys=True)
            tss_data = compute_tss_cached(activity_json, config_json)

            processed_workout = {
                'name': workout.get('activityName', 'Treino'),
                'category': _activity_category(workout),
                'duration': workout.get('duration', 0),
                'distance': workout.get('distance', 0),
                'start_time': workout.get('startTimeLocal') or workout.get('startTime', ''),
                'tss': tss_data.get('tss', 0),
                'tss_method': tss_data.get('tss_method', 'none'),
                'date': None  # Será preenchido depois se necessário
            }
            processed.append(processed_workout)

        _data_cache['workouts_processed'] = processed

    return _data_cache['workouts_processed']

def load_config():
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
        # Metas semanais
        "weekly_distance_goal": 50.0,  # km
        "weekly_tss_goal": 300,  # pontos TSS
        "weekly_hours_goal": 7.0,  # horas
        "weekly_activities_goal": 5,  # número de atividades
        # Metas mensais
        "monthly_distance_goal": 200.0,  # km
        "monthly_tss_goal": 1200,  # pontos TSS
        "monthly_hours_goal": 30.0,  # horas
        "monthly_activities_goal": 20,  # número de atividades
        # Metas de performance
        "target_ctl": 50,  # CTL alvo
        "target_atl_max": 80,  # ATL máximo permitido
    }

def save_config(config):
    """Salva configurações de fitness no armazenamento local"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_credentials():
    """Carrega credenciais do Garmin do armazenamento local"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return {"email": "", "password": ""}

def save_credentials(email, password):
    """Salva credenciais do Garmin no armazenamento local (apenas no device)"""
    # Definir permissões restritas no arquivo
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f, indent=4)
    # Tentar restringir permissões de leitura (em Windows, Linux/Mac)
    try:
        os.chmod(CREDENTIALS_FILE, 0o600)
    except:
        pass

def load_metrics():
    """Carrega métricas de fitness do armazenamento local"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    return []

def save_metrics(metrics):
    """Salva métricas de fitness no armazenamento local"""
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

def load_workouts():
    """Carrega lista de workouts do armazenamento local"""
    if WORKOUTS_FILE.exists():
        with open(WORKOUTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_workouts(workouts):
    """Salva lista de workouts no armazenamento local"""
    with open(WORKOUTS_FILE, "w") as f:
        json.dump(workouts, f, indent=4)

def calculate_trimp(activity, config):
    """Calcula TRIMP (Training Impulse) para uma atividade"""
    import math
    
    category = _activity_category(activity)

    duration_sec = float(activity.get('duration', 0) or 0)
    if duration_sec <= 0:
        return 0.0
    duration_min = duration_sec / 60.0
    duration_h = duration_sec / 3600.0

    hr_rest = float(config.get('hr_rest', 50) or 50)
    hr_max = float(config.get('hr_max', 191) or 191)

    def _avg_hr_value(a: dict) -> float:
        v = (a.get('averageHR') or a.get('avgHR') or a.get('avgHr') or a.get('averageHeartRate') or a.get('avgHeartRate'))
        return float(v or 0)

    def _hr_trimp(avg_hr: float) -> float:
        """
        TRIMP por Frequência Cardíaca (Banister, 1991).
        Fórmula: TRIMP = duração_min × (FC_avg - FC_repouso) / (FC_max - FC_repouso) × 0.64 × e^(1.92 × HRR)
        Onde HRR = (FC_avg - FC_repouso) / (FC_max - FC_repouso)
        
        Referência: TrainingPeaks TSS ≈ 30-40 para treino moderado de 1h (quando HR bem acima do limiar)
        """
        if avg_hr <= 0 or hr_max <= hr_rest:
            return 0.0
        hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
        hr_reserve = max(0.0, min(2.0, float(hr_reserve)))
        # Fórmula original: duration_min × HRR × 0.64 × e^(1.92 × HRR)
        # Ajuste: dividir por ~2-2.5 para alinhar com TrainingPeaks (evita valores muito altos)
        trimp_raw = float(duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve))
        # Normalizar para escala TrainingPeaks (1 hora moderada ≈ 30-50 pontos)
        return trimp_raw / 2.5

    avg_hr = _avg_hr_value(activity)

    if category == 'cycling':
        ftp = float(config.get('ftp', 0) or 0)
        np_power = activity.get('normalizedPower') or activity.get('normPower')
        avg_power = activity.get('averagePower') or activity.get('avgPower')
        power = float(np_power or avg_power or 0)
        if ftp > 0 and power > 0:
            if_ = power / ftp
            trimp = duration_h * (if_ ** 2) * 100.0
        else:
            trimp = _hr_trimp(avg_hr)

    elif category == 'running':
        if avg_hr > 0:
            trimp = _hr_trimp(avg_hr)
        else:
            avg_speed = float(activity.get('averageSpeed', 0) or 0)
            if avg_speed > 0:
                pace_s_km = 1000.0 / avg_speed
                threshold_sec = _parse_mmss_to_seconds(config.get('pace_threshold', '5:00'), default_seconds=300)
                intensity = float(threshold_sec) / float(pace_s_km)
                trimp = duration_h * (intensity ** 2) * 100.0
            else:
                trimp = 0.0

    elif category == 'swimming':
        # Natação tem TSS muito menor que corrida/ciclismo (FC mais baixa, menor impacto)
        if avg_hr > 0:
            # Usar HR-TRIMP mas com divisor maior específico para natação
            if avg_hr <= 0 or hr_max <= hr_rest:
                trimp = 0.0
            else:
                hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
                hr_reserve = max(0.0, min(2.0, float(hr_reserve)))
                trimp_raw = float(duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve))
                # Natação: dividir por 9.0 (ao invés de 2.5) para refletir baixo impacto
                trimp = trimp_raw / 9.0
        else:
            # Fallback: usar pace mas com fator de correção agressivo
            distance_m = float(activity.get('distance', 0) or 0)
            if distance_m > 0:
                pace_sec_100m = (duration_sec / distance_m) * 100.0
                threshold_sec = _parse_mmss_to_seconds(config.get('swim_pace_threshold', '2:30'), default_seconds=150)
                intensity = float(threshold_sec) / float(pace_sec_100m)
                trimp = (duration_h * (intensity ** 2) * 100.0) / 3.5
            else:
                trimp = duration_h * 22.0

    else:
        # Para força/outros, usa TRIMP por FC quando disponível
        trimp = _hr_trimp(avg_hr)
    
    return trimp


def _parse_mmss_to_seconds(value: str, default_seconds: int) -> int:
    try:
        if not value:
            return default_seconds
        parts = str(value).strip().split(':')
        if len(parts) != 2:
            return default_seconds
        mm = int(parts[0])
        ss = int(parts[1])
        if mm < 0 or ss < 0 or ss >= 60:
            return default_seconds
        return mm * 60 + ss
    except Exception:
        return default_seconds


def _activity_category(activity: dict) -> str:
    """Categoriza atividade baseada no tipo"""
    activity_type = activity.get('activityType', {})
    if isinstance(activity_type, dict):
        type_key = activity_type.get('typeKey', '').lower()
    else:
        type_key = str(activity_type).lower()

    if type_key in [
        'running', 'treadmill_running', 'track_running', 'trail_running', 'indoor_running', 'virtual_running'
    ]:
        return 'running'
    if type_key in [
        'cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling', 'gravel_cycling', 'virtual_cycling',
        'virtual_ride', 'indoor_biking', 'bike', 'biking', 'e_bike_ride', 'e_mountain_bike_ride',
        'commute_cycling', 'touring_cycling', 'recumbent_cycling', 'cyclocross', 'road_biking',
        'gravel_biking', 'tandem_cycling', 'bmx', 'fat_bike', 'track_cycling', 'spin_bike'
    ]:
        return 'cycling'
    if type_key in ['swimming', 'pool_swimming', 'open_water_swimming', 'indoor_swimming', 'lap_swimming']:
        return 'swimming'
    if type_key in ['strength_training', 'weight_training', 'functional_strength_training', 'gym_strength_training', 'crossfit', 'hiit']:
        return 'strength'
    return 'other'


def compute_tss_variants(activity: dict, config: dict) -> dict:
    """Calcula TSS (power), rTSS (pace), sTSS (swim pace) e hrTSS (HR) quando possível.

    Observação: são aproximações consistentes com o modelo $TSS \\approx horas \\cdot IF^2 \\cdot 100$.
    """
    duration_sec = float(activity.get('duration', 0) or 0)
    if duration_sec <= 0:
        return {
            'tss': 0.0,
            'rtss': 0.0,
            'stss': 0.0,
            'hrtss': 0.0,
            'tss_method': 'none'
        }

    duration_h = duration_sec / 3600.0
    category = _activity_category(activity)

    # Power-based (TSS)
    ftp = float(config.get('ftp', 0) or 0)
    np_power = activity.get('normalizedPower') or activity.get('normPower')
    avg_power = activity.get('averagePower') or activity.get('avgPower')
    power = float(np_power or avg_power or 0)
    tss = 0.0
    if ftp > 0 and power > 0 and category == 'cycling':
        if_ = power / ftp
        tss = duration_h * (if_ ** 2) * 100.0

    # Pace-based running (rTSS)
    rtss = 0.0
    avg_speed = float(activity.get('averageSpeed', 0) or 0)  # m/s
    if avg_speed > 0 and category == 'running':
        threshold_sec_per_km = _parse_mmss_to_seconds(config.get('pace_threshold', '5:00'), default_seconds=300)
        threshold_speed = 1000.0 / float(threshold_sec_per_km)  # m/s
        if threshold_speed > 0:
            if_ = avg_speed / threshold_speed
            # Ajuste: multiplicar por 1.15 para alinhar com TrainingPeaks (valores ~10-15% maiores)
            rtss = duration_h * (if_ ** 2) * 100.0 * 1.15

    # Pace-based swimming (sTSS) – usa avg_speed (m/s) quando disponível
    stss = 0.0
    if avg_speed > 0 and category == 'swimming':
        threshold_sec_per_100m = _parse_mmss_to_seconds(config.get('swim_pace_threshold', '2:30'), default_seconds=150)
        threshold_speed = 100.0 / float(threshold_sec_per_100m)  # m/s
        if threshold_speed > 0:
            if_ = avg_speed / threshold_speed
            # Natação: dividir por 3.5 para refletir menor impacto cardiovascular
            stss = (duration_h * (if_ ** 2) * 100.0) / 3.5

    # HR-based (hrTSS) - Método TrainingPeaks
    # Fórmula: hrTSS = duration_hours × HRR × 0.64 × e^(1.92 × HRR) × 100
    # Onde HRR = (avgHR - hrRest) / (LTHR - hrRest)
    hrtss = 0.0
    
    # Tentar múltiplos campos de FC do Garmin
    avg_hr = (activity.get('averageHR') or 
              activity.get('avgHR') or 
              activity.get('avgHr') or
              activity.get('averageHeartRate') or
              activity.get('avgHeartRate'))
    
    avg_hr = float(avg_hr or 0)
    hr_rest = float(config.get('hr_rest', 50) or 50)
    hr_threshold = float(config.get('hr_threshold', 0) or 0)
    
    if avg_hr > 0 and hr_threshold > hr_rest and avg_hr >= hr_rest:
        # Usar LTHR (hr_threshold) como referência
        hrr = (avg_hr - hr_rest) / (hr_threshold - hr_rest)
        hrr = max(0.0, min(2.0, hrr))  # Limitar entre 0 e 2
        
        import math
        # Fórmula TrainingPeaks: duração em horas × HRR × coeficientes
        raw_hrtss = duration_h * hrr * 0.64 * math.exp(1.92 * hrr) * 100.0
        
        # Para natação, aplicar fator de correção (FC é mais baixa na água)
        if category == 'swimming':
            hrtss = raw_hrtss / 3.5  # Mesma correção que para pace
        else:
            hrtss = raw_hrtss

    # Escolher melhor estimativa para preencher `tss`
    method = 'none'
    chosen = 0.0
    if tss > 0:
        chosen = tss
        method = 'power'
    elif rtss > 0:
        chosen = rtss
        method = 'pace_run'
    elif stss > 0:
        chosen = stss
        method = 'pace_swim'
    elif hrtss > 0:
        chosen = hrtss
        method = 'hr'

    return {
        'tss': float(activity.get('tss', 0) or 0) if float(activity.get('tss', 0) or 0) > 0 else float(chosen),
        'rtss': float(activity.get('rtss', 0) or 0) if float(activity.get('rtss', 0) or 0) > 0 else float(rtss),
        'stss': float(activity.get('stss', 0) or 0) if float(activity.get('stss', 0) or 0) > 0 else float(stss),
        'hrtss': float(activity.get('hrtss', 0) or 0) if float(activity.get('hrtss', 0) or 0) > 0 else float(hrtss),
        'tss_method': activity.get('tss_method') or method
    }

def calculate_modality_progress(activities):
    """Calcula progresso por modalidade agrupado por semana (42 dias)"""
    if not activities:
        return {}

    # Usar a data da atividade mais recente como referência
    if activities:
        most_recent = max(activities, key=lambda x: datetime.strptime(x.get('startTimeLocal', x.get('startTime', '1900-01-01')), "%Y-%m-%d %H:%M:%S"))
        now = datetime.strptime(most_recent.get('startTimeLocal', most_recent.get('startTime', '1900-01-01')), "%Y-%m-%d %H:%M:%S")
    else:
        now = datetime.now()

    start_date = now - timedelta(days=42)

    # Inicializar estrutura de dados
    modalities = ['cycling', 'running', 'swimming', 'strength']
    modality_data = {mod: [] for mod in modalities}

    # Agrupar atividades por modalidade e semana
    for activity in activities:
        try:
            activity_date = datetime.strptime(
                activity.get('startTimeLocal', activity.get('startTime', '1900-01-01')),
                "%Y-%m-%d %H:%M:%S"
            )

            # Pular atividades fora do período de 42 dias
            if activity_date < start_date:
                continue

            # Categorizar atividade
            activity_type = _activity_category(activity)
            if activity_type not in modalities:
                continue

            # Calcular semana (0-5, onde 0 é a semana mais antiga)
            days_diff = (activity_date - start_date).days
            week_num = days_diff // 7

            # Dados da atividade
            distance = float(activity.get('distance', 0) or 0) / 1000  # km
            tss = float(activity.get('tss', 0) or 0)
            duration = float(activity.get('duration', 0) or 0) / 3600  # horas

            # Adicionar à modalidade correspondente
            if week_num < 6:  # Apenas 6 semanas (42 dias)
                modality_data[activity_type].append({
                    'week': week_num,
                    'distance': distance,
                    'tss': tss,
                    'duration': duration,
                    'date': activity_date.date()
                })

        except Exception as e:
            continue

    # Agregar por semana para cada modalidade
    result = {}
    for modality in modalities:
        weekly_data = {}
        for activity in modality_data[modality]:
            week = activity['week']
            if week not in weekly_data:
                weekly_data[week] = {
                    'distance': 0,
                    'tss': 0,
                    'duration': 0,
                    'activities': 0,
                    'week_start': start_date + timedelta(days=week*7)
                }
            weekly_data[week]['distance'] += activity['distance']
            weekly_data[week]['tss'] += activity['tss']
            weekly_data[week]['duration'] += activity['duration']
            weekly_data[week]['activities'] += 1

        # Converter para lista ordenada por semana
        result[modality] = []
        for week in range(6):
            if week in weekly_data:
                result[modality].append(weekly_data[week])
            else:
                result[modality].append({
                    'distance': 0,
                    'tss': 0,
                    'duration': 0,
                    'activities': 0,
                    'week_start': start_date + timedelta(days=week*7)
                })

    return result

def display_modality_progress(modality_progress, modality_key, modality_name):
    """Exibe o progresso de uma modalidade com gráficos Plotly modernos"""
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    data = modality_progress.get(modality_key, [])

    if not data:
        st.info(f"Nenhum dado encontrado para {modality_name}")
        return

    # Criar DataFrame para exibição
    df_data = []
    for i, week_data in enumerate(data):
        week_start = week_data['week_start']
        week_end = week_start + timedelta(days=6)
        df_data.append({
            'Semana': f'{i+1}',
            'Período': f'{week_start.strftime("%d/%m")} - {week_end.strftime("%d/%m")}',
            'Distância (km)': f"{week_data['distance']:.1f}",
            'TSS': f"{week_data['tss']:.0f}",
            'Horas': format_hours_decimal(week_data['duration']),
            'Atividades': week_data['activities']
        })

    df = pd.DataFrame(df_data)

    # Métricas gerais com cards modernos
    total_distance = sum(week_data['distance'] for week_data in data)
    total_tss = sum(week_data['tss'] for week_data in data)
    total_hours = sum(week_data['duration'] for week_data in data)
    total_activities = sum(week_data['activities'] for week_data in data)

    # Cards de métricas com design moderno
    st.markdown(f"""
    <div class='row g-3 mb-4'>
        <div class='col-12 col-md-3'>
            <div class='card border-primary shadow-sm'>
                <div class='card-body text-center p-3'>
                    <div class='text-primary mb-1'><i class='fas fa-route'></i></div>
                    <div class='h5 mb-0 text-primary'>{total_distance:.1f}</div>
                    <small class='text-muted'>Distância Total (km)</small>
                </div>
            </div>
        </div>
        <div class='col-12 col-md-3'>
            <div class='card border-success shadow-sm'>
                <div class='card-body text-center p-3'>
                    <div class='text-success mb-1'><i class='fas fa-bolt'></i></div>
                    <div class='h5 mb-0 text-success'>{total_tss:.0f}</div>
                    <small class='text-muted'>TSS Total</small>
                </div>
            </div>
        </div>
        <div class='col-12 col-md-3'>
            <div class='card border-info shadow-sm'>
                <div class='card-body text-center p-3'>
                    <div class='text-info mb-1'><i class='fas fa-clock'></i></div>
                    <div class='h5 mb-0 text-info'>{format_hours_decimal(total_hours)}</div>
                    <small class='text-muted'>Horas Totais</small>
                </div>
            </div>
        </div>
        <div class='col-12 col-md-3'>
            <div class='card border-warning shadow-sm'>
                <div class='card-body text-center p-3'>
                    <div class='text-warning mb-1'><i class='fas fa-calendar-check'></i></div>
                    <div class='h5 mb-0 text-warning'>{total_activities}</div>
                    <small class='text-muted'>Atividades</small>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabela de progresso semanal com design melhorado
    st.markdown("#### 📅 Progresso Semanal Detalhado")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Semana': st.column_config.TextColumn('Semana', width='small'),
            'Período': st.column_config.TextColumn('Período', width='medium'),
            'Distância (km)': st.column_config.TextColumn('Distância (km)', width='medium'),
            'TSS': st.column_config.TextColumn('TSS', width='small'),
            'Horas': st.column_config.TextColumn('Horas', width='small'),
            'Atividades': st.column_config.TextColumn('Atividades', width='small')
        }
    )

    # Gráfico moderno com subplots
    st.markdown("#### 📈 Evolução Semanal Completa")

    # Preparar dados
    semanas = [f'S{i+1}' for i in range(len(data))]
    distancia = [week['distance'] for week in data]
    tss = [week['tss'] for week in data]
    horas = [week['duration'] for week in data]
    atividades = [week['activities'] for week in data]

    # Criar subplot com 2x2
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distância por Semana', 'TSS por Semana', 'Horas por Semana', 'Atividades por Semana'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )

    # Cores temáticas por modalidade - PADRONIZADAS
    cores_modalidade = {
        'swimming': {'primary': '#007bff', 'secondary': '#cce5ff'},  # Azul - Natação
        'cycling': {'primary': '#28a745', 'secondary': '#d4edda'},   # Verde - Ciclismo
        'running': {'primary': '#fd7e14', 'secondary': '#ffe5d0'},   # Laranja - Corrida
        'strength': {'primary': '#6f42c1', 'secondary': '#e7d9ff'}   # Roxo - Musculação
    }

    cores = cores_modalidade.get(modality_key, {'primary': '#666', 'secondary': '#ccc'})

    # Gráfico 1: Distância
    fig.add_trace(
        go.Bar(
            x=semanas,
            y=distancia,
            name='Distância',
            marker_color=cores['primary'],
            marker_line_color=cores['secondary'],
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Distância: %{y:.1f} km<extra></extra>'
        ),
        row=1, col=1
    )

    # Gráfico 2: TSS
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=tss,
            mode='lines+markers',
            name='TSS',
            line=dict(color=cores['primary'], width=3),
            marker=dict(size=8, color=cores['primary'], symbol='circle'),
            hovertemplate='<b>%{x}</b><br>TSS: %{y:.0f}<extra></extra>'
        ),
        row=1, col=2
    )

    # Gráfico 3: Horas
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=horas,
            mode='lines+markers',
            name='Horas',
            line=dict(color=cores['primary'], width=3, dash='dot'),
            marker=dict(size=8, color=cores['primary'], symbol='square'),
            hovertemplate='<b>%{x}</b><br>Horas: %{customdata}<extra></extra>',
            customdata=[format_hours_decimal(h) for h in horas]
        ),
        row=2, col=1
    )

    # Gráfico 4: Atividades
    fig.add_trace(
        go.Bar(
            x=semanas,
            y=atividades,
            name='Atividades',
            marker_color=cores['secondary'],
            marker_line_color=cores['primary'],
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Atividades: %{y}<extra></extra>'
        ),
        row=2, col=2
    )

    # Configurar layout
    fig.update_layout(
        height=600,
        showlegend=False,
        font=dict(family='Inter, -apple-system, sans-serif', size=11),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Configurar eixos
    fig.update_xaxes(showgrid=False, row=1, col=1)
    fig.update_yaxes(title_text='Distância (km)', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)

    fig.update_xaxes(showgrid=False, row=1, col=2)
    fig.update_yaxes(title_text='TSS', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=2)

    fig.update_xaxes(showgrid=False, row=2, col=1)
    fig.update_yaxes(title_text='Horas', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)

    fig.update_xaxes(showgrid=False, row=2, col=2)
    fig.update_yaxes(title_text='Atividades', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=2)

    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de tendência consolidado
    st.markdown("#### 📊 Tendência Consolidada (42 dias)")

    # Calcular médias móveis para suavizar tendências
    if len(data) >= 3:
        distancia_ma = np.convolve(distancia, np.ones(3)/3, mode='valid').tolist()
        tss_ma = np.convolve(tss, np.ones(3)/3, mode='valid').tolist()
        semanas_ma = semanas[1:-1]  # Ajustar índices para média móvel
    else:
        distancia_ma = distancia
        tss_ma = tss
        semanas_ma = semanas

    # Gráfico de tendência
    fig_tendencia = go.Figure()

    # Área preenchida para distância
    fig_tendencia.add_trace(
        go.Scatter(
            x=semanas,
            y=distancia,
            mode='lines+markers',
            name='Distância (km)',
            line=dict(color=cores['primary'], width=3),
            marker=dict(size=6, color=cores['primary']),
            fill='tozeroy',
            fillcolor='rgba(25, 118, 210, 0.2)',  # Azul com transparência
            hovertemplate='<b>Distância</b><br>Semana %{x}<br>%{y:.1f} km<extra></extra>'
        )
    )

    # Linha para TSS
    fig_tendencia.add_trace(
        go.Scatter(
            x=semanas,
            y=tss,
            mode='lines+markers',
            name='TSS',
            line=dict(color=cores['secondary'], width=3, dash='dash'),
            marker=dict(size=6, color=cores['secondary'], symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>TSS</b><br>Semana %{x}<br>%{y:.0f}<extra></extra>'
        )
    )

    # Configurar layout com eixo duplo
    fig_tendencia.update_layout(
        title=f'Tendência de Progresso - {modality_name}',
        height=400,
        font=dict(family='Inter, -apple-system, sans-serif', size=12),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        yaxis=dict(
            title='Distância (km)',
            tickfont=dict(color=cores['primary'])
        ),
        yaxis2=dict(
            title='TSS',
            tickfont=dict(color=cores['secondary']),
            anchor='x',
            overlaying='y',
            side='right'
        )
    )

    fig_tendencia.update_xaxes(showgrid=False)
    fig_tendencia.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')

    st.plotly_chart(fig_tendencia, use_container_width=True)

def calculate_goals_progress(activities, config):
    """Calcula progresso das metas baseado nas atividades"""
    if not activities:
        return {
            'weekly': {'distance': 0, 'tss': 0, 'hours': 0, 'activities': 0},
            'monthly': {'distance': 0, 'tss': 0, 'hours': 0, 'activities': 0},
            'current_ctl': 0,
            'current_atl': 0
        }

    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)  # Monday at 00:00
    month_start = now.replace(day=1)

    weekly_activities = []
    monthly_activities = []

    for activity in activities:
        try:
            activity_date = datetime.strptime(
                activity.get('startTimeLocal', activity.get('startTime', '1900-01-01')),
                "%Y-%m-%d %H:%M:%S"
            )

            if activity_date >= week_start:
                weekly_activities.append(activity)
            if activity_date >= month_start:
                monthly_activities.append(activity)
        except:
            continue

    def calculate_metrics(activity_list):
        total_distance = sum(float(a.get('distance', 0) or 0) / 1000 for a in activity_list)  # km
        total_tss = sum(float(a.get('tss', 0) or 0) for a in activity_list)
        total_hours = sum(float(a.get('duration', 0) or 0) / 3600 for a in activity_list)
        total_activities = len(activity_list)
        return {
            'distance': total_distance,
            'tss': total_tss,
            'hours': total_hours,
            'activities': total_activities
        }

    weekly_metrics = calculate_metrics(weekly_activities)
    monthly_metrics = calculate_metrics(monthly_activities)

    # Calcular CTL e ATL atuais (último valor disponível)
    metrics = load_metrics()
    current_ctl = metrics[-1]['ctl'] if metrics else 0
    current_atl = metrics[-1]['atl'] if metrics else 0

    return {
        'weekly': weekly_metrics,
        'monthly': monthly_metrics,
        'current_ctl': current_ctl,
        'current_atl': current_atl
    }

def calculate_fitness_metrics(activities, config, start_date, end_date):
    """Calcula métricas de fitness (CTL, ATL, TSB) baseadas nas atividades"""
    # Agrupar TRIMP por data
    daily_loads = {}
    for activity in activities:
        start_time = activity.get('startTimeLocal', '')
        if start_time:
            try:
                # startTimeLocal pode ser "2025-12-21 11:43:55" ou com Z
                if 'T' not in start_time:
                    start_time = start_time.replace(' ', 'T')
                if not start_time.endswith('Z'):
                    start_time += 'Z'
                date = datetime.fromisoformat(start_time.replace('Z', '+00:00')).date()
                trimp = calculate_trimp(activity, config)
                daily_loads[date] = daily_loads.get(date, 0) + trimp
            except ValueError as e:
                print(f"Erro ao parsear data {start_time}: {e}")
                continue
    
    # Lista de dias
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    # Calcular CTL, ATL
    ctl = 0
    atl = 0
    metrics = []
    for date in days:
        load = daily_loads.get(date, 0)
        ctl = ctl + (load - ctl) / 42
        atl = atl + (load - atl) / 7
        tsb = ctl - atl
        metrics.append({
            'date': date.isoformat(),
            'daily_load': load,
            'ctl': ctl,
            'atl': atl,
            'tsb': tsb
        })
    return metrics
    """Calcula métricas de fitness (CTL, ATL, TSB) baseado em atividades"""
    daily_loads = {}

    def _activity_date(a: dict):
        from datetime import datetime as dt
        if a.get('startTimeLocal'):
            try:
                return dt.strptime(a['startTimeLocal'], '%Y-%m-%d %H:%M:%S').date()
            except Exception:
                pass
        if a.get('startTimeGMT'):
            try:
                return dt.strptime(a['startTimeGMT'], '%Y-%m-%d %H:%M:%S').date()
            except Exception:
                pass
        if a.get('startTimeInSeconds'):
            try:
                return dt.fromtimestamp(a['startTimeInSeconds']).date()
            except Exception:
                pass
        return None

    for activity in activities:
        date = _activity_date(activity)
        if not date:
            continue
        trimp = calculate_trimp(activity, config)
        daily_loads[date] = daily_loads.get(date, 0) + trimp
    
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    ctl = 0
    atl = 0
    metrics = []
    for date in days:
        load = daily_loads.get(date, 0)
        ctl = ctl + (load - ctl) / 42
        atl = atl + (load - atl) / 7
        tsb = ctl - atl
        metrics.append({
            'date': date.isoformat(),
            'daily_load': load,
            'ctl': ctl,
            'atl': atl,
            'tsb': tsb
        })
    
    return metrics

def fetch_garmin_data(email, password, config):
    """Busca dados do Garmin Connect com lógica inteligente de atualização"""
    try:
        from garminconnect import Garmin
        client = Garmin(email, password)
        client.login()

        end_date = datetime.now().date()

        # Carregar histórico salvo
        old_activities = load_workouts()

        if not old_activities:
            # Se não há dados armazenados, buscar os últimos 42 dias
            start_date = end_date - timedelta(days=42)
            fetch_start_date = start_date
            print(f"🔄 Nenhum dado armazenado. Buscando últimos 42 dias: {start_date} até {end_date}")
        else:
            # Se há dados, pegar o último dia mais atualizado, subtrair 1 dia e buscar até hoje
            # Encontrar a data mais recente dos dados armazenados
            latest_dates = []
            for a in old_activities:
                start_time = a.get('startTimeLocal', a.get('startTime', ''))
                if start_time:
                    try:
                        if 'T' in start_time:
                            date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                        else:
                            date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()
                        latest_dates.append(date_obj)
                    except:
                        continue

            if latest_dates:
                most_recent_date = max(latest_dates)
                # Subtrair 1 dia da data mais recente
                fetch_start_date = most_recent_date - timedelta(days=1)
                print(f"🔄 Dados existentes até {most_recent_date}. Buscando de {fetch_start_date} até {end_date}")
            else:
                # Fallback para 42 dias se não conseguir parsear datas
                fetch_start_date = end_date - timedelta(days=42)
                print(f"⚠️ Não foi possível determinar data dos dados existentes. Buscando últimos 42 dias.")

        # Buscar atividades do período determinado
        if fetch_start_date <= end_date:
            new_activities = client.get_activities_by_date(
                fetch_start_date.isoformat(),
                end_date.isoformat()
            )
            print(f"📊 Encontradas {len(new_activities)} atividades no Garmin")
        else:
            new_activities = []
            print("📊 Nenhuma nova data para buscar")

        # Unir atividades antigas com novas, sobrescrevendo duplicatas
        # Usar activityId ou startTimeLocal como chave única
        activities_dict = {}

        # Primeiro, adicionar atividades antigas
        for a in old_activities:
            key = a.get('activityId') or a.get('activityUUID') or a.get('startTimeLocal') or a.get('startTime')
            if key:
                activities_dict[key] = a

        # Depois, adicionar/sobrescrever com atividades novas
        for a in new_activities:
            key = a.get('activityId') or a.get('activityUUID') or a.get('startTimeLocal') or a.get('startTime')
            if key:
                activities_dict[key] = a

        # Converter de volta para lista
        all_activities = list(activities_dict.values())
        print(f"📊 Total de atividades únicas após merge: {len(all_activities)}")

        # Enriquecer atividades com TSS variants (sempre recalcular)
        enriched_activities = []
        for a in all_activities:
            a2 = dict(a)
            tss_data = compute_tss_variants(a2, config)
            # SEMPRE recalcular para garantir que usa a config mais recente
            for k, v in tss_data.items():
                a2[k] = v
            enriched_activities.append(a2)

        # Salvar TODAS as atividades (não filtrar por 42 dias aqui)
        save_workouts(enriched_activities)

        # Para métricas do Dashboard, usar apenas os últimos 42 dias
        dashboard_cutoff = end_date - timedelta(days=42)
        dashboard_activities = []
        for a in enriched_activities:
            start_time = a.get('startTimeLocal', a.get('startTime', ''))
            if start_time:
                try:
                    if 'T' in start_time:
                        activity_date = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                    else:
                        activity_date = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()

                    if activity_date >= dashboard_cutoff:
                        dashboard_activities.append(a)
                except:
                    # Se não conseguir parsear, incluir na dúvida
                    dashboard_activities.append(a)

        print(f"📊 Atividades para Dashboard (últimos 42 dias): {len(dashboard_activities)}")

        # Calcular métricas apenas com dados dos últimos 42 dias
        metrics = calculate_fitness_metrics(dashboard_activities, config, dashboard_cutoff, end_date)
        save_metrics(metrics)

        new_count = len(new_activities)
        total_count = len(enriched_activities)
        dashboard_count = len(dashboard_activities)

        return True, f"✅ Dados atualizados! {new_count} novas atividades, {total_count} total armazenadas, {dashboard_count} para Dashboard (42 dias)."

    except ImportError:
        return False, "❌ Erro: garminconnect não instalado. Instale com: pip install garminconnect"
    except Exception as e:
        return False, f"❌ Erro ao buscar dados: {str(e)}"

# Inicializar session state
if 'update_status' not in st.session_state:
    st.session_state.update_status = None

# Sidebar - Navegação
st.sidebar.title("📱 Fitness Metrics")
page = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📅 Calendário", "🎯 Metas", "⚙️ Configuração"]
)

# PAGE 1: DASHBOARD
if page == "📊 Dashboard":
    st.title("📊 Dashboard de Fitness")

    metrics = load_metrics_cached()

    if not metrics:
        st.warning("⚠️ Nenhum dado disponível. Vá para 'Atualizar Dados' para sincronizar com Garmin Connect.")
    else:
        last_metric = metrics[-1]
        
        # Calcular variação em relação a 7 dias atrás
        prev_metric = metrics[-8] if len(metrics) >= 8 else metrics[0]
        
        ctl_change = ((last_metric['ctl'] - prev_metric['ctl']) / prev_metric['ctl'] * 100) if prev_metric['ctl'] > 0 else 0
        atl_change = ((last_metric['atl'] - prev_metric['atl']) / prev_metric['atl'] * 100) if prev_metric['atl'] > 0 else 0
        tsb_change = ((last_metric['tsb'] - prev_metric['tsb']) / abs(prev_metric['tsb']) * 100) if prev_metric['tsb'] != 0 else 0
        
        # Símbolos de tendência
        ctl_arrow = "📈" if ctl_change > 0 else "📉" if ctl_change < 0 else "➡️"
        atl_arrow = "📈" if atl_change > 0 else "📉" if atl_change < 0 else "➡️"
        tsb_arrow = "📈" if tsb_change > 0 else "📉" if tsb_change < 0 else "➡️"
        
        # ============ STATUS ATUAL: ONDE VOCÊ ESTÁ ============
        st.markdown("## 🎯 Status Atual: Onde Você Está")
        st.markdown("*Seu estado de forma física atual e tendências recentes*")
        
        # ============ CARDS DE MÉTRICAS PRINCIPAIS NO TOPO ============
        st.markdown(f"""
        <div class='container' style='margin:30px auto 40px auto;max-width:1200px;'>
            <div class='row justify-content-center g-4'>
                <div class='col-12 col-md-4'>
                    <div class='card' style='background:#fff;border:3px solid #667eea;box-shadow:0 8px 32px rgba(102,126,234,0.2);border-radius:16px;'>
                        <div class='card-body text-center p-4'>
                            <div style='font-size:1rem;color:#667eea;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>💪 Fitness (CTL)</div>
                            <div style='font-size:4rem;font-weight:900;color:#667eea;margin:20px 0;line-height:1;'>{last_metric['ctl']:.0f}</div>
                            <div style='font-size:1rem;color:#495057;font-weight:600;background:#f8f9fa;padding:8px 16px;border-radius:20px;display:inline-block;'>
                                <span style='font-size:1.3rem;'>{ctl_arrow}</span> {ctl_change:+.1f}% vs semana anterior
                            </div>
                        </div>
                    </div>
                </div>
                <div class='col-12 col-md-4'>
                    <div class='card' style='background:#fff;border:3px solid #f5576c;box-shadow:0 8px 32px rgba(245,87,108,0.2);border-radius:16px;'>
                        <div class='card-body text-center p-4'>
                            <div style='font-size:1rem;color:#f5576c;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>😴 Fadiga (ATL)</div>
                            <div style='font-size:4rem;font-weight:900;color:#f5576c;margin:20px 0;line-height:1;'>{last_metric['atl']:.0f}</div>
                            <div style='font-size:1rem;color:#495057;font-weight:600;background:#f8f9fa;padding:8px 16px;border-radius:20px;display:inline-block;'>
                                <span style='font-size:1.3rem;'>{atl_arrow}</span> {atl_change:+.1f}% vs semana anterior
                            </div>
                        </div>
                    </div>
                </div>
                <div class='col-12 col-md-4'>
                    <div class='card' style='background:#fff;border:3px solid #00f2fe;box-shadow:0 8px 32px rgba(0,242,254,0.2);border-radius:16px;'>
                        <div class='card-body text-center p-4'>
                            <div style='font-size:1rem;color:#00b8d4;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>⚖️ Forma (TSB)</div>
                            <div style='font-size:4rem;font-weight:900;color:#00b8d4;margin:20px 0;line-height:1;'>{last_metric['tsb']:.0f}</div>
                            <div style='font-size:1rem;color:#495057;font-weight:600;background:#f8f9fa;padding:8px 16px;border-radius:20px;display:inline-block;'>
                                <span style='font-size:1.3rem;'>{tsb_arrow}</span> {tsb_change:+.1f}% vs semana anterior
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ OBJETIVOS: PARA ONDE VOCÊ VAI ============
        st.markdown("## 🎯 Objetivos: Para Onde Você Vai")
        st.markdown("*Seus objetivos de treinamento e progresso atual*")
        
        # Carregar dados para calcular progresso
        workouts = load_workouts()
        config = load_config()
        
        goals_progress = calculate_goals_progress(workouts, config)
        
        # Cards de progresso semanal
        st.markdown("#### 📅 Progresso Semanal")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            weekly_distance = goals_progress['weekly']['distance']
            weekly_distance_goal = config.get('weekly_distance_goal', 50.0)
            distance_pct = min(100, (weekly_distance / weekly_distance_goal * 100) if weekly_distance_goal > 0 else 0)
            st.metric(
                "🏃 Distância",
                f"{weekly_distance:.1f}km / {weekly_distance_goal:.0f}km",
                f"{distance_pct:.1f}%"
            )
            st.progress(distance_pct / 100)
        
        with col2:
            weekly_tss = goals_progress['weekly']['tss']
            weekly_tss_goal = config.get('weekly_tss_goal', 300)
            tss_pct = min(100, (weekly_tss / weekly_tss_goal * 100) if weekly_tss_goal > 0 else 0)
            st.metric(
                "🎯 TSS",
                f"{weekly_tss:.0f} / {weekly_tss_goal}",
                f"{tss_pct:.1f}%"
            )
            st.progress(tss_pct / 100)
        
        with col3:
            weekly_hours = goals_progress['weekly']['hours']
            weekly_hours_goal = config.get('weekly_hours_goal', 7.0)
            hours_pct = min(100, (weekly_hours / weekly_hours_goal * 100) if weekly_hours_goal > 0 else 0)
            st.metric(
                "⏱️ Horas",
                f"{format_hours_decimal(weekly_hours)} / {format_hours_decimal(weekly_hours_goal)}",
                f"{hours_pct:.1f}%"
            )
            st.progress(hours_pct / 100)
        
        with col4:
            weekly_activities = goals_progress['weekly']['activities']
            weekly_activities_goal = config.get('weekly_activities_goal', 5)
            activities_pct = min(100, (weekly_activities / weekly_activities_goal * 100) if weekly_activities_goal > 0 else 0)
            st.metric(
                "📊 Atividades",
                f"{weekly_activities} / {weekly_activities_goal}",
                f"{activities_pct:.1f}%"
            )
            st.progress(activities_pct / 100)
        
        # Cards de progresso mensal
        st.markdown("#### 📊 Progresso Mensal")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            monthly_distance = goals_progress['monthly']['distance']
            monthly_distance_goal = config.get('monthly_distance_goal', 200.0)
            distance_pct = min(100, (monthly_distance / monthly_distance_goal * 100) if monthly_distance_goal > 0 else 0)
            st.metric(
                "🏃 Distância",
                f"{monthly_distance:.1f}km / {monthly_distance_goal:.0f}km",
                f"{distance_pct:.1f}%"
            )
            st.progress(distance_pct / 100)
        
        with col2:
            monthly_tss = goals_progress['monthly']['tss']
            monthly_tss_goal = config.get('monthly_tss_goal', 1200)
            tss_pct = min(100, (monthly_tss / monthly_tss_goal * 100) if monthly_tss_goal > 0 else 0)
            st.metric(
                "🎯 TSS",
                f"{monthly_tss:.0f} / {monthly_tss_goal}",
                f"{tss_pct:.1f}%"
            )
            st.progress(tss_pct / 100)
        
        with col3:
            monthly_hours = goals_progress['monthly']['hours']
            monthly_hours_goal = config.get('monthly_hours_goal', 30.0)
            hours_pct = min(100, (monthly_hours / monthly_hours_goal * 100) if monthly_hours_goal > 0 else 0)
            st.metric(
                "⏱️ Horas",
                f"{format_hours_decimal(monthly_hours)} / {format_hours_decimal(monthly_hours_goal)}",
                f"{hours_pct:.1f}%"
            )
            st.progress(hours_pct / 100)
        
        with col4:
            monthly_activities = goals_progress['monthly']['activities']
            monthly_activities_goal = config.get('monthly_activities_goal', 20)
            activities_pct = min(100, (monthly_activities / monthly_activities_goal * 100) if monthly_activities_goal > 0 else 0)
            st.metric(
                "📊 Atividades",
                f"{monthly_activities} / {monthly_activities_goal}",
                f"{activities_pct:.1f}%"
            )
            st.progress(activities_pct / 100)
        
        # Metas de performance
        st.markdown("#### 🏆 Metas de Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            current_ctl = goals_progress['current_ctl']
            target_ctl = config.get('target_ctl', 50)
            ctl_pct = min(100, (current_ctl / target_ctl * 100) if target_ctl > 0 else 0)
            status_emoji = "✅" if current_ctl >= target_ctl else "🎯"
            st.metric(
                f"{status_emoji} CTL Atual vs Alvo",
                f"{current_ctl:.1f} / {target_ctl}",
                f"{ctl_pct:.1f}%"
            )
            st.progress(ctl_pct / 100)
        
        with col2:
            current_atl = goals_progress['current_atl']
            target_atl_max = config.get('target_atl_max', 80)
            atl_pct = min(100, (current_atl / target_atl_max * 100) if target_atl_max > 0 else 0)
            status_emoji = "⚠️" if current_atl > target_atl_max else "✅"
            st.metric(
                f"{status_emoji} ATL vs Máximo",
                f"{current_atl:.1f} / {target_atl_max}",
                f"{atl_pct:.1f}%"
            )
            st.progress(atl_pct / 100)
            if current_atl > target_atl_max:
                st.warning("⚠️ Atenção: Fadiga acima do limite recomendado!")

        from datetime import datetime as dt

        # ============ TREINAMENTO: COMO CHEGAR LÁ ============
        st.markdown("## 🏃 Treinamento: Como Chegar Lá")
        st.markdown("*Suas zonas de intensidade e atividade semanal*")
        config_z = load_config()
        hr_max = float(config_z.get('hr_max', 191))
        hr_rest = float(config_z.get('hr_rest', 50))
        hr_lthr = float(config_z.get('hr_threshold', 162))
        ftp = float(config_z.get('ftp', 260))  # FTP padrão 260
        pace_thr_str = str(config_z.get('pace_threshold', '4:22'))
        def parse_pace(pace_str):
            try:
                min_, sec = map(int, pace_str.strip().split(':'))
                return min_ * 60 + sec
            except:
                return 300  # default 5:00
        pace_thr = parse_pace(pace_thr_str)


        # Zonas de Corrida (em pace min/km)
        def parse_pace(pace_str):
            try:
                min_, sec = map(int, pace_str.strip().split(':'))
                return min_ * 60 + sec
            except:
                return 300  # default 5:00

        pace_thr = parse_pace(str(config_z.get('pace_threshold', '5:00')))
        # Zonas de Corrida DINÂMICAS conforme pace_threshold
        # Limites em segundos: Z1: >338, Z2: 338-299, Z3: 299-278, Z4: 278-262, Z5a: 262-254, Z5b: 254-235, Z5c: <235
        # Base: pace_thr (em segundos)
        corrida_zonas = [
            ("Z1", pace_thr+76, 9999, "Recuperação"),
            ("Z2", pace_thr+17, pace_thr+76, "Endurance"),
            ("Z3", pace_thr-4, pace_thr+17, "Tempo"),
            ("Z4", pace_thr-20, pace_thr-4, "Limiar"),
            ("Z5a", pace_thr-28, pace_thr-20, "VO2max (a)"),
            ("Z5b", pace_thr-47, pace_thr-28, "VO2max (b)"),
            ("Z5c", 1, pace_thr-47, "Sprint / Anaeróbio"),
        ]
        def pace_str(s):
            m = int(s // 60)
            s = int(s % 60)
            return f"{m}:{s:02d}"
        corrida_rows = []
        for z, s_ini, s_fim, desc in corrida_zonas:
            if s_ini > s_fim:
                corrida_rows.append(f"<tr><td>{z}</td><td>> {pace_str(s_fim)} min/km</td><td>{desc}</td></tr>")
            elif s_fim > 900:
                corrida_rows.append(f"<tr><td>{z}</td><td>< {pace_str(s_ini)} min/km</td><td>{desc}</td></tr>")
            else:
                corrida_rows.append(f"<tr><td>{z}</td><td>{pace_str(s_ini)} - {pace_str(s_fim)} min/km</td><td>{desc}</td></tr>")

        # Zonas de Ciclismo (em watts)
        # Zonas de Ciclismo DINÂMICAS conforme FTP
        # Limites: Z1: 0-0.50*ftp, Z2: 0.51-0.68*ftp, Z3: 0.69-0.82*ftp, Z4: 0.83-0.95*ftp, Z5: 0.96-1.09*ftp, Z6: 1.10-2.00*ftp
        ciclismo_zonas = [
            ("Z1", 0, 0.50, "Recuperação Ativa"),
            ("Z2", 0.51, 0.68, "Endurance"),
            ("Z3", 0.69, 0.82, "Tempo"),
            ("Z4", 0.83, 0.95, "Limiar"),
            ("Z5", 0.96, 1.09, "VO2max"),
            ("Z6", 1.10, 2.00, "Anaeróbio / Sprint"),
        ]
        ciclismo_rows = []
        for z, f_ini, f_fim, desc in ciclismo_zonas:
            w_ini = int(round(ftp * f_ini))
            w_fim = int(round(ftp * f_fim))
            ciclismo_rows.append(f"<tr><td>{z}</td><td>{w_ini}-{w_fim} W</td><td>{desc}</td></tr>")

        st.markdown(f"""
        <div class='container' style='max-width:900px;margin:0 auto 32px auto;'>
            <div class='row'>
                <div class='col-12 col-md-6'>
                    <div class='card' style='border:2px solid #0d6efd;border-radius:14px;'>
                        <div class='card-body'>
                            <h3 style='color:#0d6efd;font-weight:700;'>🏃‍♂️ Zonas de Corrida (pace)</h3>
                            <table class='table table-striped' style='font-size:0.98rem;'>
                                <thead><tr><th>Zona</th><th>Faixa (min/km)</th><th>Descrição</th></tr></thead>
                                <tbody>{''.join(corrida_rows)}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class='col-12 col-md-6'>
                    <div class='card' style='border:2px solid #00b8d4;border-radius:14px;'>
                        <div class='card-body'>
                            <h3 style='color:#00b8d4;font-weight:700;'>🚴‍♂️ Zonas de Ciclismo (W)</h3>
                            <table class='table table-striped' style='font-size:0.98rem;'>
                                <thead><tr><th>Zona</th><th>Faixa (W)</th><th>Descrição</th></tr></thead>
                                <tbody>{''.join(ciclismo_rows)}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Calcular início e fim da semana atual
        hoje = datetime.now()
        inicio_semana = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        fim_semana = (inicio_semana + timedelta(days=6)).replace(hour=23, minute=59, second=59)
        
        st.markdown(f"""
        <div class='container' style='margin-bottom:18px;'>
            <div class='row'>
                <div class='col text-center'>
                    <h4 style='font-weight:600;margin-bottom:2px;'>Resumo Semanal</h4>
                    <span style='color:#888;font-size:15px;'>
                        {inicio_semana.day} a {fim_semana.day} de {fim_semana.strftime('%B')} de {fim_semana.year}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtrar treinos da semana
        workouts_semana = load_workouts()
        treinos_semana = []
        for w in workouts_semana:
            data = None
            if w.get('startTimeLocal'):
                try:
                    data = dt.strptime(w['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                except:
                    pass
            elif w.get('startTimeGMT'):
                try:
                    data = dt.strptime(w['startTimeGMT'], '%Y-%m-%d %H:%M:%S')
                except:
                    pass
            elif w.get('startTimeInSeconds'):
                data = dt.fromtimestamp(w['startTimeInSeconds'])
            
            if data and inicio_semana <= data <= fim_semana:
                treinos_semana.append({'workout': w, 'data': data})
        
        # Horas completadas
        def format_horas(horas_decimais):
            """Converte horas decimais para formato hh:mm:ss"""
            total_segundos = int(horas_decimais * 3600)
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            segundos = total_segundos % 60
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        
        horas_completadas = sum(t['workout'].get('duration',0)/3600 for t in treinos_semana)
        # TSS (calculado se não existir)
        tss_total = 0.0
        tss_totais_por_tipo = {'tss': 0.0, 'rtss': 0.0, 'stss': 0.0, 'hrtss': 0.0}
        config = load_config()  # Carregar config para usar nos cálculos
        for t in treinos_semana:
            w = t['workout']
            tss_calc = compute_tss_variants(w, config)
            # Atualiza o dict local para reuso nas outras visualizações
            for k, v in tss_calc.items():
                w[k] = v
            tss_total += float(w.get('tss', 0) or 0)
            for k in tss_totais_por_tipo.keys():
                tss_totais_por_tipo[k] += float(w.get(k, 0) or 0)
        
        # Cards de resumo
        st.markdown(f"""
        <div class='row justify-content-center' style='margin-bottom:15px;'>
            <div class='col-auto'>
                <div class='card shadow-sm text-center' style='min-width:140px;'>
                    <div class='card-body p-3'>
                        <div style='font-size:14px;color:#0d6efd;font-weight:600;'>Horas Completadas</div>
                        <div style='font-size:26px;font-weight:700;'>{format_horas(horas_completadas)}</div>
                    </div>
                </div>
            </div>
            <div class='col-auto'>
                <div class='card shadow-sm text-center' style='min-width:140px;'>
                    <div class='card-body p-3'>
                        <div style='font-size:14px;color:#dc3545;font-weight:600;'>TSS Semanal</div>
                        <div style='font-size:26px;font-weight:700;'>{tss_total:.0f}</div>
                    </div>
                </div>
            </div>
            <div class='col-auto'>
                <div class='card shadow-sm text-center' style='min-width:140px;'>
                    <div class='card-body p-3'>
                        <div style='font-size:14px;color:#20c997;font-weight:600;'>Treinos</div>
                        <div style='font-size:26px;font-weight:700;'>{len(treinos_semana)}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ GRÁFICO SEMANAL MODERNO (PLOTLY) ============
        st.markdown("### 📊 Treinos da Semana (Horas por Dia)")

        import plotly.graph_objects as go

        # Preparar dados para o gráfico
        dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        tipos_cores = {
            'natacao': '#007bff',    # Azul - Natação
            'ciclismo': '#28a745',  # Verde - Ciclismo
            'corrida': '#fd7e14',   # Laranja - Corrida
            'forca': '#6f42c1',     # Roxo - Musculação
            'outros': '#6c757d'
        }

        valores_por_tipo = {tipo: [0]*7 for tipo in tipos_cores.keys()}

        for t in treinos_semana:
            idx = t['data'].weekday()
            tipo = t['workout'].get('activityType', {}).get('typeKey', '').lower()
            dur = t['workout'].get('duration',0)/3600

            if tipo in ['running', 'treadmill_running', 'track_running', 'trail_running', 'indoor_running', 'virtual_running']:
                valores_por_tipo['corrida'][idx] += dur
            elif tipo in ['cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling', 'gravel_cycling', 'virtual_cycling',
                        'virtual_ride', 'indoor_biking', 'bike', 'biking', 'e_bike_ride', 'e_mountain_bike_ride']:
                valores_por_tipo['ciclismo'][idx] += dur
            elif tipo in ['swimming', 'pool_swimming', 'open_water_swimming', 'indoor_swimming', 'lap_swimming']:
                valores_por_tipo['natacao'][idx] += dur
            elif tipo in ['strength_training', 'weight_training', 'functional_strength_training', 'gym_strength_training', 'crossfit', 'hiit']:
                valores_por_tipo['forca'][idx] += dur
            else:
                valores_por_tipo['outros'][idx] += dur

        # Criar gráfico de barras empilhadas com Plotly
        fig_semana = go.Figure()

        # Adicionar barras para cada tipo
        labels_legendas = {'corrida': '🏃 Corrida', 'ciclismo': '🚴 Ciclismo', 'natacao': '🏊 Natação', 'forca': '💪 Força', 'outros': '⚽ Outros'}
        for tipo, cor in tipos_cores.items():
            valores = valores_por_tipo[tipo]
            if sum(valores) > 0:  # Só adicionar se houver valores
                fig_semana.add_trace(go.Bar(
                    name=labels_legendas[tipo],
                    x=dias,
                    y=valores,
                    marker_color=cor,
                    hovertemplate='<b>%{fullData.name}</b><br>Dia: %{x}<br>Horas: %{y:.2f}h<extra></extra>'
                ))

        # Calcular totais por dia para mostrar no hover
        totais_por_dia = [sum(valores_por_tipo[tipo][i] for tipo in tipos_cores.keys()) for i in range(7)]

        # Configurar layout
        fig_semana.update_layout(
            barmode='stack',
            title={
                'text': f'Treinos da Semana ({inicio_semana.day}-{fim_semana.day} {fim_semana.strftime("%b")})',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16, 'color': '#212529'}
            },
            xaxis_title='Dia da Semana',
            yaxis_title='Horas de Treino',
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5,
                font={'size': 11}
            ),
            margin=dict(l=50, r=50, t=80, b=100)
        )

        # Adicionar grid e melhorar aparência
        fig_semana.update_xaxes(showgrid=False, gridcolor='rgba(0,0,0,0.1)')
        fig_semana.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')

        # Adicionar anotações com totais
        for i, total in enumerate(totais_por_dia):
            if total > 0:
                fig_semana.add_annotation(
                    x=dias[i],
                    y=total + 0.1,
                    text=format_horas(total),
                    showarrow=False,
                    font=dict(size=10, color='#495057', weight='bold'),
                    align='center'
                )

        st.plotly_chart(fig_semana, use_container_width=True)

        # ============ GRÁFICO DE PIZZA: TIPOS DE TREINO ÚLTIMA SEMANA ============
        st.markdown("### 🥧 Distribuição dos Tipos de Treino (Última Semana)")
        workouts = load_workouts()
        from datetime import datetime as dt, timedelta as td
        if workouts:
            hoje = datetime.now()
            uma_semana_atras = hoje - td(days=7)
            tipos = {'corrida': 0, 'ciclismo': 0, 'natacao': 0, 'forca': 0, 'outros': 0}
            horas = {'corrida': 0, 'ciclismo': 0, 'natacao': 0, 'forca': 0, 'outros': 0}
            for w in workouts:
                data = None
                if w.get('startTimeLocal'):
                    try:
                        data = dt.strptime(w['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                elif w.get('startTimeGMT'):
                    try:
                        data = dt.strptime(w['startTimeGMT'], '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                elif w.get('startTimeInSeconds'):
                    data = dt.fromtimestamp(w['startTimeInSeconds'])
                if data and data >= uma_semana_atras:
                    tipo = w.get('activityType', {}).get('typeKey', '').lower()
                    dur = w.get('duration', 0) / 3600
                    if tipo in [
                        'running', 'treadmill_running', 'track_running', 'trail_running', 'indoor_running', 'virtual_running']:
                        tipos['corrida'] += 1
                        horas['corrida'] += dur
                    elif tipo in [
                        'cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling', 'gravel_cycling', 'virtual_cycling',
                        'virtual_ride', 'indoor_biking', 'bike', 'biking', 'e_bike_ride', 'e_mountain_bike_ride', 'commute_cycling', 'touring_cycling', 'recumbent_cycling', 'cyclocross', 'road_biking', 'mountain_biking', 'gravel_biking', 'tandem_cycling', 'bmx', 'fat_bike', 'track_cycling', 'spin_bike']:
                        tipos['ciclismo'] += 1
                        horas['ciclismo'] += dur
                    elif tipo in [
                        'swimming', 'pool_swimming', 'open_water_swimming', 'indoor_swimming', 'lap_swimming']:
                        tipos['natacao'] += 1
                        horas['natacao'] += dur
                    elif tipo in [
                        'strength_training', 'weight_training', 'functional_strength_training', 'gym_strength_training', 'crossfit', 'hiit']:
                        tipos['forca'] += 1
                        horas['forca'] += dur
                    else:
                        tipos['outros'] += 1
                        horas['outros'] += dur
            # ============ GRÁFICO MODERNO DE DISTRIBUIÇÃO (PLOTLY) ============
            # Ordenar do maior para o menor por horas
            dados = [
                (k, horas[k], tipos[k]) for k in tipos.keys() if tipos[k] > 0
            ]
            dados.sort(key=lambda x: x[1], reverse=True)

            labels_map = {
                'corrida': '🏃 Corrida',
                'ciclismo': '🚴 Ciclismo',
                'natacao': '🏊 Natação',
                'forca': '💪 Força',
                'outros': '⚽ Outros'
            }

            labels = [labels_map[k] for k, _, _ in dados]
            horas_list = [h for _, h, _ in dados]
            atividades_list = [a for _, _, a in dados]

            # Mapeamento de cores padronizadas por modalidade
            cores_por_tipo = {
                'corrida': '#fd7e14',    # Laranja - Corrida
                'ciclismo': '#28a745',  # Verde - Ciclismo
                'natacao': '#007bff',   # Azul - Natação
                'forca': '#6f42c1',     # Roxo - Musculação
                'outros': '#6c757d'     # Cinza - Outros
            }

            # Aplicar cores na ordem dos dados ordenados
            cores_plotly = [cores_por_tipo[k] for k, _, _ in dados]

            # Criar gráfico de barras horizontais com Plotly
            fig_dist = go.Figure()

            fig_dist.add_trace(go.Bar(
                x=horas_list,
                y=labels,
                orientation='h',
                marker=dict(
                    color=cores_plotly[:len(labels)],
                    line=dict(width=0)
                ),
                text=[f'{format_horas(h)}<br>{a} atividades' for h, a in zip(horas_list, atividades_list)],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Horas: %{x:.2f}h (%{text})<extra></extra>'
            ))

            # Calcular total
            total_horas = sum(horas_list)
            total_horas_str = format_horas(total_horas)

            # Configurar layout
            fig_dist.update_layout(
                title={
                    'text': f'Distribuição dos Tipos de Treino<br><span style="font-size:14px;color:#6c757d;">Total: {total_horas_str} | {sum(atividades_list)} atividades</span>',
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 16, 'color': '#212529'}
                },
                xaxis_title='Horas (hh:mm:ss)',
                font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
                plot_bgcolor='rgba(248,249,250,0.5)',
                paper_bgcolor='white',
                showlegend=False,
                margin=dict(l=120, r=50, t=80, b=50),
                height=300
            )

            # Melhorar aparência dos eixos
            fig_dist.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False)
            fig_dist.update_yaxes(showgrid=False)

            st.plotly_chart(fig_dist, use_container_width=True)
        # Fim do bloco if workouts
        else:
            st.info('Nenhum treino registrado na última semana.')
        
        # ============ STATUS DE TREINAMENTO ============
        st.markdown("### 📊 Status de Treinamento")
        
        tsb_value = last_metric['tsb']
        if tsb_value > 10:
            status = "✅ Recuperado"
            status_color = "#4caf50"
            description = "Você está bem descansado, ótimo para treinos intensos!"
        elif tsb_value >= -10:
            status = "⚖️ Equilibrado"
            status_color = "#ff9800"
            description = "Bom equilíbrio entre forma e fadiga, continue assim!"
        elif tsb_value >= -30:
            status = "⚠️ Fadiga"
            status_color = "#ff5722"
            description = "Você está cansado, considere reduzir volume/intensidade."
        else:
            status = "🚫 Overtraining"
            status_color = "#f44336"
            description = "CUIDADO! Você precisa descansar para evitar lesões."
        
        st.markdown(f"""
        <div style='background: {status_color}20; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};'>
            <h3 style='color: {status_color}; margin: 0;'>{status}</h3>
            <p style='color: #333; margin: 5px 0;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ ANÁLISE: ENTENDENDO SUA JORNADA ============
        st.markdown("## 📈 Análise: Entendendo Sua Jornada")
        st.markdown("*Tendências históricas e evolução do seu treinamento*")

        # Preparar dados
        dates = [m['date'] for m in metrics]
        ctl = [m['ctl'] for m in metrics]
        atl = [m['atl'] for m in metrics]
        tsb = [m['tsb'] for m in metrics]

        # Calcular deltas semanais e percentuais
        if len(metrics) >= 8:
            delta_ctl = ctl[-1] - ctl[-8]
            pct_ctl = (ctl[-1] / ctl[-8] - 1) * 100 if ctl[-8] != 0 else 0
            delta_atl = atl[-1] - atl[-8]
            pct_atl = (atl[-1] / atl[-8] - 1) * 100 if atl[-8] != 0 else 0
            delta_tsb = tsb[-1] - tsb[-8]
            pct_tsb = (tsb[-1] / tsb[-8] - 1) * 100 if tsb[-8] != 0 else 0
        else:
            delta_ctl = delta_atl = delta_tsb = pct_ctl = pct_atl = pct_tsb = 0

        # Calcular média móvel 7 dias
        if len(ctl) >= 7:
            ctl_ma = np.convolve(ctl, np.ones(7)/7, mode='valid').tolist()
            atl_ma = np.convolve(atl, np.ones(7)/7, mode='valid').tolist()
            tsb_ma = np.convolve(tsb, np.ones(7)/7, mode='valid').tolist()
            ma_dates = dates[6:]
        else:
            ctl_ma = atl_ma = tsb_ma = []
            ma_dates = []

        # Criar figura com subplots usando Plotly
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Métricas de Performance - Análise Completa', 'Mudanças na Última Semana', 'Progresso Mensal (Médias)'),
            row_heights=[0.6, 0.2, 0.2],
            vertical_spacing=0.08
        )

        # ========== SUBPLOT 1: Gráfico Principal ==========
        # Linhas principais
        fig.add_trace(
            go.Scatter(
                x=dates, y=ctl, mode='lines+markers',
                name='💪 CTL (Forma Física)',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=6, symbol='circle'),
                hovertemplate='<b>CTL</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=dates, y=atl, mode='lines+markers',
                name='😴 ATL (Fadiga)',
                line=dict(color='#d32f2f', width=3),
                marker=dict(size=6, symbol='square'),
                hovertemplate='<b>ATL</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=dates, y=tsb, mode='lines+markers',
                name='⚖️ TSB (Equilíbrio)',
                line=dict(color='#388e3c', width=3),
                marker=dict(size=6, symbol='triangle-up'),
                hovertemplate='<b>TSB</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Médias móveis
        if ctl_ma:
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=ctl_ma, mode='lines',
                    name='MA-7 CTL',
                    line=dict(color='#1976d2', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 CTL</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=atl_ma, mode='lines',
                    name='MA-7 ATL',
                    line=dict(color='#d32f2f', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 ATL</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=tsb_ma, mode='lines',
                    name='MA-7 TSB',
                    line=dict(color='#388e3c', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 TSB</b><br>Data: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Zonas preenchidas
        fig.add_trace(
            go.Scatter(
                x=dates + dates[::-1],
                y=[0]*len(dates) + [120]*len(dates),
                fill='toself',
                fillcolor='rgba(187, 222, 251, 0.2)',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ),
            row=1, col=1
        )

        # ========== SUBPLOT 2: Deltas Semanais ==========
        labels_delta = ['CTL', 'ATL', 'TSB']
        deltas = [delta_ctl, delta_atl, delta_tsb]
        colors_delta = ['#1976d2', '#d32f2f', '#388e3c']

        fig.add_trace(
            go.Bar(
                x=labels_delta,
                y=deltas,
                marker_color=colors_delta,
                text=[f'{d:+.1f}' for d in deltas],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Delta: %{y:+.1f}<extra></extra>'
            ),
            row=2, col=1
        )

        # ========== SUBPLOT 3: Progresso Mensal ==========
        months = []
        ctl_monthly = []
        atl_monthly = []
        tsb_monthly = []
        current_month = None
        month_data = {'ctl': [], 'atl': [], 'tsb': []}

        for m in metrics:
            try:
                from datetime import datetime as dt_parse
                date = dt_parse.fromisoformat(m['date'])
                month = date.strftime('%b')  # Abreviado (Jan, Fev, etc)
                if current_month != month:
                    if current_month is not None:
                        ctl_monthly.append(np.mean(month_data['ctl']))
                        atl_monthly.append(np.mean(month_data['atl']))
                        tsb_monthly.append(np.mean(month_data['tsb']))
                        months.append(current_month)
                    current_month = month
                    month_data = {'ctl': [], 'atl': [], 'tsb': []}
                month_data['ctl'].append(m['ctl'])
                month_data['atl'].append(m['atl'])
                month_data['tsb'].append(m['tsb'])
            except:
                continue

        if month_data['ctl']:
            ctl_monthly.append(np.mean(month_data['ctl']))
            atl_monthly.append(np.mean(month_data['atl']))
            tsb_monthly.append(np.mean(month_data['tsb']))
            months.append(current_month)

        if months:
            fig.add_trace(
                go.Scatter(
                    x=months, y=ctl_monthly, mode='lines+markers',
                    name='CTL Médio',
                    line=dict(color='#1976d2', width=3),
                    marker=dict(size=8, symbol='circle'),
                    hovertemplate='<b>CTL Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=months, y=atl_monthly, mode='lines+markers',
                    name='ATL Médio',
                    line=dict(color='#d32f2f', width=3),
                    marker=dict(size=8, symbol='square'),
                    hovertemplate='<b>ATL Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=months, y=tsb_monthly, mode='lines+markers',
                    name='TSB Médio',
                    line=dict(color='#388e3c', width=3),
                    marker=dict(size=8, symbol='triangle-up'),
                    hovertemplate='<b>TSB Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )

        # Configurar layout geral
        trend_ctl = "📈" if delta_ctl > 0 else "📉" if delta_ctl < 0 else "➡️"
        trend_atl = "📈" if delta_atl > 0 else "📉" if delta_atl < 0 else "➡️"
        trend_tsb = "📈" if delta_tsb > 0 else "📉" if delta_tsb < 0 else "➡️"

        fig.update_layout(
            height=800,
            title={
                'text': f'Análise Completa das Métricas de Performance<br><span style="font-size:14px;color:#6c757d;">Tendência Semanal: CTL {trend_ctl} {delta_ctl:+.1f} ({pct_ctl:+.1f}%) | ATL {trend_atl} {delta_atl:+.1f} ({pct_atl:+.1f}%) | TSB {trend_tsb} {delta_tsb:+.1f} ({pct_tsb:+.1f}%)</span>',
                'y': 0.98,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16, 'color': '#212529'}
            },
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.1,
                xanchor='center',
                x=0.5,
                font={'size': 11}
            )
        )

        # Configurar eixos
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_yaxes(title_text='Pontuação', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_yaxes(title_text='Delta Semanal', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)
        fig.update_xaxes(title_text='Mês', showgrid=False, row=3, col=1)
        fig.update_yaxes(title_text='Pontuação', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=3, col=1)

        # Adicionar linha zero no subplot 2
        fig.add_hline(y=0, line_width=1, line_color='black', row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)
        
        # ============ REFERÊNCIAS PARA IRONMAN ============
        with st.expander("🎯 Referências para Amador Bem Treinado - Meio Ironman"):
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.markdown("""
                **8 semanas antes da prova:**
                - Forma Física (CTL): ~50
                - Fadiga (ATL): ~25
                - Equilíbrio (TSB): ~25
                
                **2 semanas antes da prova:**
                - Forma Física (CTL): ~80
                - Fadiga (ATL): ~40
                - Equilíbrio (TSB): ~40
                """)
            with col_ref2:
                st.markdown("""
                **Semana da prova:**
                - Forma Física (CTL): ~90
                - Fadiga (ATL): ~45
                - Equilíbrio (TSB): ~45
                
                **Valores atuais:**
                - CTL: {:.1f}
                - ATL: {:.1f}
                - TSB: {:.1f}
                """.format(ctl[-1], atl[-1], tsb[-1]))
        
        # ============ APRENDIZADO: ENTENDA MELHOR ============
        st.markdown("## 📚 Aprendizado: Entenda Melhor")
        st.markdown("*Informações educacionais e referências para otimizar seu treinamento*")
        
        # ============ EXPLICAÇÃO DAS MÉTRICAS ============
        with st.expander("📚 O que significa cada métrica?"):
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.markdown("""
                **💪 CTL (Forma Física Crônica)**
                - Representa sua forma física geral, construída ao longo de ~6 semanas
                - Valores mais altos = você está mais preparado para provas longas
                - Para amador bem treinado em Ironman: ideal 50-90
                
                **😴 ATL (Fadiga Aguda)**
                - Mostra a fadiga recente (últimos 7 dias)
                - Valores altos = você precisa de descanso
                - Idealmente ATL < CTL para evitar overtraining
                """)
            
            with col_exp2:
                st.markdown("""
                **⚖️ TSB (Equilíbrio de Treino)**
                - Diferença entre CTL e ATL: TSB = CTL - ATL
                - Positivo = recuperação (bom para treinar duro)
                - Negativo = fadiga (precisa descansar)
                - É como um "saldo" de energia
                """)
        
        # ============ REFERÊNCIAS PARA IRONMAN ============
        with st.expander("🎯 Referências para Amador Bem Treinado - Meio Ironman"):
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.markdown("""
                **8 semanas antes da prova:**
                - Forma Física (CTL): ~50
                - Fadiga (ATL): ~25
                - Equilíbrio (TSB): ~25
                
                **2 semanas antes da prova:**
                - Forma Física (CTL): ~80
                - Fadiga (ATL): ~40
                - Equilíbrio (TSB): ~40
                """)
            with col_ref2:
                st.markdown("""
                **Semana da prova:**
                - Forma Física (CTL): ~90
                - Fadiga (ATL): ~45
                - Equilíbrio (TSB): ~45
                
                **Valores atuais:**
                - CTL: {:.1f}
                - ATL: {:.1f}
                - TSB: {:.1f}
                """.format(ctl[-1], atl[-1], tsb[-1]))
        
        
        # ============ TABELA DE ATIVIDADES RECENTES ============
        st.markdown("### 📋 Últimas Métricas Diárias")
        
        workouts = load_workouts()
        if workouts:
            config_for_tss = load_config()

            def _modality_tss(category: str, tss_data: dict) -> float:
                if category == 'running':
                    return float(tss_data.get('rtss', 0) or 0) or float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0)
                if category == 'swimming':
                    return float(tss_data.get('stss', 0) or 0) or float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0)
                if category == 'cycling':
                    return float(tss_data.get('tss', 0) or 0)
                return float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0) or 0.0

            # Pegar últimas 7 atividades
            def get_activity_datetime(w):
                # Usa startTimeLocal, depois startTimeGMT, depois startTimeInSeconds
                from datetime import datetime as dt
                if w.get('startTimeLocal'):
                    try:
                        return dt.strptime(w['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass
                if w.get('startTimeGMT'):
                    try:
                        return dt.strptime(w['startTimeGMT'], '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass
                if w.get('startTimeInSeconds'):
                    return dt.fromtimestamp(w['startTimeInSeconds'])
                return dt(1970,1,1)

            recent_workouts = sorted(workouts, key=get_activity_datetime, reverse=True)[:7]

            workout_df = []
            for w in recent_workouts:
                try:
                    activity_name = w.get('activityName', 'Atividade Desconhecida')
                    distance = w.get('distance', 0)
                    duration_mins = w.get('duration', 0) // 60

                    type_key = (w.get('activityType') or {}).get('typeKey', '')
                    category = _activity_category(w)
                    tss_calc = compute_tss_variants(w, config_for_tss)
                    tss_value = _modality_tss(category, tss_calc)

                    modality_label = {
                        'cycling': 'Bike',
                        'running': 'Corrida',
                        'swimming': 'Natação',
                        'strength': 'Força',
                        'other': 'Outros'
                    }.get(category, 'Outros')

                    # Formatar distância
                    if distance >= 1000:
                        distance_str = f"{distance/1000:.2f} km"
                    else:
                        distance_str = f"{distance:.0f} m"

                    # Data preferencial: startTimeLocal, depois startTimeGMT, depois startTimeInSeconds
                    from datetime import datetime as dt
                    if w.get('startTimeLocal'):
                        activity_date = dt.strptime(w['startTimeLocal'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    elif w.get('startTimeGMT'):
                        activity_date = dt.strptime(w['startTimeGMT'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    elif w.get('startTimeInSeconds'):
                        activity_date = dt.fromtimestamp(w['startTimeInSeconds']).strftime('%d/%m/%Y')
                    else:
                        activity_date = ''

                    workout_df.append({
                        '📅 Data': activity_date,
                        '🏃 Atividade': activity_name[:25],
                        '🏷️ Modalidade': modality_label,
                        '📏 Distância': distance_str,
                        '⏱️ Duração': f"{duration_mins} min",
                        '🎯 TSS': f"{tss_value:.1f}"
                    })
                except Exception:
                    continue

            if workout_df:
                st.dataframe(workout_df, use_container_width=True, hide_index=True)
        
        # ============ TABELA COM ÚLTIMAS MÉTRICAS ============
        st.markdown("### 📊 Histórico de Métricas (Últimos 7 dias)")
        
        display_metrics = metrics[-7:] if len(metrics) >= 7 else metrics
        display_df = []
        for m in reversed(display_metrics):
            display_df.append({
                '📅 Data': m['date'],
                '💪 Fitness (CTL)': f"{m['ctl']:.1f}",
                '😴 Fadiga (ATL)': f"{m['atl']:.1f}",
                '⚖️ Equilíbrio (TSB)': f"{m['tsb']:.1f}",
                '🎯 Carga Diária': f"{m['daily_load']:.1f}"
            })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ============ MODALIDADES: SEU DESEMPENHO DETALHADO ============
        st.markdown("## 🏊 Modalidades: Seu Desempenho Detalhado")
        st.markdown("*Análise específica por esporte ao longo de 42 dias*")
        
        # ============ PROGRESSO POR MODALIDADE ============
        st.markdown("---")
        st.header("📊 Progresso por Modalidade")

    workouts = load_workouts()
    if workouts:
        # Calcular progresso por modalidade e semana
        modality_progress = calculate_modality_progress(workouts)

        # Criar abas para cada modalidade
        tab1, tab2, tab3, tab4 = st.tabs(["🚴 Ciclismo", "🏃 Corrida", "🏊 Natação", "💪 Musculação"])

        with tab1:
            display_modality_progress(modality_progress, 'cycling', "🚴 Ciclismo")

        with tab2:
            display_modality_progress(modality_progress, 'running', "🏃 Corrida")

        with tab3:
            display_modality_progress(modality_progress, 'swimming', "🏊 Natação")

        with tab4:
            display_modality_progress(modality_progress, 'strength', "💪 Musculação")
    else:
        st.info("🔄 Sincronize seus dados do Garmin Connect para ver o progresso por modalidade.")

# PAGE 2: CALENDÁRIO
elif page == "📅 Calendário":
    st.title("📅 Calendário de Treinos")

    # Usar dados processados em cache
    workouts = get_processed_workouts()
    config = load_config_cached()

    # Função helper para formatar duração em hh:mm:ss (usando utils)
    def format_duration_local(seconds):
        return format_duration(seconds)

    if not workouts:
        st.warning("⚠️ Nenhum treino disponível. Vá para 'Atualizar Dados' para sincronizar.")
    else:
        # Controles de navegação do mês
        col1, col2, col3 = st.columns([1, 3, 1])

        # Inicializar mês/ano no session_state
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = datetime.now().month
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = datetime.now().year

        with col1:
            if st.button("◀ Mês Anterior", use_container_width=True):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                else:
                    st.session_state.cal_month -= 1

        with col2:
            month_name = calendar.month_name[st.session_state.cal_month]
            st.markdown(f"<h2 style='text-align:center;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;letter-spacing:1px;'>{month_name} {st.session_state.cal_year}</h2>", unsafe_allow_html=True)

        with col3:
            if st.button("Próximo Mês ▶", use_container_width=True):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                else:
                    st.session_state.cal_month += 1

        st.divider()

        # Preparar dados do calendário
        cal = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)

        # Cores por modalidade
        colors = {
            'running': '#10b981',
            'cycling': '#3b82f6',
            'swimming': '#06b6d4',
            'strength': '#f59e0b',
            'other': '#6b7280'
        }

        icons = {
            'running': '🏃',
            'cycling': '🚴',
            'swimming': '🏊',
            'strength': '💪',
            'other': '📊'
        }

        # Filtrar workouts do mês atual (processamento otimizado)
        current_month_workouts = []
        workouts_by_date = {}

        for workout in workouts:
            start_time = workout.get('start_time', '')
            if start_time:
                try:
                    if 'T' in start_time:
                        date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                    else:
                        date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()

                    if date_obj.month == st.session_state.cal_month and date_obj.year == st.session_state.cal_year:
                        date_key = date_obj.day
                        if date_key not in workouts_by_date:
                            workouts_by_date[date_key] = []
                        workouts_by_date[date_key].append(workout)
                        current_month_workouts.append(workout)
                except:
                    continue
        
        # Se não há workouts no mês atual, tentar encontrar um mês com dados
        if not current_month_workouts:
            st.info("📅 Nenhum treino encontrado neste mês. Procurando dados em outros meses...")
            
            # Encontrar o mês com mais workouts
            month_stats = {}
            for workout in workouts:
                start_time = workout.get('start_time', '')
                if start_time:
                    try:
                        if 'T' in start_time:
                            date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                        else:
                            date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()
                        
                        key = (date_obj.year, date_obj.month)
                        if key not in month_stats:
                            month_stats[key] = 0
                        month_stats[key] += 1
                    except:
                        continue
            
            if month_stats:
                # Encontrar o mês com mais dados
                best_month = max(month_stats.items(), key=lambda x: x[1])
                st.session_state.cal_year, st.session_state.cal_month = best_month[0]
                st.success(f"📊 Mostrando dados de {calendar.month_name[st.session_state.cal_month]} {st.session_state.cal_year} ({best_month[1]} treinos)")
                
                # Refazer a filtragem com o novo mês
                current_month_workouts = []
                workouts_by_date = {}
                for workout in workouts:
                    start_time = workout.get('start_time', '')
                    if start_time:
                        try:
                            if 'T' in start_time:
                                date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                            else:
                                date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()
                            
                            if date_obj.month == st.session_state.cal_month and date_obj.year == st.session_state.cal_year:
                                date_key = date_obj.day
                                if date_key not in workouts_by_date:
                                    workouts_by_date[date_key] = []
                                workouts_by_date[date_key].append(workout)
                                current_month_workouts.append(workout)
                        except:
                            continue

        # Calcular resumo do mês (otimizado - usar dados já processados)
        total_workouts = len(current_month_workouts)
        total_tss = sum(act['tss'] for act in current_month_workouts)
        total_distance = sum(act['distance'] for act in current_month_workouts) / 1000
        total_duration_sec = sum(act['duration'] for act in current_month_workouts)
        
        # Contar por modalidade (otimizado)
        monthly_by_category = {}
        for act in current_month_workouts:
            cat = act['category']
            if cat not in monthly_by_category:
                monthly_by_category[cat] = {'count': 0, 'distance': 0, 'duration': 0}
            monthly_by_category[cat]['count'] += 1
            monthly_by_category[cat]['distance'] += act['distance'] / 1000
            monthly_by_category[cat]['duration'] += act['duration']
        
        # Exibir resumo do mês no topo
        st.markdown("### 📊 Resumo do Mês")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏋️ Treinos", f"{total_workouts}")
        col2.metric("📊 TSS Total", f"{total_tss:.0f}")
        col3.metric("📏 Distância", f"{total_distance:.1f} km")
        col4.metric("⏱️ Tempo", format_duration_local(total_duration_sec))
        
        st.divider()
        
        # Renderizar calendário
        st.markdown("""
        <style>
        /* Estilo dos cabeçalhos dos dias */
        .cal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px;
            text-align: center;
            font-weight: 700;
            border-radius: 6px;
            margin-bottom: 2px;
            font-size: 0.75rem;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Container de cada dia */
        .cal-day-container {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 4px;
            min-height: 80px;
            margin-bottom: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .cal-day-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #c7d2fe;
        }
        
        /* Dias vazios */
        .cal-day-empty {
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            border: 1px dashed #d1d5db;
            border-radius: 6px;
            min-height: 80px;
            margin-bottom: 2px;
        }
        
        /* Número do dia */
        .cal-day-num {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            font-weight: 700;
            font-size: 0.95rem;
            color: #1e40af;
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-block;
            margin-bottom: 4px;
            float: right;
            box-shadow: 0 1px 2px rgba(30, 64, 175, 0.1);
        }
        
        /* Cabeçalho do dia */
        .cal-day-header {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            color: #1e40af;
            font-weight: 700;
            font-size: 0.85rem;
            padding: 3px 6px;
            border-radius: 4px;
            margin-bottom: 3px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(59, 130, 246, 0.1);
        }
        
        /* Card de resumo semanal */
        .cal-week-summary {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #60a5fa;
            border-radius: 6px;
            padding: 5px;
            font-size: 0.6rem;
            min-height: 80px;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.15);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        .cal-week-summary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(59, 130, 246, 0.25);
        }
        
        /* Responsividade para mobile */
        @media (max-width: 768px) {
            .cal-header {
                font-size: 0.65rem;
                padding: 4px 1px;
                border-radius: 4px;
            }
            .cal-day-container {
                min-height: 70px;
                padding: 3px;
                border-radius: 4px;
            }
            .cal-day-empty {
                min-height: 70px;
            }
            .cal-day-num {
                font-size: 0.75rem;
                padding: 2px 5px;
            }
            .cal-day-header {
                font-size: 0.7rem;
                padding: 2px 5px;
                margin-bottom: 2px;
            }
            .cal-week-summary {
                min-height: 70px;
                font-size: 0.55rem;
                padding: 4px;
            }
        }
        
        /* Responsividade para telas muito pequenas */
        @media (max-width: 480px) {
            .cal-header {
                font-size: 0.6rem;
                padding: 3px 1px;
            }
            .cal-day-container {
                min-height: 65px;
                padding: 3px;
            }
            .cal-day-empty {
                min-height: 65px;
            }
            .cal-day-num {
                font-size: 0.7rem;
                padding: 1px 4px;
            }
            .cal-day-header {
                font-size: 0.65rem;
                padding: 2px 4px;
                margin-bottom: 2px;
            }
            .cal-week-summary {
                min-height: 65px;
                font-size: 0.5rem;
                padding: 3px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Cabeçalho dos dias da semana + resumo
        weekdays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom', 'Resumo']
        cols = st.columns(8)
        for i, day in enumerate(weekdays):
            with cols[i]:
                st.markdown(f"<div class='cal-header'>{day}</div>", unsafe_allow_html=True)
        
        # Renderizar semanas
        for week_idx, week in enumerate(cal):
            cols = st.columns(8)
            
            # Calcular resumo semanal (otimizado)
            week_workouts = []
            for day in week:
                if day != 0 and day in workouts_by_date:
                    week_workouts.extend(workouts_by_date[day])

            # Usar dados já calculados para resumo semanal
            week_tss = sum(act['tss'] for act in week_workouts)
            week_distance = sum(act['distance'] for act in week_workouts) / 1000
            week_duration_sec = sum(act['duration'] for act in week_workouts)

            # Agrupar por categoria (otimizado)
            week_by_cat = {}
            for act in week_workouts:
                cat = act['category']
                if cat not in week_by_cat:
                    week_by_cat[cat] = {'count': 0, 'duration': 0, 'distance': 0}
                week_by_cat[cat]['count'] += 1
                week_by_cat[cat]['duration'] += act['duration']
                week_by_cat[cat]['distance'] += act['distance'] / 1000
            
            # Renderizar dias
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown("<div class='cal-day-empty'></div>", unsafe_allow_html=True)
                    else:
                        day_workouts = workouts_by_date.get(day, [])

                        # Usar função otimizada para gerar HTML
                        activities_html = generate_activity_html(day_workouts, colors, icons)

                        day_html = f"<div class='cal-day-container'><div class='cal-day-header'>{day}</div>{activities_html}</div>"
                        st.markdown(day_html, unsafe_allow_html=True)
            
            # Resumo semanal na última coluna
            with cols[7]:
                summary_html = "<div class='cal-week-summary' style='text-align:center;'>"
                summary_html += f"<div style='font-weight:800;color:#1e40af;background:white;padding:2px;border-radius:3px;font-size:0.68rem;margin-bottom:1px;box-shadow:0 1px 2px rgba(30,64,175,0.1);'>S{week_idx+1}</div>"
                summary_html += f"<div style='color:#1f2937;font-size:0.62rem;font-weight:600;margin-bottom:1px;'><span style='background:#dbeafe;padding:1px 4px;border-radius:3px;'>{len(week_workouts)} tr</span> • <span style='background:#fef3c7;padding:1px 4px;border-radius:3px;'>TSS {week_tss:.0f}</span></div>"
                summary_html += f"<div style='color:#6b7280;font-size:0.57rem;font-weight:500;'>{week_distance:.1f}km • {format_duration_local(week_duration_sec)}</div>"
                
                if week_by_cat:
                    summary_html += "<div style='padding-top:3px;border-top:1px solid #bfdbfe;text-align:left;margin-top:auto;'>"
                    for cat, data in week_by_cat.items():
                        icon = icons.get(cat, '📊')
                        count = data['count']
                        duration_sec = data['duration']
                        distance_km = data['distance']
                        summary_html += f"<div style='color:#374151;font-size:0.57rem;margin-bottom:1px;display:flex;justify-content:space-between;align-items:center;font-weight:500;'><span style='font-weight:700;'>{icon} {count}</span><span style='color:#6b7280;'>{format_duration_local(duration_sec)}</span><span style='color:#6b7280;'>{distance_km:.1f}km</span></div>"
                    summary_html += "</div>"
                
                summary_html += "</div>"
                st.markdown(summary_html, unsafe_allow_html=True)
            
            # Divisor discreto entre semanas (exceto após a última)
            if week_idx < len(cal) - 1:
                st.markdown("<div style='border-top:1px solid #e5e7eb;margin:3px 0;'></div>", unsafe_allow_html=True)

# PAGE 3: METAS
elif page == "🎯 Metas":
    st.title("🎯 Configuração de Metas")

    st.markdown("""
    Defina suas metas de treinamento semanal, mensal e de performance.

    **💡 Dicas:**
    - **Metas realistas:** Comece com objetivos alcançáveis e aumente gradualmente
    - **Equilíbrio:** Mantenha ATL abaixo de 80 para evitar overtraining
    - **Progressão:** Acompanhe seu progresso e ajuste conforme necessário
    """)

    config = load_config()

    # Metas semanais
    st.subheader("📅 Metas Semanais")
    col1, col2 = st.columns(2)
    with col1:
        weekly_distance_goal = st.number_input(
            "Distância (km)",
            min_value=0.0,
            max_value=500.0,
            value=float(config.get('weekly_distance_goal', 50.0)),
            step=5.0,
            help="Distância total semanal em quilômetros"
        )
        weekly_tss_goal = st.number_input(
            "TSS Total",
            min_value=0,
            max_value=2000,
            value=int(config.get('weekly_tss_goal', 300)),
            help="Training Stress Score semanal total"
        )
    with col2:
        weekly_hours_goal = st.number_input(
            "Horas de Treino",
            min_value=0.0,
            max_value=50.0,
            value=float(config.get('weekly_hours_goal', 7.0)),
            step=0.5,
            help="Tempo total de treinamento semanal em horas"
        )
        weekly_activities_goal = st.number_input(
            "Número de Atividades",
            min_value=0,
            max_value=20,
            value=int(config.get('weekly_activities_goal', 5)),
            help="Número de sessões de treino por semana"
        )

    # Metas mensais
    st.subheader("📊 Metas Mensais")
    col1, col2 = st.columns(2)
    with col1:
        monthly_distance_goal = st.number_input(
            "Distância (km)",
            min_value=0.0,
            max_value=2000.0,
            value=float(config.get('monthly_distance_goal', 200.0)),
            step=10.0,
            help="Distância total mensal em quilômetros"
        )
        monthly_tss_goal = st.number_input(
            "TSS Total",
            min_value=0,
            max_value=8000,
            value=int(config.get('monthly_tss_goal', 1200)),
            help="Training Stress Score mensal total"
        )
    with col2:
        monthly_hours_goal = st.number_input(
            "Horas de Treino",
            min_value=0.0,
            max_value=200.0,
            value=float(config.get('monthly_hours_goal', 30.0)),
            step=1.0,
            help="Tempo total de treinamento mensal em horas"
        )
        monthly_activities_goal = st.number_input(
            "Número de Atividades",
            min_value=0,
            max_value=100,
            value=int(config.get('monthly_activities_goal', 20)),
            help="Número de sessões de treino por mês"
        )

    # Metas de performance
    st.subheader("🏆 Metas de Performance")
    col1, col2 = st.columns(2)
    with col1:
        target_ctl = st.number_input(
            "CTL Alvo (Forma Física)",
            min_value=0,
            max_value=150,
            value=int(config.get('target_ctl', 50)),
            help="Nível de forma física desejado (Chronic Training Load)"
        )
    with col2:
        target_atl_max = st.number_input(
            "ATL Máximo Permitido",
            min_value=0,
            max_value=200,
            value=int(config.get('target_atl_max', 80)),
            help="Limite máximo de fadiga aguda para evitar overtraining"
        )

    # Botão para salvar metas
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Salvar Metas", use_container_width=True):
            # Carregar config atual
            current_config = load_config()

            # Atualizar apenas as metas
            updated_config = current_config.copy()
            updated_config.update({
                # Metas semanais
                'weekly_distance_goal': weekly_distance_goal,
                'weekly_tss_goal': weekly_tss_goal,
                'weekly_hours_goal': weekly_hours_goal,
                'weekly_activities_goal': weekly_activities_goal,
                # Metas mensais
                'monthly_distance_goal': monthly_distance_goal,
                'monthly_tss_goal': monthly_tss_goal,
                'monthly_hours_goal': monthly_hours_goal,
                'monthly_activities_goal': monthly_activities_goal,
                # Metas de performance
                'target_ctl': target_ctl,
                'target_atl_max': target_atl_max
            })

            save_config(updated_config)
            st.success("✅ Metas salvas com sucesso!")
            st.balloons()

    # Mostrar progresso atual
    st.markdown("---")
    st.subheader("📈 Progresso Atual")

    workouts = load_workouts()
    if workouts:
        goals_progress = calculate_goals_progress(workouts, config)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Semanal**")
            weekly_distance = goals_progress['weekly']['distance']
            weekly_distance_goal_val = config.get('weekly_distance_goal', 50.0)
            distance_pct = min(100, (weekly_distance / weekly_distance_goal_val * 100) if weekly_distance_goal_val > 0 else 0)

            st.metric(
                "🏃 Distância",
                f"{weekly_distance:.1f}km / {weekly_distance_goal_val:.0f}km",
                f"{distance_pct:.1f}%"
            )

            weekly_tss = goals_progress['weekly']['tss']
            weekly_tss_goal_val = config.get('weekly_tss_goal', 300)
            tss_pct = min(100, (weekly_tss / weekly_tss_goal_val * 100) if weekly_tss_goal_val > 0 else 0)

            st.metric(
                "🎯 TSS",
                f"{weekly_tss:.0f} / {weekly_tss_goal_val:.0f}",
                f"{tss_pct:.1f}%"
            )

        with col2:
            st.markdown("**Mensal**")
            monthly_distance = goals_progress['monthly']['distance']
            monthly_distance_goal_val = config.get('monthly_distance_goal', 200.0)
            monthly_distance_pct = min(100, (monthly_distance / monthly_distance_goal_val * 100) if monthly_distance_goal_val > 0 else 0)

            st.metric(
                "🏃 Distância",
                f"{monthly_distance:.1f}km / {monthly_distance_goal_val:.0f}km",
                f"{monthly_distance_pct:.1f}%"
            )

            monthly_tss = goals_progress['monthly']['tss']
            monthly_tss_goal_val = config.get('monthly_tss_goal', 1200)
            monthly_tss_pct = min(100, (monthly_tss / monthly_tss_goal_val * 100) if monthly_tss_goal_val > 0 else 0)

            st.metric(
                "🎯 TSS",
                f"{monthly_tss:.0f} / {monthly_tss_goal_val:.0f}",
                f"{monthly_tss_pct:.1f}%"
            )
    else:
        st.info("🔄 Sincronize seus dados do Garmin Connect para ver o progresso atual.")

# PAGE 3: CONFIGURAÇÃO
elif page == "⚙️ Configuração":
    st.title("⚙️ Configuração")
    
    st.markdown("""
    Configure suas credenciais do Garmin Connect e parâmetros de fitness.
    
    **⚠️ Segurança:** Suas credenciais são armazenadas **apenas no seu dispositivo** e 
    nunca são enviadas para servidores. Você pode deletá-las a qualquer momento.
    """)
    
    # Seção de Credenciais
    st.subheader("🔐 Credenciais Garmin Connect")
    st.info("Seus dados de login são armazenados de forma segura apenas neste dispositivo.")
    
    creds = load_credentials()
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input(
            "Email Garmin Connect",
            value=creds.get('email', ''),
            key='email_input'
        )
    with col2:
        password = st.text_input(
            "Senha Garmin Connect",
            value=creds.get('password', ''),
            type="password"
        )

    st.markdown("""
    ### 🏋️ Parâmetros de Fitness
    
    **💡 Sobre o hrTSS:** O cálculo do hrTSS usa o LTHR (Limiar de Frequência Cardíaca) como referência, 
    seguindo a fórmula do TrainingPeaks. Configure corretamente seu LTHR para obter valores precisos.
    """)
    
    config = load_config()
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "Idade",
            min_value=15,
            max_value=100,
            value=config.get('age', 29)
        )
        ftp = st.number_input(
            "FTP (Functional Threshold Power) - Watts",
            min_value=50,
            max_value=500,
            value=config.get('ftp', 250),
            step=5
        )
        hr_rest = st.number_input(
            "Frequência Cardíaca em Repouso (bpm)",
            min_value=40,
            max_value=100,
            value=config.get('hr_rest', 50)
        )
        hr_threshold = st.number_input(
            "LTHR - Frequência Cardíaca de Limiar (bpm)",
            min_value=100,
            max_value=200,
            value=config.get('hr_threshold', 162),
            help="Usado para calcular hrTSS (TrainingPeaks)"
        )
    
    with col2:
        hr_max = st.number_input(
            "Frequência Cardíaca Máxima (bpm)",
            min_value=150,
            max_value=220,
            value=config.get('hr_max', 191)
        )
        pace_threshold = st.text_input(
            "Limiar de Pace - Corrida (mm:ss)",
            value=config.get('pace_threshold', '4:22')
        )
        swim_pace_threshold = st.text_input(
            "Limiar de Pace - Natação (mm:ss)",
            value=config.get('swim_pace_threshold', '2:01')
        )
    
    # Botão para salvar
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Configurações", use_container_width=True):
            # Salvar credenciais
            save_credentials(email, password)
            
            # Salvar config
            new_config = {
                'age': age,
                'ftp': ftp,
                'hr_rest': hr_rest,
                'hr_max': hr_max,
                'hr_threshold': hr_threshold,
                'pace_threshold': pace_threshold,
                'swim_pace_threshold': swim_pace_threshold
            }
            save_config(new_config)
            
            st.success("✅ Configurações salvas com sucesso!")
    
    with col2:
        if st.button("🗑️ Deletar Credenciais", use_container_width=True):
            if CREDENTIALS_FILE.exists():
                os.remove(CREDENTIALS_FILE)
            st.success("✅ Credenciais deletadas com sucesso!")
            st.rerun()
    

    with col3:
        if st.button("📂 Ver Local de Armazenamento", use_container_width=True):
            st.info(f"Arquivos armazenados em:\n`{LOCAL_STORAGE_DIR}`")

    # Botão de reiniciar dados do dashboard
    st.markdown("---")
    st.subheader("Reiniciar Dados do Dashboard")
    st.caption("Apaga todos os dados locais de métricas e treinos. Não afeta configurações.")
    if st.button('🧹 Reiniciar Dados do Dashboard', key='reset_config', use_container_width=True):
        def reset_dashboard_data():
            for f in [METRICS_FILE, WORKOUTS_FILE]:
                try:
                    if f.exists():
                        f.unlink()
                except Exception as e:
                    st.warning(f"Erro ao apagar {f}: {e}")
        reset_dashboard_data()
        st.success('Dados reiniciados! Recarregue a página.')


    # ============ BLOCO DE ATUALIZAÇÃO DE DADOS INCORPORADO ============
    st.markdown("---")
    st.header("🔄 Atualizar Dados do Garmin Connect")
    st.markdown("""
    Clique no botão abaixo para sincronizar seus dados com Garmin Connect.
    Este processo busca todas as atividades dos últimos 42 dias e recalcula 
    as métricas de fitness (CTL, ATL, TSB).
    """)
    creds = load_credentials()
    if not creds.get('email') or not creds.get('password'):
        st.warning("⚠️ Credenciais não configuradas. Preencha acima para adicionar suas credenciais do Garmin Connect.")
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Atualizar Dados Agora", use_container_width=True):
                with st.spinner("Sincronizando com Garmin Connect..."):
                    config = load_config()
                    success, message = fetch_garmin_data(
                        creds['email'],
                        creds['password'],
                        config
                    )
                    if success:
                        st.success(message)
                        st.session_state.update_status = ("success", message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                        st.session_state.update_status = ("error", message)
        with col2:
            workouts = load_workouts()
            if workouts:
                st.info(f"📊 Dados disponíveis:\n- **{len(workouts)}** atividades carregadas\n- Última atualização: Verifique a página Dashboard")
            else:
                st.info("📊 Nenhum dado carregado ainda.")
        if st.session_state.update_status:
            status_type, message = st.session_state.update_status
            if status_type == "success":
                st.success(message)
            else:
                st.error(message)
    st.subheader("📖 Instruções")
    st.markdown("""
    1. **Configure suas credenciais** acima
    2. **Clique em "Atualizar Dados Agora"** para sincronizar
    3. **Visualize os resultados** na página Dashboard
    
    A aplicação buscará todas as atividades dos últimos 42 dias e calculará:
    - **CTL (Forma Física)**: Carga de treino crônica (média de 42 dias)
    - **ATL (Fadiga)**: Carga de treino aguda (média de 7 dias)
    - **TSB (Equilíbrio)**: Diferença entre forma e fadiga (CTL - ATL)
    """)
