"""
Módulo de Análise Avançada de Potência e Pace
Implementa métricas profissionais: NP, IF, VI, distribuição de zonas
"""
from typing import Dict, List, Optional, Tuple
import math
from datetime import datetime

# =============================================================================
# ANÁLISE DE POTÊNCIA (CICLISMO)
# =============================================================================

def calculate_normalized_power(power_data: List[float], rolling_window: int = 30) -> float:
    """
    Calcula Normalized Power (NP) - métrica mais precisa que potência média
    
    NP leva em conta a natureza não-linear da fadiga, dando mais peso a
    esforços de alta intensidade.
    
    Algoritmo:
    1. Janela móvel de 30s
    2. Elevar cada valor à 4ª potência
    3. Calcular média
    4. Tirar raiz 4ª
    
    Args:
        power_data: Lista de valores de potência (watts)
        rolling_window: Tamanho da janela em segundos (padrão: 30)
        
    Returns:
        Normalized Power em watts
    """
    if not power_data or len(power_data) < rolling_window:
        return 0.0
    
    # Passo 1: Calcular médias móveis de 30s
    rolling_averages = []
    for i in range(len(power_data) - rolling_window + 1):
        window = power_data[i:i + rolling_window]
        avg = sum(window) / len(window)
        rolling_averages.append(avg)
    
    if not rolling_averages:
        return 0.0
    
    # Passo 2-4: Elevar à 4ª potência, média, raiz 4ª
    powered = [p ** 4 for p in rolling_averages]
    mean_powered = sum(powered) / len(powered)
    np_value = mean_powered ** 0.25
    
    return np_value


def calculate_intensity_factor(normalized_power: float, ftp: float) -> float:
    """
    Calcula Intensity Factor (IF) - intensidade relativa ao FTP
    
    IF = NP / FTP
    
    Interpretação:
    - IF < 0.75: Recuperação/Endurance
    - IF 0.75-0.85: Tempo
    - IF 0.85-0.95: Sweetspot
    - IF 0.95-1.05: Threshold
    - IF > 1.05: VO2max ou superior
    
    Args:
        normalized_power: NP calculado
        ftp: Functional Threshold Power
        
    Returns:
        Intensity Factor (0-1+)
    """
    if ftp <= 0:
        return 0.0
    
    return normalized_power / ftp


def calculate_variability_index(normalized_power: float, average_power: float) -> float:
    """
    Calcula Variability Index (VI) - quão variável foi o esforço
    
    VI = NP / Average Power
    
    Interpretação:
    - VI 1.00-1.05: Muito consistente (TT, treino indoor)
    - VI 1.05-1.10: Consistente
    - VI 1.10-1.15: Moderadamente variável
    - VI > 1.15: Muito variável (critério, montanha)
    
    Args:
        normalized_power: NP calculado
        average_power: Potência média do treino
        
    Returns:
        Variability Index
    """
    if average_power <= 0:
        return 1.0
    
    return normalized_power / average_power


def calculate_tss_from_np(normalized_power: float, duration_seconds: float, ftp: float) -> float:
    """
    Calcula Training Stress Score usando Normalized Power
    
    TSS = (duration_hours * NP * IF) / (FTP * 3600) * 100
    
    Mais preciso que usar potência média, especialmente para treinos variáveis.
    
    Args:
        normalized_power: NP calculado
        duration_seconds: Duração do treino em segundos
        ftp: Functional Threshold Power
        
    Returns:
        TSS calculado
    """
    if ftp <= 0 or duration_seconds <= 0:
        return 0.0
    
    intensity_factor = calculate_intensity_factor(normalized_power, ftp)
    duration_hours = duration_seconds / 3600
    
    tss = (duration_hours * normalized_power * intensity_factor) / (ftp * 3600) * 100
    
    return tss


def analyze_power_distribution(
    power_data: List[float],
    ftp: float,
    duration_seconds: float
) -> Dict:
    """
    Analisa distribuição de potência em zonas
    
    Args:
        power_data: Lista de valores de potência
        ftp: FTP do atleta
        duration_seconds: Duração total
        
    Returns:
        Dict com tempo em cada zona e percentuais
    """
    if not power_data or ftp <= 0:
        return {}
    
    # Definir zonas baseadas em FTP
    zones = {
        'z1': (0, 0.55 * ftp),
        'z2': (0.55 * ftp, 0.75 * ftp),
        'z3': (0.75 * ftp, 0.90 * ftp),
        'z4': (0.90 * ftp, 1.05 * ftp),
        'z5': (1.05 * ftp, 1.20 * ftp),
        'z6': (1.20 * ftp, float('inf'))
    }
    
    # Contar tempo em cada zona (1 sample = 1 segundo)
    time_in_zones = {zone: 0 for zone in zones.keys()}
    
    for power in power_data:
        for zone_name, (min_p, max_p) in zones.items():
            if min_p <= power < max_p:
                time_in_zones[zone_name] += 1
                break
    
    total_samples = len(power_data)
    
    # Calcular percentuais
    distribution = {}
    for zone, time_samples in time_in_zones.items():
        percentage = (time_samples / total_samples * 100) if total_samples > 0 else 0
        distribution[zone] = {
            'time_seconds': time_samples,
            'time_minutes': time_samples / 60,
            'percentage': percentage
        }
    
    return distribution


