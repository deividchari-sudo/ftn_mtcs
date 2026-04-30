"""
Módulo de Predição de Tempo de Prova para Triathlon
Usa fórmulas científicas baseadas em VO2max, FTP, CSS e dados históricos
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# =============================================================================
# CONSTANTES E FÓRMULAS CIENTÍFICAS
# =============================================================================

# Riegel's Formula - expoente para extrapolação de tempo
RIEGEL_EXPONENT = 1.06

# Fatores de conversão de distâncias
METERS_PER_KM = 1000
SECONDS_PER_HOUR = 3600
MINUTES_PER_HOUR = 60

# Distâncias padrão de provas (em metros)
RACE_DISTANCES = {
    'sprint': {
        'swim': 750,
        'bike': 20000,
        'run': 5000,
        'name': 'Sprint',
        'transitions': 180  # 3 min total
    },
    'olympic': {
        'swim': 1500,
        'bike': 40000,
        'run': 10000,
        'name': 'Olímpico',
        'transitions': 240  # 4 min total
    },
    'half_ironman': {
        'swim': 1900,
        'bike': 90000,
        'run': 21097,
        'name': 'Half Ironman (70.3)',
        'transitions': 600  # 10 min total
    },
    'ironman': {
        'swim': 3800,
        'bike': 180000,
        'run': 42195,
        'name': 'Ironman',
        'transitions': 900  # 15 min total
    }
}

# =============================================================================
# PREDIÇÃO DE CORRIDA
# =============================================================================

def predict_run_time(
    threshold_pace: float,
    distance_km: float,
    vo2max: Optional[float] = None,
    recent_runs: Optional[List[Dict]] = None
) -> Dict:
    """
    Prediz tempo de corrida baseado no threshold pace e VO2max
    
    Args:
        threshold_pace: Pace threshold em min/km (ex: 4.37 = 4:22/km)
        distance_km: Distância da prova em km
        vo2max: VO2max em ml/kg/min (opcional)
        recent_runs: Lista de corridas recentes para ajuste (opcional)
        
    Returns:
        Dict com predição de tempo e paces
    """
    # Riegel's Formula para extrapolação
    # T2 = T1 * (D2/D1)^1.06
    
    # Usar threshold como referência
    # Threshold pace tipicamente é pace de 1 hora (FTP running)
    # Para uma corrida longa, assumir que pode manter threshold em ~60min
    threshold_time_seconds = threshold_pace * 60  # Threshold em segundos/km
    threshold_distance_km = 1.0  # Referência de 1km
    
    # Calcular tempo previsto usando Riegel
    # Para prova, usar 95-105% do threshold dependendo da distância
    race_pace_multiplier = 1.0
    if distance_km <= 5:
        race_pace_multiplier = 0.95  # Pode ir mais rápido em distâncias curtas
    elif distance_km <= 10:
        race_pace_multiplier = 1.0   # No threshold
    elif distance_km <= 21:
        race_pace_multiplier = 1.05  # Um pouco mais lento (meia maratona)
    else:
        race_pace_multiplier = 1.12  # Muito mais lento (maratona/ultra)
    
    # Tempo base usando Riegel
    base_pace_seconds_per_km = threshold_time_seconds * race_pace_multiplier
    predicted_seconds = base_pace_seconds_per_km * distance_km
    
    # Ajuste baseado em VO2max (se disponível)
    if vo2max:
        # VO2max médio para corredores é ~45-55 ml/kg/min
        # Ajustar baseado na diferença da média
        vo2max_adjustment = 1.0
        if vo2max > 60:
            vo2max_adjustment = 0.90  # Elite, muito mais rápido
        elif vo2max > 55:
            vo2max_adjustment = 0.95  # Muito bom
        elif vo2max > 50:
            vo2max_adjustment = 0.98  # Bom
        elif vo2max < 35:
            vo2max_adjustment = 1.10  # Iniciante
        elif vo2max < 40:
            vo2max_adjustment = 1.05  # Abaixo da média
        
        predicted_seconds *= vo2max_adjustment
    
    # Ajuste baseado em corridas recentes
    if recent_runs and len(recent_runs) >= 3:
        # Calcular pace médio real das corridas recentes (min/km)
        recent_paces = []
        for r in recent_runs[:10]:
            dist = r.get('distance', 0) / 1000  # km
            dur = r.get('duration', 0) / 60     # minutos
            if dist > 0 and dur > 0:
                pace_min_per_km = dur / dist
                recent_paces.append(pace_min_per_km)
        
        if recent_paces:
            avg_recent_pace = sum(recent_paces) / len(recent_paces)
            # Se o pace real recente é muito diferente do threshold, ajustar
            # Blend 60% predição teórica + 40% realidade
            theoretical_pace = predicted_seconds / 60 / distance_km
            blended_pace = theoretical_pace * 0.6 + avg_recent_pace * 0.4
            predicted_seconds = blended_pace * distance_km * 60
    
    predicted_minutes = predicted_seconds / 60
    predicted_pace = predicted_minutes / distance_km
    
    # Calcular paces por zona (conservative, realistic, optimistic)
    conservative_seconds = predicted_seconds * 1.05
    optimistic_seconds = predicted_seconds * 0.95
    
    return {
        'distance_km': distance_km,
        'predicted_time_seconds': predicted_seconds,
        'predicted_time_formatted': format_time_seconds(predicted_seconds),
        'predicted_pace': predicted_pace,
        'predicted_pace_formatted': format_pace(predicted_pace),
        'conservative': {
            'time_seconds': conservative_seconds,
            'time_formatted': format_time_seconds(conservative_seconds),
            'pace_formatted': format_pace(conservative_seconds / 60 / distance_km)
        },
        'optimistic': {
            'time_seconds': optimistic_seconds,
            'time_formatted': format_time_seconds(optimistic_seconds),
            'pace_formatted': format_pace(optimistic_seconds / 60 / distance_km)
        }
    }


def calculate_vdot(distance_km: float, time_seconds: float) -> float:
    """
    Calcula VDOT (Jack Daniels) baseado em performance
    
    Args:
        distance_km: Distância em km
        time_seconds: Tempo em segundos
        
    Returns:
        VDOT estimado
    """
    distance_meters = distance_km * 1000
    minutes = time_seconds / 60
    
    # Fórmula simplificada de VDOT
    velocity_m_per_min = distance_meters / minutes
    
    # VO2 = -4.60 + 0.182258 * v + 0.000104 * v^2
    vo2 = -4.60 + 0.182258 * velocity_m_per_min + 0.000104 * (velocity_m_per_min ** 2)
    
    # Percentual do VO2max baseado no tempo de prova
    if minutes < 2.5:
        percent_vo2max = 1.0
    elif minutes < 10:
        percent_vo2max = 0.95
    elif minutes < 30:
        percent_vo2max = 0.90
    else:
        percent_vo2max = 0.85
    
    vdot = vo2 / percent_vo2max
    return max(vdot, 30)  # Mínimo razoável


# =============================================================================
# PREDIÇÃO DE CICLISMO
# =============================================================================

def predict_bike_time(
    ftp: float,
    distance_km: float,
    elevation_gain: float = 0,
    recent_rides: Optional[List[Dict]] = None
) -> Dict:
    """
    Prediz tempo de ciclismo baseado no FTP
    
    Args:
        ftp: Functional Threshold Power em watts
        distance_km: Distância em km
        elevation_gain: Ganho de elevação em metros (opcional)
        recent_rides: Lista de pedais recentes (opcional)
        
    Returns:
        Dict com predição de tempo e potências
    """
    # Assumir peso de 70kg (pode ser parametrizado depois)
    assumed_weight_kg = 70
    watts_per_kg = ftp / assumed_weight_kg
    
    # Velocidade base em km/h baseada em watts/kg (modelo empírico)
    # Relação típica:
    # - 2.5 W/kg = ~28 km/h
    # - 3.0 W/kg = ~32 km/h
    # - 3.5 W/kg = ~35 km/h
    # - 4.0 W/kg = ~38 km/h
    base_speed_kmh = 18 + (watts_per_kg * 5.5)
    
    # Ajustar por elevação (cada 100m de elevação reduz ~1.5-2 km/h)
    elevation_penalty_kmh = (elevation_gain / 100) * 1.8
    adjusted_speed_kmh = max(base_speed_kmh - elevation_penalty_kmh, 15)
    
    # Para prova longa, assumir intensidade de 70-80% do FTP
    race_intensity = 0.75
    # Intensidade afeta velocidade de forma não-linear (aproximadamente raiz cúbica)
    race_speed_kmh = adjusted_speed_kmh * (race_intensity ** 0.33)
    
    # Ajuste baseado em pedais recentes
    if recent_rides and len(recent_rides) >= 3:
        recent_speeds = []
        for r in recent_rides[:10]:
            dist = r.get('distance', 0) / 1000  # km
            dur = r.get('duration', 0) / 3600   # horas
            if dist > 0 and dur > 0:
                speed = dist / dur
                recent_speeds.append(speed)
        
        if recent_speeds:
            recent_avg_speed = sum(recent_speeds) / len(recent_speeds)
            # Blend 70% teórico + 30% realidade
            race_speed_kmh = race_speed_kmh * 0.7 + recent_avg_speed * 0.3
    
    predicted_hours = distance_km / race_speed_kmh
    predicted_seconds = predicted_hours * SECONDS_PER_HOUR
    
    # Calcular potência alvo
    target_power = ftp * race_intensity
    
    # Cenários
    conservative_seconds = predicted_seconds * 1.08
    optimistic_seconds = predicted_seconds * 0.92
    
    return {
        'distance_km': distance_km,
        'predicted_time_seconds': predicted_seconds,
        'predicted_time_formatted': format_time_seconds(predicted_seconds),
        'predicted_speed_kmh': race_speed_kmh,
        'target_power_watts': target_power,
        'target_power_percent_ftp': race_intensity * 100,
        'conservative': {
            'time_seconds': conservative_seconds,
            'time_formatted': format_time_seconds(conservative_seconds),
            'speed_kmh': distance_km / (conservative_seconds / 3600)
        },
        'optimistic': {
            'time_seconds': optimistic_seconds,
            'time_formatted': format_time_seconds(optimistic_seconds),
            'speed_kmh': distance_km / (optimistic_seconds / 3600)
        }
    }


# =============================================================================
# PREDIÇÃO DE NATAÇÃO
# =============================================================================

def predict_swim_time(
    css: float,
    distance_m: float,
    recent_swims: Optional[List[Dict]] = None
) -> Dict:
    """
    Prediz tempo de natação baseado no CSS (Critical Swim Speed)
    
    Args:
        css: Critical Swim Speed em segundos/100m
        distance_m: Distância em metros
        recent_swims: Lista de nados recentes (opcional)
        
    Returns:
        Dict com predição de tempo e paces
    """
    # CSS é o pace sustentável (~threshold)
    # Para prova, adicionar 3-5% de margem
    race_pace_per_100m = css * 1.04
    
    # Calcular tempo total
    num_hundreds = distance_m / 100
    predicted_seconds = race_pace_per_100m * num_hundreds
    
    # Ajuste baseado em nados recentes
    if recent_swims and len(recent_swims) >= 3:
        recent_avg_pace = sum(
            (r.get('duration', 0)) / (r.get('distance', 1) / 100)
            for r in recent_swims[:5] if r.get('distance', 0) > 0
        ) / min(len(recent_swims), 5)
        
        if recent_avg_pace > 0:
            # Blend
            predicted_seconds = (predicted_seconds * 0.7 + 
                               (recent_avg_pace * num_hundreds) * 0.3)
    
    predicted_pace_per_100m = predicted_seconds / num_hundreds
    
    # Cenários
    conservative_seconds = predicted_seconds * 1.05
    optimistic_seconds = predicted_seconds * 0.95
    
    return {
        'distance_m': distance_m,
        'predicted_time_seconds': predicted_seconds,
        'predicted_time_formatted': format_time_seconds(predicted_seconds),
        'predicted_pace_per_100m': predicted_pace_per_100m,
        'predicted_pace_formatted': format_swim_pace(predicted_pace_per_100m),
        'conservative': {
            'time_seconds': conservative_seconds,
            'time_formatted': format_time_seconds(conservative_seconds),
            'pace_formatted': format_swim_pace(conservative_seconds / num_hundreds)
        },
        'optimistic': {
            'time_seconds': optimistic_seconds,
            'time_formatted': format_time_seconds(optimistic_seconds),
            'pace_formatted': format_swim_pace(optimistic_seconds / num_hundreds)
        }
    }


# =============================================================================
# PREDIÇÃO DE TRIATHLON COMPLETO
# =============================================================================

def predict_triathlon_time(
    race_type: str,
    css: float,
    ftp: float,
    threshold_pace: float,
    vo2max: Optional[float] = None,
    recent_workouts: Optional[List[Dict]] = None,
    elevation_gain: float = 0
) -> Dict:
    """
    Prediz tempo completo de triathlon (swim + T1 + bike + T2 + run)
    
    Args:
        race_type: Tipo de prova ('sprint', 'olympic', 'half_ironman', 'ironman')
        css: Critical Swim Speed em segundos/100m
        ftp: Functional Threshold Power em watts
        threshold_pace: Pace threshold corrida em min/km
        vo2max: VO2max em ml/kg/min (opcional)
        recent_workouts: Histórico de treinos (opcional)
        elevation_gain: Elevação do ciclismo em metros
        
    Returns:
        Dict com predição completa do triathlon
    """
    if race_type not in RACE_DISTANCES:
        raise ValueError(f"Tipo de prova inválido: {race_type}")
    
    race_info = RACE_DISTANCES[race_type]
    
    # Separar workouts por modalidade
    recent_swims = []
    recent_bikes = []
    recent_runs = []
    
    if recent_workouts:
        for w in recent_workouts:
            activity_type = w.get('activityType', {}).get('typeKey', '')
            if activity_type == 'lap_swimming':
                recent_swims.append(w)
            elif activity_type == 'cycling':
                recent_bikes.append(w)
            elif activity_type == 'running':
                recent_runs.append(w)
    
    # Predição de natação
    swim_pred = predict_swim_time(
        css=css,
        distance_m=race_info['swim'],
        recent_swims=recent_swims
    )
    
    # Predição de ciclismo
    bike_pred = predict_bike_time(
        ftp=ftp,
        distance_km=race_info['bike'] / 1000,
        elevation_gain=elevation_gain,
        recent_rides=recent_bikes
    )
    
    # Predição de corrida
    run_pred = predict_run_time(
        threshold_pace=threshold_pace,
        distance_km=race_info['run'] / 1000,
        vo2max=vo2max,
        recent_runs=recent_runs
    )
    
    # Tempo total (realístico)
    total_seconds = (
        swim_pred['predicted_time_seconds'] +
        bike_pred['predicted_time_seconds'] +
        run_pred['predicted_time_seconds'] +
        race_info['transitions']
    )
    
    # Cenário conservador
    conservative_total = (
        swim_pred['conservative']['time_seconds'] +
        bike_pred['conservative']['time_seconds'] +
        run_pred['conservative']['time_seconds'] +
        race_info['transitions'] * 1.2
    )
    
    # Cenário otimista
    optimistic_total = (
        swim_pred['optimistic']['time_seconds'] +
        bike_pred['optimistic']['time_seconds'] +
        run_pred['optimistic']['time_seconds'] +
        race_info['transitions'] * 0.9
    )
    
    return {
        'race_type': race_type,
        'race_name': race_info['name'],
        'distances': {
            'swim_m': race_info['swim'],
            'bike_km': race_info['bike'] / 1000,
            'run_km': race_info['run'] / 1000
        },
        'swim': swim_pred,
        'bike': bike_pred,
        'run': run_pred,
        'transitions_seconds': race_info['transitions'],
        'predicted_total_seconds': total_seconds,
        'predicted_total_formatted': format_time_seconds(total_seconds),
        'conservative': {
            'total_seconds': conservative_total,
            'total_formatted': format_time_seconds(conservative_total)
        },
        'optimistic': {
            'total_seconds': optimistic_total,
            'total_formatted': format_time_seconds(optimistic_total)
        },
        'splits': {
            'swim_percent': (swim_pred['predicted_time_seconds'] / total_seconds) * 100,
            'bike_percent': (bike_pred['predicted_time_seconds'] / total_seconds) * 100,
            'run_percent': (run_pred['predicted_time_seconds'] / total_seconds) * 100,
            'transitions_percent': (race_info['transitions'] / total_seconds) * 100
        }
    }


# =============================================================================
# ANÁLISE DE FACTIBILIDADE
# =============================================================================

def analyze_race_readiness(
    target_race: str,
    current_ctl: float,
    recent_workouts: List[Dict],
    race_date: Optional[datetime] = None
) -> Dict:
    """
    Analisa se o atleta está pronto para a prova alvo
    
    Args:
        target_race: Tipo de prova
        current_ctl: CTL atual (fitness)
        recent_workouts: Histórico de treinos
        race_date: Data da prova (opcional)
        
    Returns:
        Dict com análise de prontidão
    """
    # CTL mínimo recomendado por tipo de prova
    recommended_ctl = {
        'sprint': 30,
        'olympic': 45,
        'half_ironman': 65,
        'ironman': 85
    }
    
    target_ctl = recommended_ctl.get(target_race, 50)
    ctl_deficit = target_ctl - current_ctl
    
    # Analisar volume recente (últimas 4 semanas)
    four_weeks_ago = datetime.now() - timedelta(days=28)
    recent = [w for w in recent_workouts 
              if datetime.strptime(w.get('startTimeLocal', '')[:10], '%Y-%m-%d') >= four_weeks_ago]
    
    total_distance = sum(w.get('distance', 0) for w in recent) / 1000
    total_hours = sum(w.get('duration', 0) for w in recent) / 3600
    
    # Determinar status
    if current_ctl >= target_ctl:
        status = 'ready'
        message = f"✅ Você está pronto! Seu CTL ({current_ctl:.1f}) está acima do recomendado ({target_ctl})."
    elif ctl_deficit <= 10:
        status = 'almost_ready'
        message = f"⚠️ Quase pronto! Faltam {ctl_deficit:.1f} pontos de CTL. Continue treinando consistentemente."
    else:
        status = 'not_ready'
        weeks_needed = int(ctl_deficit / 3)  # ~3 CTL por semana é ganho razoável
        message = f"❌ Ainda não. Faltam {ctl_deficit:.1f} pontos de CTL. Estima-se {weeks_needed} semanas de treino."
    
    # Recomendações
    recommendations = []
    
    if total_hours < 5:
        recommendations.append("Aumente o volume para pelo menos 7-8 horas por semana")
    
    if ctl_deficit > 0:
        recommended_weekly_tss = target_ctl * 0.7  # ~70% do CTL como TSS semanal
        recommendations.append(f"Meta semanal: ~{recommended_weekly_tss:.0f} TSS")
    
    if race_date:
        days_until_race = (race_date - datetime.now()).days
        if days_until_race < 14:
            recommendations.append("⚠️ Menos de 2 semanas! Foque em recuperação e taper.")
        elif days_until_race < 30:
            recommendations.append("Última fase de preparação. Mantenha volume e intensidade.")
    
    return {
        'status': status,
        'message': message,
        'current_ctl': current_ctl,
        'target_ctl': target_ctl,
        'ctl_deficit': max(ctl_deficit, 0),
        'recent_volume': {
            'distance_km': total_distance,
            'hours': total_hours
        },
        'recommendations': recommendations,
        'race_type': target_race,
        'race_name': RACE_DISTANCES[target_race]['name']
    }


# =============================================================================
# FUNÇÕES AUXILIARES DE FORMATAÇÃO
# =============================================================================

def format_time_seconds(seconds: float) -> str:
    """Formata segundos em HH:MM:SS"""
    # ✅ FIXO: Validar None e negativos
    if seconds is None or seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_pace(minutes_per_km: float) -> str:
    """Formata pace de corrida em mm:ss/km"""
    minutes = int(minutes_per_km)
    seconds = int((minutes_per_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}/km"


def format_swim_pace(seconds_per_100m: float) -> str:
    """Formata pace de natação em mm:ss/100m"""
    minutes = int(seconds_per_100m // 60)
    seconds = int(seconds_per_100m % 60)
    return f"{minutes}:{seconds:02d}/100m"


def parse_time_string(time_str: str) -> float:
    """Converte string HH:MM:SS para segundos"""
    parts = time_str.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return float(parts[0])
