"""
Análise Avançada de Potência para Ciclismo
===========================================

Módulo completo de análise de power para ciclistas.
Detecta FTP, calcula NP (já implementado), VI, power curve, quadrant analysis.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# ==================== FTP Detection ====================

def estimate_ftp_from_workouts(rides: List[Dict]) -> Optional[float]:
    """
    Estima FTP (Functional Threshold Power) a partir do histórico de rides.
    
    Metodologia:
    1. Procura por treinos de threshold (20-40 min no ritmo máximo sustentável)
    2. Calcula potência média desses treinos
    3. FTP ≈ Potência média de ~30-40 min esforço máximo
    
    Args:
        rides: Lista de rides com dados de potência
               Esperado: {'distance_km': float, 'duration_s': float, 
                         'avg_power_w': float, 'type': str}
        
    Returns:
        FTP estimado em watts, ou None se dados insuficientes
    """
    if not rides or len(rides) < 5:
        return None
    
    # Filtra rides de threshold (20-60 minutos, alta intensidade)
    threshold_rides = []
    for ride in rides:
        duration_min = ride.get('duration_s', 0) / 60
        avg_power = ride.get('avg_power_w', 0)
        ride_type = ride.get('type', '').lower()
        intensity = ride.get('intensity_factor', ride.get('avg_power_w', 0) / 250)  # Assume FTP=250 default
        
        # Identifica threshold rides
        if (20 <= duration_min <= 60) and (intensity > 0.85 or 'threshold' in ride_type or 'tempo' in ride_type):
            threshold_rides.append(ride)
    
    if not threshold_rides:
        # Se não houver threshold identificado, usa as rides com maior potência média
        rides_sorted = sorted(rides, 
                             key=lambda x: x.get('avg_power_w', 0),
                             reverse=True)
        # Filtra rides de 20+ min com alta potência
        threshold_rides = [r for r in rides_sorted 
                          if (r.get('duration_s', 0) / 60) >= 20][:5]
    
    if not threshold_rides:
        return None
    
    # Calcula potência média dos threshold rides
    ftp_estimates = []
    for ride in threshold_rides:
        avg_power = ride.get('avg_power_w', 0)
        if avg_power > 0:
            # FTP é aproximadamente 95% da potência máxima sustentável por 1 hora
            # Para rides de ~30-40 min, FTP ≈ 90-95% da média
            ftp_estimate = avg_power * 0.95
            ftp_estimates.append(ftp_estimate)
    
    if not ftp_estimates:
        return None
    
    return np.mean(ftp_estimates)


def detect_ftp_test_result(power_data: List[float], duration_s: float) -> Optional[float]:
    """
    Detecta resultado de teste FTP (20 min all-out).
    
    Metodologia: FTP = 95% da potência média em 20 min
    Remove primeiros 3 min (aquecimento) e últimos 3 min (fadiga excessiva)
    
    Args:
        power_data: Lista de potências por segundo
        duration_s: Duração do teste em segundos
        
    Returns:
        FTP estimado (0.95 * avg_power do teste), ou None se dados insuficientes
    """
    if not power_data or len(power_data) < 300:  # Mínimo 5 minutos de dados
        return None
    
    # Remove os primeiros 3 minutos (warmup) e últimos 3 minutos (fadiga excessiva)
    warmup_s = 180
    cooldown_s = 180
    
    start_idx = min(warmup_s, len(power_data) - 1)
    end_idx = len(power_data) - cooldown_s
    
    # Garante que há pelo menos 60 segundos de dados úteis
    if end_idx - start_idx < 60:
        end_idx = len(power_data)
        start_idx = max(0, end_idx - 600)  # Pega os últimos 10 minutos
    
    effective_power = power_data[start_idx:end_idx]
    
    if not effective_power or len(effective_power) == 0:
        return None
    
    avg_power = np.mean(effective_power)
    
    # Valida resultado
    if avg_power < 0 or avg_power > 5000:  # Limite sanity
        return None
    
    ftp = avg_power * 0.95  # FTP = 95% da média
    
    return ftp


# ==================== Power Zones ====================

def calculate_power_zones(ftp_w: float) -> Dict[str, Dict]:
    """
    Calcula as 7 zonas de ciclismo baseadas em FTP.
    
    Args:
        ftp_w: FTP em watts
        
    Returns:
        Dict com zonas e seus ranges
    """
    # ✅ FIXO: Validar FTP - rejeitar valores impossíveis
    # FTP máximo humano: ~600W (pros), amadores: 150-400W
    # FTP mínimo razoável: 50W
    if ftp_w is None or ftp_w <= 0 or ftp_w < 50 or ftp_w > 800:
        return {}  # Retorna vazio para valores impossíveis
    
    zones = {
        'z1': {
            'name': 'Recuperação',
            'percent_ftp': (0, 55),
            'tss_hour': 55,
            'description': 'Recuperação ativa, pedal leve',
            'color': 'success'
        },
        'z2': {
            'name': 'Endurance',
            'percent_ftp': (56, 75),
            'tss_hour': 75,
            'description': 'Treino aeróbico base',
            'color': 'info'
        },
        'z3': {
            'name': 'Tempo',
            'percent_ftp': (76, 90),
            'tss_hour': 90,
            'description': 'Ritmo moderado-intenso',
            'color': 'warning'
        },
        'z4': {
            'name': 'Limiar',
            'percent_ftp': (91, 105),
            'tss_hour': 100,
            'description': 'Trabalho no FTP',
            'color': 'warning'
        },
        'z5': {
            'name': 'VO2 Max',
            'percent_ftp': (106, 120),
            'tss_hour': 120,
            'description': 'Trabalho intenso acima FTP',
            'color': 'danger'
        },
        'z6': {
            'name': 'Anaeróbico',
            'percent_ftp': (121, 150),
            'tss_hour': 150,
            'description': 'Esforço anaeróbico',
            'color': 'danger'
        },
        'z7': {
            'name': 'Neuromuscular',
            'percent_ftp': (151, 999),
            'tss_hour': 200,
            'description': 'Máxima potência/sprints',
            'color': 'dark'
        }
    }
    
    for zone_key, zone_info in zones.items():
        min_pct, max_pct = zone_info['percent_ftp']
        min_watts = int((min_pct / 100) * ftp_w)
        max_watts = int((max_pct / 100) * ftp_w) if max_pct < 999 else 9999
        
        zone_info['power_range'] = (min_watts, max_watts)
    
    return zones


# ==================== Power Curve ====================

def calculate_peak_powers(power_data: List[float], durations_s: List[int] = None) -> Dict[str, float]:
    """
    Calcula potências máximas para diferentes durações.
    
    Args:
        power_data: Lista de potências por segundo
        durations_s: Lista de durações desejadas (padrão: [5, 60, 300, 1200, 5400])
        
    Returns:
        Dict com potência máxima para cada duração
    """
    if not power_data:
        return {}
    
    if durations_s is None:
        durations_s = [5, 60, 300, 1200, 5400]  # 5s, 1min, 5min, 20min, 90min
    
    peak_powers = {}
    
    for duration in durations_s:
        if duration > len(power_data):
            continue
        
        # Calcula máxima média móvel para essa duração
        max_avg = 0
        for i in range(len(power_data) - duration + 1):
            window = power_data[i:i + duration]
            avg = np.mean(window)
            max_avg = max(max_avg, avg)
        
        duration_str = f"{duration}s"
        if duration >= 60:
            duration_str = f"{duration // 60}m"
        
        peak_powers[duration_str] = max_avg
    
    return peak_powers


def analyze_power_curve(rides: List[Dict]) -> Dict:
    """
    Analisa power curve a partir do histórico de rides.
    
    Args:
        rides: Lista de rides com dados de potência
        
    Returns:
        Dict com power curve por duração
    """
    all_power_data = []
    
    # Consolida todos os dados de potência
    for ride in rides:
        power_list = ride.get('power_data', [])
        if power_list:
            all_power_data.extend(power_list)
    
    if not all_power_data:
        return {}
    
    return calculate_peak_powers(all_power_data)


def interpret_power_curve(peak_powers: Dict, ftp: float) -> Dict[str, str]:
    """
    Interpreta a power curve (tipo de ciclista).
    
    Args:
        peak_powers: Dict com potências pico
        ftp: FTP em watts
        
    Returns:
        Dict com interpretação do perfil
    """
    if not peak_powers:
        return {'profile': 'Dados insuficientes'}
    
    sprint_5s = peak_powers.get('5s', 0)
    anaerobic_1m = peak_powers.get('1m', 0)
    vo2max_5m = peak_powers.get('5m', 0)
    threshold_20m = peak_powers.get('20m', ftp)
    
    # Calcula ratios
    sprint_ftp_ratio = sprint_5s / ftp if ftp > 0 else 0
    anaerobic_ftp_ratio = anaerobic_1m / ftp if ftp > 0 else 0
    vo2max_ftp_ratio = vo2max_5m / ftp if ftp > 0 else 0
    
    # Classifica perfil
    if sprint_ftp_ratio > 2.0 and anaerobic_ftp_ratio > 1.5:
        profile = "Sprinter/Climbista"
        description = "Forte em potência explosiva e subidas"
    elif vo2max_ftp_ratio > 1.3 and threshold_20m >= ftp * 1.05:
        profile = "VO2 Max/Ataque"
        description = "Bom para ataques e esforços de 5-10 min"
    elif threshold_20m > ftp * 0.95:
        profile = "Especialista em Tempo (TT)"
        description = "Forte em esforços sustentados e contra-relógio"
    else:
        profile = "Endurance/Estrada"
        description = "Bom para longas distâncias e base aeróbica"
    
    return {
        'profile': profile,
        'description': description,
        'sprint_to_ftp_ratio': sprint_ftp_ratio,
        'anaerobic_to_ftp_ratio': anaerobic_ftp_ratio,
        'vo2max_to_ftp_ratio': vo2max_ftp_ratio
    }


# ==================== Quadrant Analysis ====================

def quadrant_analysis(power_data: List[float], cadence_data: List[int], 
                      avg_power: float, avg_cadence: int) -> Dict:
    """
    Análise de quadrantes (Force vs Cadence).
    
    Quadrantes:
    - Q1: Alta força, alta cadência (eficiente)
    - Q2: Baixa força, alta cadência (skill based)
    - Q3: Baixa força, baixa cadência (recuperação)
    - Q4: Alta força, baixa cadência (power)
    
    Args:
        power_data: Lista de potências
        cadence_data: Lista de cadências
        avg_power: Potência média
        avg_cadence: Cadência média
        
    Returns:
        Dict com distribuição por quadrante
    """
    if len(power_data) != len(cadence_data) or not power_data:
        return {}
    
    quadrants = {
        'q1': {'name': 'Eficiente', 'count': 0, 'percent': 0, 'color': 'success'},
        'q2': {'name': 'Skill-Based', 'count': 0, 'percent': 0, 'color': 'info'},
        'q3': {'name': 'Recuperação', 'count': 0, 'percent': 0, 'color': 'warning'},
        'q4': {'name': 'Power', 'count': 0, 'percent': 0, 'color': 'danger'}
    }
    
    total = len(power_data)
    
    for power, cadence in zip(power_data, cadence_data):
        high_force = power >= avg_power
        high_cadence = cadence >= avg_cadence
        
        if high_force and high_cadence:
            quadrants['q1']['count'] += 1
        elif not high_force and high_cadence:
            quadrants['q2']['count'] += 1
        elif not high_force and not high_cadence:
            quadrants['q3']['count'] += 1
        else:  # high_force and not high_cadence
            quadrants['q4']['count'] += 1
    
    # Calcula percentuais
    for quad in quadrants.values():
        quad['percent'] = (quad['count'] / total * 100) if total > 0 else 0
    
    return quadrants


def interpret_quadrant_analysis(quadrants: Dict) -> Dict[str, str]:
    """
    Interpreta o padrão de pedal baseado em quadrantes.
    
    Args:
        quadrants: Dict com distribuição
        
    Returns:
        Dict com interpretação
    """
    q1_pct = quadrants.get('q1', {}).get('percent', 0)
    q2_pct = quadrants.get('q2', {}).get('percent', 0)
    q4_pct = quadrants.get('q4', {}).get('percent', 0)
    
    recommendations = []
    
    if q1_pct < 30:
        recommendations.append("Melhorar eficiência - trabalhar cadência em alto esforço")
    
    if q2_pct > 30:
        recommendations.append("Treinar força de perna - trabalho com cadência alta mas força baixa indica técnica")
    
    if q4_pct > 30:
        recommendations.append("Aumentar cadência em esforços de força - evita fadiga muscular")
    
    return {
        'efficiency_score': q1_pct,
        'skill_score': q2_pct,
        'power_score': q4_pct,
        'recommendations': recommendations if recommendations else ['Padrão equilibrado!']
    }


# ==================== Power Distribution ====================

def analyze_power_by_zone(rides: List[Dict], ftp: float) -> Dict:
    """
    Analisa distribuição de treino por zona de potência.
    
    Args:
        rides: Lista de rides
        ftp: FTP em watts
        
    Returns:
        Dict com distribuição por zona
    """
    zones = calculate_power_zones(ftp)
    distribution = {zone: {'count': 0, 'distance_km': 0, 'duration_s': 0, 'tss': 0} 
                   for zone in zones.keys()}
    
    total_distance = 0
    total_duration = 0
    
    for ride in rides:
        distance = ride.get('distance_km', 0)
        duration = ride.get('duration_s', 0)
        avg_power = ride.get('avg_power_w', 0)
        tss = ride.get('tss', 0)
        
        if distance > 0 and duration > 0 and avg_power > 0:
            total_distance += distance
            total_duration += duration
            
            # Identifica zona
            zone_found = False
            for zone_key, zone_info in zones.items():
                min_pct, max_pct = zone_info['percent_ftp']
                min_watts, max_watts = zone_info['power_range']
                
                if min_watts <= avg_power <= max_watts:
                    distribution[zone_key]['count'] += 1
                    distribution[zone_key]['distance_km'] += distance
                    distribution[zone_key]['duration_s'] += duration
                    distribution[zone_key]['tss'] += tss
                    zone_found = True
                    break
            
            # Se não encontrou zona, coloca em Z1
            if not zone_found:
                distribution['z1']['count'] += 1
                distribution['z1']['distance_km'] += distance
                distribution['z1']['duration_s'] += duration
                distribution['z1']['tss'] += tss
    
    # Calcula percentuais
    for zone in distribution.values():
        zone['percent_distance'] = (zone['distance_km'] / total_distance * 100) if total_distance > 0 else 0
        zone['percent_time'] = (zone['duration_s'] / total_duration * 100) if total_duration > 0 else 0
        zone['percent_tss'] = (zone['tss'] / sum(r.get('tss', 0) for r in rides) * 100) \
                             if sum(r.get('tss', 0) for r in rides) > 0 else 0
    
    return distribution


def evaluate_power_distribution(distribution: Dict) -> Dict:
    """
    Avalia se a distribuição segue princípio 80/20.
    
    Ideal para ciclista de estrada/triathlon:
    - 70-80% Z1-Z2 (volume base)
    - 10-15% Z3-Z4 (threshold)
    - 5-10% Z5-Z7 (intensidade)
    
    Args:
        distribution: Distribuição por zona
        
    Returns:
        Dict com avaliação
    """
    z1_z2_pct = distribution.get('z1', {}).get('percent_distance', 0) + \
                distribution.get('z2', {}).get('percent_distance', 0)
    z3_z4_pct = distribution.get('z3', {}).get('percent_distance', 0) + \
                distribution.get('z4', {}).get('percent_distance', 0)
    z5_plus_pct = sum(distribution.get(f'z{i}', {}).get('percent_distance', 0) 
                     for i in range(5, 8))
    
    recommendations = []
    
    if z1_z2_pct < 60:
        recommendations.append(f"Aumentar volume base Z1-Z2 (atual: {z1_z2_pct:.0f}%, alvo: 70-80%)")
    elif z1_z2_pct > 85:
        recommendations.append(f"Adicionar mais trabalho de qualidade")
    
    if z3_z4_pct < 8:
        recommendations.append(f"Aumentar treinos de threshold (Z3-Z4)")
    elif z3_z4_pct > 20:
        recommendations.append(f"Reduzir Z3-Z4, risco de overtraining")
    
    if z5_plus_pct < 3:
        recommendations.append(f"Adicionar 1-2 treinos de alta intensidade por semana")
    elif z5_plus_pct > 12:
        recommendations.append(f"Reduzir Z5+, priorizar recuperação")
    
    is_balanced = 60 <= z1_z2_pct <= 85 and 8 <= z3_z4_pct <= 20 and 3 <= z5_plus_pct <= 12
    
    return {
        'distribution': {
            'z1_z2': z1_z2_pct,
            'z3_z4': z3_z4_pct,
            'z5_plus': z5_plus_pct
        },
        'is_balanced': is_balanced,
        'recommendations': recommendations if recommendations else ['Distribuição equilibrada!']
    }


# ==================== Fatigue Index & Efficiency ====================

def calculate_vi_efficiency(power_data: List[float], duration_s: float) -> Dict[str, float]:
    """
    Calcula Variability Index e eficiência da pedalada.
    
    VI = Normalized Power / Average Power
    Quanto mais próximo de 1.0, mais constante o esforço.
    
    Args:
        power_data: Lista de potências por segundo
        duration_s: Duração total em segundos
        
    Returns:
        Dict com VI e outros índices de eficiência
    """
    if not power_data:
        return {}
    
    avg_power = np.mean(power_data)
    
    # Normalized Power (já calculado em power_pace_analysis)
    # NP = (média de potências elevadas à 4ª potência)^(1/4)
    fourth_powers = [p ** 4 for p in power_data]
    mean_fourth = np.mean(fourth_powers)
    normalized_power = mean_fourth ** 0.25
    
    # Variability Index
    vi = normalized_power / avg_power if avg_power > 0 else 0
    
    # Intensity Factor
    ftp_estimate = avg_power / 0.75  # Assume avg ≈ 75% FTP para ride típico
    intensity_factor = normalized_power / ftp_estimate if ftp_estimate > 0 else 0
    
    # Coefficient of Variation
    std_dev = np.std(power_data)
    cv = (std_dev / avg_power * 100) if avg_power > 0 else 0
    
    return {
        'avg_power': avg_power,
        'normalized_power': normalized_power,
        'variability_index': vi,
        'intensity_factor': intensity_factor,
        'coefficient_variation': cv,
        'power_std_dev': std_dev
    }


def interpret_vi(vi: float) -> Dict[str, str]:
    """
    Interpreta Variability Index.
    
    Args:
        vi: Variability Index (VI)
        
    Returns:
        Dict com interpretação
    """
    if vi <= 1.05:
        return {
            'consistency': 'Muito consistente',
            'color': 'success',
            'description': 'TT/Critério, esforço muito constante',
            'recommendation': 'Excelente pacing'
        }
    elif vi <= 1.10:
        return {
            'consistency': 'Consistente',
            'color': 'info',
            'description': 'Bom controle de ritmo',
            'recommendation': 'Manter padrão'
        }
    elif vi <= 1.15:
        return {
            'consistency': 'Moderadamente variável',
            'color': 'warning',
            'description': 'Variação normal em grupo',
            'recommendation': 'Trabalhar steadiness'
        }
    elif vi <= 1.20:
        return {
            'consistency': 'Variável',
            'color': 'warning',
            'description': 'Muita variação, típico montanha',
            'recommendation': 'Esperado em terreno montanhoso'
        }
    else:
        return {
            'consistency': 'Muito variável',
            'color': 'danger',
            'description': 'Variação excessiva',
            'recommendation': 'Trabalhar pacing e steadiness'
        }


# ==================== Relatório Completo ====================

def generate_power_report(rides: List[Dict], ftp_w: float = None) -> Dict:
    """
    Gera relatório completo de análise de potência.
    
    Args:
        rides: Lista de rides com dados de potência
        ftp_w: FTP em watts (estima se não fornecer)
        
    Returns:
        Dict com relatório completo
    """
    if not ftp_w:
        ftp_w = estimate_ftp_from_workouts(rides) or 250  # FTP padrão de 250W
    
    zones = calculate_power_zones(ftp_w)
    power_curve = analyze_power_curve(rides)
    distribution = analyze_power_by_zone(rides, ftp_w)
    evaluation = evaluate_power_distribution(distribution)
    
    # Consolida dados de potência para VI
    all_power = []
    total_duration = 0
    for ride in rides:
        if ride.get('power_data'):
            all_power.extend(ride['power_data'])
        total_duration += ride.get('duration_s', 0)
    
    vi_analysis = calculate_vi_efficiency(all_power, total_duration) if all_power else {}
    
    # Análise de power curve
    power_curve_interpretation = interpret_power_curve(power_curve, ftp_w)
    
    return {
        'ftp': {
            'watts': ftp_w,
            'description': 'Functional Threshold Power'
        },
        'zones': zones,
        'power_curve': power_curve,
        'power_curve_profile': power_curve_interpretation,
        'efficiency': vi_analysis,
        'distribution': distribution,
        'evaluation': evaluation,
        'generated_at': datetime.now().isoformat()
    }