def calculate_peak_powers(power_data: List[float], durations: List[int] = None) -> Dict:
    """
    Calcula potências máximas para diferentes durações (power curve)
    
    Args:
        power_data: Lista de valores de potência
        durations: Durações em segundos para calcular (padrão: 5s, 1min, 5min, 20min)
        
    Returns:
        Dict com picos de potência
    """
    if not power_data:
        return {}
    
    if durations is None:
        durations = [5, 60, 300, 1200]  # 5s, 1min, 5min, 20min
    
    peaks = {}
    
    for duration in durations:
        if len(power_data) < duration:
            peaks[f'{duration}s'] = 0
            continue
        
        # Calcular média móvel máxima
        max_avg = 0
        for i in range(len(power_data) - duration + 1):
            window = power_data[i:i + duration]
            avg = sum(window) / len(window)
            max_avg = max(max_avg, avg)
        
        peaks[f'{duration}s'] = round(max_avg, 1)
    
    return peaks


# =============================================================================
# ANÁLISE DE PACE (CORRIDA)
# =============================================================================

def calculate_gap(pace_min_per_km: float, elevation_gain: float, distance_km: float) -> float:
    """
    Calcula Grade Adjusted Pace (GAP) - pace ajustado por elevação
    
    Ajusta o pace para equivalente de terreno plano, permitindo
    comparação justa entre corridas com diferentes perfis.
    
    Args:
        pace_min_per_km: Pace em minutos por km
        elevation_gain: Ganho de elevação em metros
        distance_km: Distância em km
        
    Returns:
        GAP em minutos por km
    """
    if distance_km <= 0:
        return pace_min_per_km
    
    # Calcular grade média
    grade_percent = (elevation_gain / (distance_km * 1000)) * 100
    
    # Ajuste por grade (aproximação)
    # Cada 1% de subida adiciona ~10-12 segundos por km
    adjustment = grade_percent * 0.2  # minutos por km
    
    gap = pace_min_per_km - adjustment
    
    return max(gap, 2.0)  # Mínimo razoável


def analyze_pace_distribution(
    pace_data: List[float],
    threshold_pace: float,
    duration_seconds: float
) -> Dict:
    """
    Analisa distribuição de pace em zonas de corrida
    
    Args:
        pace_data: Lista de paces (min/km)
        threshold_pace: Pace threshold do atleta
        duration_seconds: Duração total
        
    Returns:
        Dict com tempo em cada zona
    """
    if not pace_data or threshold_pace <= 0:
        return {}
    
    # Definir zonas baseadas em threshold pace
    # Zonas invertidas: pace menor = mais rápido
    zones = {
        'z1': (threshold_pace * 1.15, float('inf')),  # Mais lento
        'z2': (threshold_pace * 1.05, threshold_pace * 1.15),
        'z3': (threshold_pace * 0.98, threshold_pace * 1.05),
        'z4': (threshold_pace * 0.90, threshold_pace * 0.98),  # Threshold
        'z5': (threshold_pace * 0.85, threshold_pace * 0.90),
        'z6': (0, threshold_pace * 0.85)  # Mais rápido
    }
    
    # Contar tempo em cada zona
    time_in_zones = {zone: 0 for zone in zones.keys()}
    
    for pace in pace_data:
        if pace <= 0:  # Ignorar paces inválidos
            continue
        for zone_name, (min_p, max_p) in zones.items():
            if min_p <= pace < max_p:
                time_in_zones[zone_name] += 1
                break
    
    total_samples = len([p for p in pace_data if p > 0])
    
    # Calcular percentuais
    distribution = {}
    for zone, time_samples in time_in_zones.items():
        percentage = (time_samples / total_samples * 100) if total_samples > 0 else 0
        distribution[zone] = {
            'time_seconds': time_samples,
            'time_minutes': time_samples / 60,
            'percentage': percentage
        }
    
    return distribution


def calculate_pace_variability(pace_data: List[float]) -> Dict:
    """
    Calcula variabilidade do pace durante corrida
    
    Args:
        pace_data: Lista de paces (min/km)
        
    Returns:
        Dict com estatísticas de variabilidade
    """
    if not pace_data:
        return {}
    
    valid_paces = [p for p in pace_data if p > 0]
    
    if not valid_paces:
        return {}
    
    mean_pace = sum(valid_paces) / len(valid_paces)
    
    # Calcular desvio padrão
    variance = sum((p - mean_pace) ** 2 for p in valid_paces) / len(valid_paces)
    std_dev = variance ** 0.5
    
    # Coeficiente de variação
    cv = (std_dev / mean_pace) * 100 if mean_pace > 0 else 0
    
    # Interpretar consistência
    if cv < 5:
        consistency = "Muito consistente"
    elif cv < 10:
        consistency = "Consistente"
    elif cv < 15:
        consistency = "Moderadamente variável"
    else:
        consistency = "Muito variável"
    
    return {
        'mean_pace': mean_pace,
        'std_dev': std_dev,
        'cv_percent': cv,
        'consistency': consistency,
        'min_pace': min(valid_paces),
        'max_pace': max(valid_paces)
    }


