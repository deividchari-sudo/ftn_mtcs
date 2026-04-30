"""
Cálculos de fitness metrics - versão refatorada.

Implementação das métricas conforme documentação oficial do TrainingPeaks.
Esta é uma versão refatorada do módulo original, mantendo 100% de compatibilidade
comportamental mas com melhor estrutura e testabilidade.
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from domain.models import Activity, TSSResult, TSSType, FitnessMetrics, UserConfig
from config.constants import (
    CTL_TIME_CONSTANT,
    ATL_TIME_CONSTANT,
    HR_ZONE_TSS_PER_HOUR,
    TRIMP_GENDER_MALE,
    TRIMP_GENDER_FEMALE,
)


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
    TSS = (sec × NP × IF) / (FTP × 3600) × 100 = IF² × duration_hours × 100
    
    Por definição: 1 hora no FTP = 100 TSS
    
    Args:
        duration_sec: Duração em segundos
        power: Potência (NP preferencialmente, ou média)
        ftp: Functional Threshold Power
        is_normalized: Se a potência fornecida é normalizada
    
    Returns:
        float: TSS calculado (>= 0)
    """
    if duration_sec <= 0 or power <= 0 or ftp <= 0:
        return 0.0
    
    duration_hours = duration_sec / 3600.0
    intensity_factor = power / ftp
    
    # TSS = IF² × hours × 100
    tss = (intensity_factor ** 2) * duration_hours * 100.0
    
    return max(0.0, tss)


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
    - IF = threshold_pace / actual_pace (pace menor = mais intenso)
    
    Args:
        duration_sec: Duração em segundos
        avg_speed_mps: Velocidade média em m/s
        threshold_pace_sec_per_km: Pace threshold em segundos por km
    
    Returns:
        float: rTSS calculado (>= 0)
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
    
    return max(0.0, rtss)


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
        float: sTSS calculado (>= 0)
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
    
    return max(0.0, stss)


