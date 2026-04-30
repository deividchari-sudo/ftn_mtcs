"""
Módulo de cálculos de fitness metrics.

Implementação das métricas conforme documentação oficial do TrainingPeaks:
- https://help.trainingpeaks.com/hc/en-us/articles/204071944-Training-Stress-Scores-TSS-Explained
- https://www.trainingpeaks.com/learn/articles/estimating-training-stress-score-tss/
- https://help.trainingpeaks.com/hc/en-us/articles/204072154-Advanced-Analysis-Metrics
- https://www.procyclingcoaching.com/post/core-trainingpeaks-metrics-fitness-form-fatigue

Fórmulas principais:
- TSS = (sec × NP × IF) / (FTP × 3600) × 100 = IF² × duration_hours × 100
- rTSS = (sec × NGP × IF) / (Threshold_Pace × 3600) × 100
- sTSS = (duration_sec × (pace/threshold)²) / 3600 × 100
- hrTSS = baseado em tempo em zonas de FC relativas ao LTHR
- tTSS = TRIMP adaptado (quando só temos avgHR e duration)
- CTL = exponential moving average de 42 dias do TSS diário
- ATL = exponential moving average de 7 dias do TSS diário  
- TSB = CTL - ATL
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any


# =============================================================================
# CONSTANTES
# =============================================================================

# Constantes de tempo para médias móveis exponenciais (EMA)
CTL_TIME_CONSTANT = 42  # dias para Chronic Training Load (Fitness)
ATL_TIME_CONSTANT = 7   # dias para Acute Training Load (Fatigue)

# Constantes de gênero para cálculo TRIMP (Banister)
TRIMP_GENDER_MALE = {'k': 1.92, 'factor': 0.64}
TRIMP_GENDER_FEMALE = {'k': 1.67, 'factor': 0.86}

# Multiplicadores de intensidade por zona de FC (TrainingPeaks hrTSS estimation)
# Baseado em: https://www.trainingpeaks.com/learn/articles/estimating-training-stress-score-tss/
HR_ZONE_TSS_PER_HOUR = {
    1: 55,   # Zone 1 (Recovery): ~55 TSS/hour
    2: 75,   # Zone 2 (Endurance): ~75 TSS/hour  
    3: 90,   # Zone 3 (Tempo): ~90 TSS/hour
    4: 100,  # Zone 4 (Threshold): 100 TSS/hour (by definition)
    5: 120,  # Zone 5 (VO2Max): ~120 TSS/hour
    6: 140,  # Zone 6 (Anaerobic): ~140 TSS/hour
}


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def _activity_category(activity: dict) -> str:
    """
    Categoriza atividade baseada no tipo.
    
    Args:
        activity: Dicionário com dados da atividade
    
    Returns:
        str: Categoria ('cycling', 'running', 'swimming', 'strength', 'other')
    """
    activity_type = activity.get('activityType', {})
    if isinstance(activity_type, dict):
        type_key = activity_type.get('typeKey', '').lower()
    else:
        type_key = str(activity_type).lower()

    # Ciclismo
    cycling_types = {
        'cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling', 
        'gravel_cycling', 'virtual_cycling', 'virtual_ride', 'indoor_biking', 
        'bike', 'biking', 'e_bike_ride', 'e_mountain_bike_ride',
        'commute_cycling', 'touring_cycling', 'recumbent_cycling', 'cyclocross', 
        'road_biking', 'gravel_biking', 'tandem_cycling', 'bmx', 'fat_bike', 
        'track_cycling', 'spin_bike'
    }
    
    # Corrida
    running_types = {
        'running', 'treadmill_running', 'track_running', 'trail_running', 
        'indoor_running', 'virtual_running'
    }
    
    # Natação
    swimming_types = {
        'swimming', 'pool_swimming', 'open_water_swimming', 
        'indoor_swimming', 'lap_swimming'
    }
    
    # Força/HIIT
    strength_types = {
        'strength_training', 'weight_training', 'functional_strength_training', 
        'gym_strength_training', 'crossfit', 'hiit'
    }

    if type_key in cycling_types:
        return 'cycling'
    if type_key in running_types:
        return 'running'
    if type_key in swimming_types:
        return 'swimming'
    if type_key in strength_types:
        return 'strength'
    return 'other'


def _parse_mmss_to_seconds(value: str, default_seconds: int = 300) -> int:
    """
    Converte string mm:ss para segundos totais.
    
    Args:
        value: String no formato "mm:ss" (ex: "5:00" para 5 minutos)
        default_seconds: Valor padrão caso a conversão falhe
    
    Returns:
        int: Total de segundos
    
    Examples:
        >>> _parse_mmss_to_seconds("5:00")
        300
        >>> _parse_mmss_to_seconds("4:30")
        270
    """
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
    except (ValueError, TypeError):
        return default_seconds


def _get_hr_zone(hr: float, lthr: float) -> int:
    """
    Determina a zona de frequência cardíaca baseada no LTHR.
    
    Zonas baseadas em % do LTHR (TrainingPeaks standard):
    - Zone 1: < 81% LTHR (Recovery)
    - Zone 2: 81-89% LTHR (Endurance)
    - Zone 3: 90-93% LTHR (Tempo)
    - Zone 4: 94-99% LTHR (Threshold)
    - Zone 5a: 100-102% LTHR (VO2Max)
    - Zone 5b: 103-106% LTHR (VO2Max high)
    - Zone 6: > 106% LTHR (Anaerobic)
    
    Args:
        hr: Frequência cardíaca atual
        lthr: Frequência cardíaca no limiar (Lactate Threshold HR)
    
    Returns:
        int: Zona de FC (1-6)
    """
    if lthr <= 0:
        return 1
    
    pct = (hr / lthr) * 100
    
    if pct < 81:
        return 1
    elif pct < 90:
        return 2
    elif pct < 94:
        return 3
    elif pct < 100:
        return 4
    elif pct < 106:
        return 5
    else:
        return 6


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Converte valor para float de forma segura."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def _get_avg_hr(activity: dict) -> float:
    """Extrai HR médio de uma atividade."""
    hr_fields = ['averageHR', 'avgHR', 'avgHr', 'averageHeartRate', 'avgHeartRate']
    for field in hr_fields:
        val = activity.get(field)
        if val:
            return _safe_float(val)
    return 0.0


def _get_power(activity: dict) -> Tuple[float, bool]:
    """
    Extrai potência de uma atividade.
    
    Returns:
        Tuple[float, bool]: (potência, é_normalizada)
    """
    np_fields = ['normalizedPower', 'normPower', 'np']
    for field in np_fields:
        val = activity.get(field)
        if val and _safe_float(val) > 0:
            return _safe_float(val), True
    
    avg_fields = ['averagePower', 'avgPower', 'power']
    for field in avg_fields:
        val = activity.get(field)
        if val and _safe_float(val) > 0:
            return _safe_float(val), False
    
    return 0.0, False


# =============================================================================
# CÁLCULO DE TSS (Training Stress Score)
# =============================================================================

def calculate_tss_cycling(
    duration_sec: float, 
    power: float, 
    ftp: float,
    is_normalized: bool = True
) -> float:
    """
    Calcula TSS para ciclismo (baseado em potência).
    
    Fórmula TrainingPeaks:
    TSS = (sec × NP × IF) / (FTP × 3600) × 100
    
    Onde IF = NP/FTP, simplificando:
    TSS = (duration_hours) × IF² × 100
    
    Por definição: 1 hora no FTP = 100 TSS
    
    Args:
        duration_sec: Duração em segundos
        power: Potência (NP preferencialmente, ou média)
        ftp: Functional Threshold Power
        is_normalized: Se a potência fornecida é normalizada
    
    Returns:
        float: TSS calculado
    """
    if duration_sec <= 0 or power <= 0 or ftp <= 0:
        return 0.0
    
    duration_hours = duration_sec / 3600.0
    intensity_factor = power / ftp
    
    # TSS = IF² × hours × 100
    tss = (intensity_factor ** 2) * duration_hours * 100.0
    
    return tss


def calculate_rtss_running(
    duration_sec: float,
    avg_speed_mps: float,
    threshold_pace_sec_per_km: float
) -> float:
    """
    Calcula rTSS (running TSS) baseado em pace.
    
    Fórmula:
    rTSS = (duration_hours) × IF² × 100
    
    Onde:
    - IF = threshold_pace / actual_pace (se threshold = 5:00/km e corremos 4:30/km, IF > 1)
    - Pace mais rápido = maior intensidade
    
    Args:
        duration_sec: Duração em segundos
        avg_speed_mps: Velocidade média em m/s
        threshold_pace_sec_per_km: Pace threshold em segundos por km
    
    Returns:
        float: rTSS calculado
    """
    if duration_sec <= 0 or avg_speed_mps <= 0 or threshold_pace_sec_per_km <= 0:
        return 0.0
    
    # Calcular pace atual em sec/km
    actual_pace_sec_per_km = 1000.0 / avg_speed_mps
    
    if actual_pace_sec_per_km <= 0:
        return 0.0
    
    duration_hours = duration_sec / 3600.0
    
    # IF = threshold/actual (pace menor = mais intenso)
    intensity_factor = threshold_pace_sec_per_km / actual_pace_sec_per_km
    
    # rTSS = IF² × hours × 100
    rtss = (intensity_factor ** 2) * duration_hours * 100.0
    
    return rtss


def calculate_stss_swimming(
    duration_sec: float,
    distance_m: float,
    threshold_pace_sec_per_100m: float
) -> float:
    """
    Calcula sTSS (swimming TSS) baseado em pace de natação.
    
    Fórmula TrainingPeaks:
    sTSS = (duration_hours) × IF² × 100
    
    Args:
        duration_sec: Duração total em segundos
        distance_m: Distância total em metros
        threshold_pace_sec_per_100m: Pace threshold em segundos por 100m
    
    Returns:
        float: sTSS calculado
    """
    if duration_sec <= 0 or distance_m <= 0 or threshold_pace_sec_per_100m <= 0:
        return 0.0
    
    # Calcular pace atual em sec/100m
    actual_pace_sec_per_100m = (duration_sec / distance_m) * 100.0
    
    if actual_pace_sec_per_100m <= 0:
        return 0.0
    
    duration_hours = duration_sec / 3600.0
    
    # IF = threshold/actual (pace menor = mais intenso)
    intensity_factor = threshold_pace_sec_per_100m / actual_pace_sec_per_100m
    
    # sTSS = IF² × hours × 100
    stss = (intensity_factor ** 2) * duration_hours * 100.0
    
    return stss


def calculate_hrtss(
    duration_sec: float,
    avg_hr: float,
    lthr: float,
    hr_max: float = None,
    hr_rest: float = None,
    activity_type: str = 'other'
) -> float:
    """
    Calcula hrTSS (heart rate based TSS) alinhado com TrainingPeaks.
    
    Fórmula base: hrTSS = duration_hours × (avgHR / LTHR)² × 100
    
    Ajustes específicos por tipo de atividade baseados em análise empírica
    comparando com valores reais do TrainingPeaks:
    - Swimming: fator 0.54 (natação ~70% LTHR)
    - Strength_training: fator 1.17 (musculação ~54% LTHR)
    - Other: fator 1.0 (padrão)
    
    Args:
        duration_sec: Duração em segundos
        avg_hr: Frequência cardíaca média
        lthr: Lactate Threshold Heart Rate
        hr_max: FC máxima (não usado nesta implementação)
        hr_rest: FC de repouso (não usado nesta implementação)
        activity_type: Tipo da atividade ('swimming', 'strength_training', 'other')
    
    Returns:
        float: hrTSS calculado
    """
    if duration_sec <= 0 or avg_hr <= 0 or lthr <= 0:
        return 0.0
    
    duration_hours = duration_sec / 3600.0
    hr_intensity_factor = avg_hr / lthr
    base_tss = duration_hours * (hr_intensity_factor ** 2) * 100
    
    # Ajustes específicos por tipo de atividade (calibrados com TrainingPeaks)
    if activity_type == 'swimming':
        # Natação: fator médio 0.54 (range 0.52-0.56)
        adjustment = 0.54
    elif activity_type == 'strength_training':
        # Musculação: fator médio 1.17 (range 1.13-1.20)
        adjustment = 1.17
    else:
        # Outras atividades: fórmula padrão
        adjustment = 1.0
    
    hrtss = base_tss * adjustment
    
    return hrtss


def calculate_trimp(
    duration_sec: float,
    avg_hr: float,
    hr_max: float,
    hr_rest: float,
    gender: str = 'male'
) -> float:
    """
    Calcula TRIMP (Training Impulse) - método Banister.
    
    TRIMP é a base científica original para quantificar carga de treino.
    
    Fórmula (Banister 1991):
    TRIMP = duration_min × HRR × 0.64 × e^(1.92 × HRR)  [homens]
    TRIMP = duration_min × HRR × 0.86 × e^(1.67 × HRR)  [mulheres]
    
    Onde HRR (Heart Rate Reserve) = (avg_hr - hr_rest) / (hr_max - hr_rest)
    
    Args:
        duration_sec: Duração em segundos
        avg_hr: Frequência cardíaca média
        hr_max: FC máxima
        hr_rest: FC de repouso
        gender: 'male' ou 'female'
    
    Returns:
        float: TRIMP calculado
    """
    if duration_sec <= 0 or avg_hr <= 0:
        return 0.0
    
    if hr_max <= hr_rest:
        return 0.0
    
    duration_min = duration_sec / 60.0
    
    # Heart Rate Reserve (Karvonen)
    hrr = (avg_hr - hr_rest) / (hr_max - hr_rest)
    hrr = max(0.0, min(1.0, hrr))  # Limitar entre 0 e 1
    
    # Parâmetros de gênero
    params = TRIMP_GENDER_MALE if gender.lower() == 'male' else TRIMP_GENDER_FEMALE
    k = params['k']
    factor = params['factor']
    
    # TRIMP = duration × HRR × factor × e^(k × HRR)
    trimp = duration_min * hrr * factor * math.exp(k * hrr)
    
    return trimp


def calculate_ttss(
    duration_sec: float,
    avg_hr: float,
    hr_max: float,
    hr_rest: float,
    lthr: float = None
) -> float:
    """
    Calcula tTSS (TRIMP-based TSS).
    
    Usado quando só temos duration e avgHR, sem dados de potência ou pace.
    Converte TRIMP para escala TSS.
    
    TrainingPeaks usa: Um TRIMP de ~100 em treino de 1h no limiar ≈ 100 TSS
    
    Args:
        duration_sec: Duração em segundos
        avg_hr: FC média
        hr_max: FC máxima  
        hr_rest: FC de repouso
        lthr: LTHR (opcional, para melhor calibração)
    
    Returns:
        float: tTSS calculado
    """
    if duration_sec <= 0 or avg_hr <= 0:
        return 0.0
    
    # Calcular TRIMP
    trimp = calculate_trimp(duration_sec, avg_hr, hr_max, hr_rest, 'male')
    
    if trimp <= 0:
        return 0.0
    
    # Calcular TRIMP de referência (1h no LTHR ou 85% HRmax)
    ref_hr = lthr if lthr and lthr > 0 else (hr_max * 0.85)
    ref_trimp = calculate_trimp(3600, ref_hr, hr_max, hr_rest, 'male')
    
    if ref_trimp <= 0:
        # Fallback: usar fator de escala fixo
        # TRIMP típico de 1h moderado ≈ 50-80
        ttss = trimp * 1.25
    else:
        # Escalar para que 1h no threshold = 100 TSS
        ttss = (trimp / ref_trimp) * 100.0
    
    return ttss


# =============================================================================
# FUNÇÃO PRINCIPAL DE CÁLCULO DE TSS
# =============================================================================

def compute_tss_variants(activity: dict, config: dict) -> dict:
    """
    Calcula TSS padronizado para cada modalidade.
    
    PADRONIZAÇÃO POR MODALIDADE:
    - Ciclismo: TSS (power-based) - requer dados de potência e FTP
    - Corrida: rTSS (pace-based) - requer velocidade e pace threshold
    - Natação: hrTSS (heart rate based) - requer FC média e LTHR
    - Força/Outras: hrTSS (heart rate based) - requer FC média e LTHR
    
    Fallback: Se dados específicos não disponíveis, usa estimativa de 50 TSS/hora
    
    Args:
        activity: Dicionário com dados da atividade
        config: Configurações do usuário (ftp, lthr, thresholds, etc)
    
    Returns:
        dict: {
            'tss': float,         # TSS calculado
            'tss_type': str,      # Tipo usado ('tss', 'rtss', 'hrtss', 'estimated')
            'category': str,      # Categoria da atividade
            'breakdown': dict     # Detalhes dos cálculos
        }
    """
    category = _activity_category(activity)
    duration_sec = _safe_float(activity.get('duration', 0))
    
    if duration_sec <= 0:
        return {
            'tss': 0.0,
            'tss_type': 'none',
            'category': category,
            'breakdown': {}
        }
    
    # Extrair configurações
    ftp = _safe_float(config.get('ftp', 0))
    lthr = _safe_float(config.get('hr_threshold', 0)) or _safe_float(config.get('lthr', 0))
    hr_max = _safe_float(config.get('hr_max', 191))
    hr_rest = _safe_float(config.get('hr_rest', 50))
    pace_threshold_str = config.get('pace_threshold', '5:00')
    swim_pace_threshold_str = config.get('swim_pace_threshold', '2:00')
    
    pace_threshold_sec = _parse_mmss_to_seconds(pace_threshold_str, 300)
    swim_pace_threshold_sec = _parse_mmss_to_seconds(swim_pace_threshold_str, 120)
    
    # Extrair dados da atividade
    avg_hr = _get_avg_hr(activity)
    power, is_np = _get_power(activity)
    avg_speed = _safe_float(activity.get('averageSpeed', 0))
    distance = _safe_float(activity.get('distance', 0))
    
    breakdown = {}
    tss_value = 0.0
    tss_type = 'none'
    
    # ==========================================================================
    # CICLISMO - SEMPRE TSS (power-based)
    # ==========================================================================
    if category == 'cycling':
        if power > 0 and ftp > 0:
            tss_value = calculate_tss_cycling(duration_sec, power, ftp, is_np)
            tss_type = 'tss'
            breakdown['tss'] = {
                'value': tss_value,
                'power': power,
                'ftp': ftp,
                'if': power / ftp,
                'duration_h': duration_sec / 3600
            }
        else:
            # Sem dados de potência, usar estimativa básica
            duration_hours = duration_sec / 3600
            tss_value = duration_hours * 50
            tss_type = 'estimated'
            breakdown['estimated'] = {'value': tss_value, 'rate_per_hour': 50}
    
    # ==========================================================================
    # CORRIDA - SEMPRE rTSS (pace-based)
    # ==========================================================================
    elif category == 'running':
        if avg_speed > 0 and pace_threshold_sec > 0:
            tss_value = calculate_rtss_running(duration_sec, avg_speed, pace_threshold_sec)
            tss_type = 'rtss'
            actual_pace = 1000 / avg_speed if avg_speed > 0 else 0
            breakdown['rtss'] = {
                'value': tss_value,
                'avg_speed_mps': avg_speed,
                'actual_pace_sec_km': actual_pace,
                'threshold_pace_sec_km': pace_threshold_sec,
                'if': pace_threshold_sec / actual_pace if actual_pace > 0 else 0
            }
        else:
            # Sem dados de pace, usar estimativa básica
            duration_hours = duration_sec / 3600
            tss_value = duration_hours * 50
            tss_type = 'estimated'
            breakdown['estimated'] = {'value': tss_value, 'rate_per_hour': 50}
    
    # ==========================================================================
    # NATAÇÃO - SEMPRE hrTSS (heart rate based)
    # ==========================================================================
    elif category == 'swimming':
        if avg_hr > 0 and lthr > 0:
            tss_value = calculate_hrtss(duration_sec, avg_hr, lthr, hr_max, hr_rest, activity_type='swimming')
            tss_type = 'hrtss'
            breakdown['hrtss'] = {'value': tss_value, 'avg_hr': avg_hr, 'lthr': lthr}
        elif avg_hr > 0:
            tss_value = calculate_ttss(duration_sec, avg_hr, hr_max, hr_rest, lthr)
            tss_type = 'ttss'
            breakdown['ttss'] = {'value': tss_value, 'avg_hr': avg_hr}
        else:
            # Sem dados de FC, usar estimativa básica
            duration_hours = duration_sec / 3600
            tss_value = duration_hours * 50
            tss_type = 'estimated'
            breakdown['estimated'] = {'value': tss_value, 'rate_per_hour': 50}
    
    # ==========================================================================
    # FORÇA E OUTRAS - SEMPRE hrTSS (heart rate based)
    # ==========================================================================
    else:
        if avg_hr > 0 and lthr > 0:
            # Força/Musculação usa fator específico
            activity_type = 'strength_training' if category == 'strength' else 'other'
            tss_value = calculate_hrtss(duration_sec, avg_hr, lthr, hr_max, hr_rest, activity_type=activity_type)
            tss_type = 'hrtss'
            breakdown['hrtss'] = {'value': tss_value, 'avg_hr': avg_hr, 'lthr': lthr}
        elif avg_hr > 0:
            tss_value = calculate_ttss(duration_sec, avg_hr, hr_max, hr_rest, lthr)
            tss_type = 'ttss'
            breakdown['ttss'] = {'value': tss_value, 'avg_hr': avg_hr}
        else:
            # Estimativa básica: ~50 TSS por hora de atividade moderada
            duration_hours = duration_sec / 3600
            tss_value = duration_hours * 50
            tss_type = 'estimated'
            breakdown['estimated'] = {'value': tss_value, 'rate_per_hour': 50}
    
    return {
        'tss': round(tss_value, 1),
        'tss_type': tss_type,
        'category': category,
        'breakdown': breakdown
    }


# =============================================================================
# CÁLCULO DE MÉTRICAS DE FITNESS (CTL, ATL, TSB)
# =============================================================================

def calculate_fitness_metrics(
    activities: list, 
    config: dict, 
    start_date, 
    end_date,
    initial_ctl: float = 0.0,
    initial_atl: float = 0.0
) -> list:
    """
    Calcula métricas de fitness (CTL, ATL, TSB) baseadas nas atividades.
    
    Fórmulas TrainingPeaks (Exponential Moving Average):
    - CTL_today = CTL_yesterday + (TSS_today - CTL_yesterday) / τ_CTL
    - ATL_today = ATL_yesterday + (TSS_today - ATL_yesterday) / τ_ATL
    - TSB_today = CTL_today - ATL_today
    
    Onde:
    - τ_CTL = 42 dias (constante de tempo para Fitness)
    - τ_ATL = 7 dias (constante de tempo para Fatigue)
    
    Interpretação:
    - CTL (Chronic Training Load): Fitness - capacidade de treino sustentada
    - ATL (Acute Training Load): Fadiga - carga recente acumulada
    - TSB (Training Stress Balance): Form - prontidão para performance
      - TSB positivo (+5 a +25): recuperado, pronto para performance
      - TSB negativo (-10 a -30): fatigado, construindo fitness
      - TSB muito negativo (< -30): risco de overtraining
    
    Args:
        activities: Lista de atividades
        config: Configurações do usuário
        start_date: Data inicial (datetime.date)
        end_date: Data final (datetime.date)
        initial_ctl: CTL inicial (para continuidade de histórico)
        initial_atl: ATL inicial (para continuidade de histórico)
    
    Returns:
        list: Lista de dicionários com métricas diárias
    """
    # Agrupar TSS por data
    daily_tss = {}
    
    for activity in activities:
        start_time = (
            activity.get('startTimeLocal')
            or activity.get('startTime')
            or activity.get('startTimeGMT')
            or activity.get('startTimeUtc')
            or ''
        )
        start_seconds = activity.get('startTimeInSeconds') or activity.get('startTimeInSecondsGMT')

        try:
            if start_time:
                # Normalizar formato de data (aceita "YYYY-MM-DD HH:MM:SS" e ISO)
                if 'T' not in start_time:
                    start_time = start_time.replace(' ', 'T')
                if start_time.endswith('Z'):
                    date = datetime.fromisoformat(start_time.replace('Z', '+00:00')).date()
                else:
                    date = datetime.fromisoformat(start_time).date()
            elif start_seconds:
                date = datetime.utcfromtimestamp(float(start_seconds)).date()
            else:
                continue

            # Reutilizar TSS pré-calculado (quando o app já enriqueceu dinamicamente)
            tss = _safe_float(activity.get('tss', 0.0), 0.0)
            if tss <= 0:
                tss_result = compute_tss_variants(activity, config)
                tss = _safe_float(tss_result.get('tss', 0.0), 0.0)

            # Acumular TSS do dia
            daily_tss[date] = daily_tss.get(date, 0) + tss

        except (ValueError, TypeError, AttributeError):
            continue
    
    # Gerar lista de dias
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    # Calcular métricas usando EMA
    metrics = []
    ctl = initial_ctl
    atl = initial_atl
    
    for day in days:
        tss_today = daily_tss.get(day, 0.0)
        
        # EMA update
        # CTL = CTL_prev + (TSS - CTL_prev) / τ
        ctl = ctl + (tss_today - ctl) / CTL_TIME_CONSTANT
        atl = atl + (tss_today - atl) / ATL_TIME_CONSTANT
        
        # TSB (Form) = CTL (Fitness) - ATL (Fatigue)
        tsb = ctl - atl
        
        metrics.append({
            'date': day.isoformat(),
            'ctl': round(ctl, 1),
            'atl': round(atl, 1),
            'tsb': round(tsb, 1),
            'daily_tss': round(tss_today, 1),
            # Compatibilidade com versões antigas do app/UI
            'daily_load': round(tss_today, 1)
        })
    
    return metrics


def calculate_ramp_rate(metrics: list, days: int = 7) -> float:
    """
    Calcula a taxa de rampa do CTL (variação de fitness por semana).
    
    Recomendações:
    - Ramp rate < 5 TSS/week: conservador, seguro
    - Ramp rate 5-8 TSS/week: ideal para maioria dos atletas
    - Ramp rate > 8 TSS/week: agressivo, risco de lesão/overtraining
    
    Args:
        metrics: Lista de métricas diárias
        days: Período para calcular (padrão 7 dias)
    
    Returns:
        float: Taxa de variação do CTL por semana
    """
    if len(metrics) < days + 1:
        return 0.0
    
    ctl_now = metrics[-1].get('ctl', 0)
    ctl_prev = metrics[-(days + 1)].get('ctl', 0)
    
    ramp_rate = ctl_now - ctl_prev
    
    return round(ramp_rate, 1)


def get_training_phase(tsb: float, ctl: float) -> dict:
    """
    Determina a fase de treino atual baseada em TSB e CTL.
    
    Args:
        tsb: Training Stress Balance atual
        ctl: Chronic Training Load atual
    
    Returns:
        dict: {
            'phase': str,
            'description': str,
            'recommendation': str,
            'color': str
        }
    """
    if tsb > 25:
        return {
            'phase': 'Fresh',
            'description': 'Muito descansado, perdendo fitness',
            'recommendation': 'Aumente o volume de treino gradualmente',
            'color': 'info'
        }
    elif tsb > 5:
        return {
            'phase': 'Rested',
            'description': 'Recuperado, pronto para performance',
            'recommendation': 'Ideal para competições ou treinos de qualidade',
            'color': 'success'
        }
    elif tsb > -10:
        return {
            'phase': 'Neutral',
            'description': 'Balanço equilibrado',
            'recommendation': 'Pode treinar normalmente ou intensificar levemente',
            'color': 'secondary'
        }
    elif tsb > -30:
        return {
            'phase': 'Fatigued',
            'description': 'Acumulando carga, construindo fitness',
            'recommendation': 'Continue o bloco de treino, monitore recuperação',
            'color': 'warning'
        }
    else:
        return {
            'phase': 'Overreaching',
            'description': 'Fadiga alta, risco de overtraining',
            'recommendation': 'Reduza volume/intensidade, priorize recuperação',
            'color': 'danger'
        }