# =============================================================================
# ANÁLISE DE NATAÇÃO
# =============================================================================

def calculate_swim_efficiency(
    distance_m: float,
    duration_seconds: float,
    stroke_count: Optional[int] = None
) -> Dict:
    """
    Calcula eficiência de natação (SWOLF e pace)
    
    Args:
        distance_m: Distância nadada em metros
        duration_seconds: Duração em segundos
        stroke_count: Número de braçadas (opcional)
        
    Returns:
        Dict com métricas de eficiência
    """
    if distance_m <= 0 or duration_seconds <= 0:
        return {}
    
    # Pace (segundos por 100m)
    pace_per_100m = (duration_seconds / distance_m) * 100
    
    # Velocidade (m/s)
    speed_ms = distance_m / duration_seconds
    
    result = {
        'pace_per_100m': pace_per_100m,
        'speed_ms': speed_ms,
        'pace_formatted': format_swim_pace(pace_per_100m)
    }
    
    # SWOLF (stroke count + time para 25m ou 50m)
    if stroke_count:
        # Assumir pool de 25m
        pool_length = 25
        num_lengths = distance_m / pool_length
        avg_strokes_per_length = stroke_count / num_lengths if num_lengths > 0 else 0
        time_per_length = duration_seconds / num_lengths if num_lengths > 0 else 0
        
        swolf = avg_strokes_per_length + time_per_length
        
        result['swolf'] = round(swolf, 1)
        result['strokes_per_length'] = round(avg_strokes_per_length, 1)
        result['efficiency_note'] = interpret_swolf(swolf)
    
    return result


def interpret_swolf(swolf: float) -> str:
    """Interpreta valor de SWOLF"""
    if swolf < 35:
        return "Excelente eficiência"
    elif swolf < 40:
        return "Boa eficiência"
    elif swolf < 45:
        return "Eficiência moderada"
    else:
        return "Precisa melhorar técnica"


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def format_swim_pace(seconds_per_100m: float) -> str:
    """Formata pace de natação"""
    if seconds_per_100m <= 0:
        return "N/A"
    minutes = int(seconds_per_100m // 60)
    seconds = int(seconds_per_100m % 60)
    return f"{minutes}:{seconds:02d}/100m"


def generate_power_summary(workout: Dict, ftp: float) -> Dict:
    """
    Gera resumo completo de análise de potência para um treino
    
    Args:
        workout: Dict com dados do treino incluindo power_data
        ftp: FTP do atleta
        
    Returns:
        Dict com todas as métricas calculadas
    """
    power_data = workout.get('power_stream', [])
    
    if not power_data:
        return {'error': 'Sem dados de potência'}
    
    avg_power = sum(power_data) / len(power_data) if power_data else 0
    duration = workout.get('duration', 0)
    
    # Métricas principais
    np = calculate_normalized_power(power_data)
    if_value = calculate_intensity_factor(np, ftp)
    vi = calculate_variability_index(np, avg_power)
    tss = calculate_tss_from_np(np, duration, ftp)
    
    # Distribuição e picos
    distribution = analyze_power_distribution(power_data, ftp, duration)
    peaks = calculate_peak_powers(power_data)
    
    return {
        'average_power': round(avg_power, 1),
        'normalized_power': round(np, 1),
        'intensity_factor': round(if_value, 3),
        'variability_index': round(vi, 3),
        'tss': round(tss, 1),
        'distribution': distribution,
        'peak_powers': peaks,
        'interpretation': interpret_metrics(if_value, vi)
    }


def interpret_metrics(if_value: float, vi: float) -> Dict:
    """Interpreta IF e VI"""
    # Interpretar IF
    if if_value < 0.75:
        if_interp = "Recuperação/Endurance"
    elif if_value < 0.85:
        if_interp = "Tempo"
    elif if_value < 0.95:
        if_interp = "Sweetspot"
    elif if_value <= 1.05:
        if_interp = "Threshold"
    else:
        if_interp = "VO2max+"
    
    # Interpretar VI
    if vi <= 1.05:
        vi_interp = "Muito consistente"
    elif vi <= 1.10:
        vi_interp = "Consistente"
    elif vi <= 1.15:
        vi_interp = "Moderadamente variável"
    else:
        vi_interp = "Muito variável"
    
    return {
        'intensity': if_interp,
        'consistency': vi_interp
    }