def calculate_hrtss(
    duration_sec: float,
    avg_hr: float,
    lthr: float,
    hr_max: Optional[float] = None,
    hr_rest: Optional[float] = None,
    activity_type: str = 'other'
) -> float:
    """
    Calcula hrTSS baseado em FC média (estimativa quando não há potência/pace).
    
    Metodologia:
    1. Determina zona de FC baseada no LTHR
    2. Usa TSS/hour estimado para aquela zona
    3. Ajusta para duração real
    
    Args:
        duration_sec: Duração em segundos
        avg_hr: FC média durante a atividade
        lthr: FC no limiar (LTHR)
        hr_max: FC máxima (opcional)
        hr_rest: FC em repouso (opcional)
        activity_type: Tipo de atividade
    
    Returns:
        float: hrTSS estimado (>= 0)
    """
    if duration_sec <= 0 or avg_hr <= 0 or lthr <= 0:
        return 0.0
    
    # Determinar zona de FC
    hr_zone = _get_hr_zone(avg_hr, lthr)
    
    # Obter TSS/hour para a zona
    tss_per_hour = HR_ZONE_TSS_PER_HOUR.get(hr_zone, 75)  # Default zona 2
    
    # Calcular TSS proporcional à duração
    duration_hours = duration_sec / 3600.0
    hrtss = tss_per_hour * duration_hours
    
    return max(0.0, hrtss)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def _get_hr_zone(hr: float, lthr: float) -> int:
    """
    Determina a zona de frequência cardíaca baseada no LTHR.
    
    Zonas baseadas em % do LTHR (TrainingPeaks standard):
    - Zone 1: < 81% LTHR (Recovery)
    - Zone 2: 81-89% LTHR (Endurance)
    - Zone 3: 90-93% LTHR (Tempo)
    - Zone 4: 94-99% LTHR (Threshold)
    - Zone 5: 100-102% LTHR (VO2Max)
    - Zone 6: > 102% LTHR (Anaerobic)
    
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
    elif pct < 103:
        return 5
    else:
        return 6


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Converte valor para float de forma segura."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


# =============================================================================
# ORQUESTRADOR DE CÁLCULO DE TSS
# =============================================================================

def calculate_tss_for_activity(
    activity: Activity,
    user_config: UserConfig
) -> TSSResult:
    """
    Orquestra o cálculo de TSS baseado no tipo de atividade e dados disponíveis.
    
    Prioridade de cálculo:
    1. Ciclismo: Potência (NP > Avg Power) > FC
    2. Corrida: Pace > FC
    3. Natação: Pace (CSS) > FC
    4. Outros: FC estimado > Duração estimada
    
    Args:
        activity: Atividade com dados
        user_config: Configurações do usuário (FTP, thresholds, etc)
    
    Returns:
        TSSResult com valor e metadados
    """
    duration_sec = activity.duration.total_seconds()
    
    # CICLISMO: Prioridade para potência
    if activity.type.value == 'cycling':
        power = activity.normalized_power or activity.avg_power
        if power and user_config.ftp > 0:
            tss = calculate_tss_cycling(
                duration_sec=duration_sec,
                power=power,
                ftp=user_config.ftp,
                is_normalized=activity.normalized_power is not None
            )
            return TSSResult(
                value=tss,
                type=TSSType.CYCLING_POWER,
                intensity_factor=power / user_config.ftp,
                normalized_power=activity.normalized_power
            )
    
    # CORRIDA: Prioridade para pace
    if activity.type.value == 'running':
        if activity.avg_speed and user_config.threshold_pace_running > 0:
            tss = calculate_rtss_running(
                duration_sec=duration_sec,
                avg_speed_mps=activity.avg_speed,
                threshold_pace_sec_per_km=user_config.threshold_pace_running
            )
            return TSSResult(
                value=tss,
                type=TSSType.RUNNING_PACE,
                intensity_factor=user_config.get_threshold_speed_running() / activity.avg_speed
            )
    
    # NATAÇÃO: Prioridade para pace
    if activity.type.value == 'swimming':
        if activity.distance_meters and duration_sec > 0 and user_config.threshold_pace_swimming > 0:
            tss = calculate_stss_swimming(
                duration_sec=duration_sec,
                distance_m=activity.distance_meters,
                threshold_pace_sec_per_100m=user_config.threshold_pace_swimming
            )
            return TSSResult(
                value=tss,
                type=TSSType.SWIMMING_PACE
            )
    
    # Fallback: FC (para qualquer atividade)
    if activity.avg_hr and user_config.lthr > 0:
        tss = calculate_hrtss(
            duration_sec=duration_sec,
            avg_hr=activity.avg_hr,
            lthr=user_config.lthr,
            hr_max=user_config.hr_max,
            hr_rest=user_config.hr_rest,
            activity_type=activity.type.value
        )
        return TSSResult(
            value=tss,
            type=TSSType.HR_ESTIMATED
        )
    
    # Último fallback: estimativa baseada apenas em duração (muito aproximado)
    # Assume zona 2 moderada (~75 TSS/hour)
    tss = 75.0 * (duration_sec / 3600.0)
    return TSSResult(
        value=tss,
        type=TSSType.DURATION_ESTIMATED
    )


# =============================================================================
# CÁLCULO DE FITNESS METRICS (CTL, ATL, TSB)
# =============================================================================

def calculate_fitness_metrics(
    daily_tss: List[Tuple[datetime, float]],
    ctl_constant: int = CTL_TIME_CONSTANT,
    atl_constant: int = ATL_TIME_CONSTANT
) -> List[FitnessMetrics]:
    """
    Calcula métricas de fitness (CTL, ATL, TSB) a partir de TSS diário.
    
    Fórmulas (TrainingPeaks):
    - CTL(t) = CTL(t-1) + (TSS(t) - CTL(t-1)) × (1/42)
    - ATL(t) = ATL(t-1) + (TSS(t) - ATL(t-1)) × (1/7)
    - TSB(t) = CTL(t) - ATL(t)
    
    Args:
        daily_tss: Lista de (data, tss) ordenada cronologicamente
        ctl_constant: Constante de tempo para CTL (padrão: 42)
        atl_constant: Constante de tempo para ATL (padrão: 7)
    
    Returns:
        List[FitnessMetrics]: Métricas calculadas para cada dia
    """
    if not daily_tss:
        return []
    
    # Taxas de decaimento exponencial
    ctl_alpha = 1.0 / ctl_constant
    atl_alpha = 1.0 / atl_constant
    
    results = []
    prev_ctl = 0.0
    prev_atl = 0.0
    
    for date, tss in daily_tss:
        # Calcular CTL (Fitness)
        ctl = prev_ctl + (tss - prev_ctl) * ctl_alpha
        
        # Calcular ATL (Fatigue)
        atl = prev_atl + (tss - prev_atl) * atl_alpha
        
        # Calcular TSB (Form)
        tsb = ctl - atl
        
        metrics = FitnessMetrics(
            date=date,
            ctl=round(ctl, 2),
            atl=round(atl, 2),
            tsb=round(tsb, 2),
            daily_tss=tss
        )
        results.append(metrics)
        
        prev_ctl = ctl
        prev_atl = atl
    
    return results


def calculate_trimp(
    duration_min: float,
    avg_hr: float,
    hr_rest: float,
    hr_max: float,
    gender: str = 'male'
) -> float:
    """
    Calcula TRIMP (Training Impulse) de Banister.
    
    Fórmula:
    TRIMP = duration_min × (HR_ratio) × (k ^ (HR_ratio))
    
    Onde HR_ratio = (avg_hr - hr_rest) / (hr_max - hr_rest)
    
    Args:
        duration_min: Duração em minutos
        avg_hr: FC média
        hr_rest: FC em repouso
        hr_max: FC máxima
        gender: 'male' ou 'female'
    
    Returns:
        float: TRIMP calculado
    """
    if duration_min <= 0 or avg_hr <= hr_rest or hr_max <= hr_rest:
        return 0.0
    
    # Constantes por gênero
    if gender.lower() == 'female':
        k = TRIMP_GENDER_FEMALE['k']
    else:
        k = TRIMP_GENDER_MALE['k']
    
    # Ratio de FC
    hr_ratio = (avg_hr - hr_rest) / (hr_max - hr_rest)
    
    # TRIMP
    trimp = duration_min * hr_ratio * (k ** hr_ratio)
    
    return trimp


# =============================================================================
# FUNÇÕES DE CONVERSÃO E PARSING
# =============================================================================

def parse_activity_from_dict(data: Dict[str, Any]) -> Activity:
    """
    Converte dicionário de dados brutos em objeto Activity.
    
    Args:
        data: Dicionário com dados da atividade (formato Garmin/JSON)
    
    Returns:
        Activity: Objeto de domínio
    """
    from domain.models import ActivityType
    
    # Extrair ID
    activity_id = str(data.get('activityId', data.get('id', 'unknown')))
    
    # Determinar tipo
    type_key = data.get('activityType', {}).get('typeKey', '').lower()
    
    if type_key in ['cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling']:
        activity_type = ActivityType.CYCLING
    elif type_key in ['running', 'treadmill_running', 'trail_running']:
        activity_type = ActivityType.RUNNING
    elif type_key in ['swimming', 'pool_swimming', 'open_water_swimming']:
        activity_type = ActivityType.SWIMMING
    elif type_key in ['strength_training', 'weight_training', 'crossfit']:
        activity_type = ActivityType.STRENGTH
    else:
        activity_type = ActivityType.OTHER
    
    # Parse data/hora
    start_time_str = data.get('startTimeLocal', data.get('startTime'))
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        except:
            start_time = datetime.now()
    else:
        start_time = datetime.now()
    
    # Duração
    duration_sec = _safe_float(data.get('duration'), 0)
    duration = timedelta(seconds=duration_sec)
    
    # Criar atividade
    return Activity(
        id=activity_id,
        type=activity_type,
        start_time=start_time,
        duration=duration,
        distance_meters=_safe_float(data.get('distance')),
        avg_power=_safe_float(data.get('averagePower')),
        normalized_power=_safe_float(data.get('normalizedPower')),
        avg_hr=_safe_float(data.get('averageHR')),
        max_hr=_safe_float(data.get('maxHR')),
        avg_speed=_safe_float(data.get('averageSpeed')),
        raw_data=data
    )
