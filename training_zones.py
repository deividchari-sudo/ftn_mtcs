"""
Módulo de Zonas de Treinamento para Triathlon
Implementa zonas específicas para natação, ciclismo e corrida
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

# =============================================================================
# CONSTANTES DE ZONAS DE TREINAMENTO
# =============================================================================

SWIMMING_ZONES = {
    'z1': {
        'name': 'Recovery',
        'css_percent': (0, 80),
        'tss_per_hour': 55,
        'description': 'Recuperação ativa, técnica',
        'color': '#90EE90'
    },
    'z2': {
        'name': 'Endurance',
        'css_percent': (81, 88),
        'tss_per_hour': 75,
        'description': 'Aeróbico base, volume',
        'color': '#87CEEB'
    },
    'z3': {
        'name': 'Tempo',
        'css_percent': (89, 95),
        'tss_per_hour': 90,
        'description': 'Ritmo controlado, steady state',
        'color': '#FFA500'
    },
    'z4': {
        'name': 'Threshold',
        'css_percent': (96, 102),
        'tss_per_hour': 100,
        'description': 'Limiar anaeróbico, CSS',
        'color': '#FF6347'
    },
    'z5': {
        'name': 'VO2Max',
        'css_percent': (103, 110),
        'tss_per_hour': 120,
        'description': 'Máxima potência aeróbica',
        'color': '#DC143C'
    }
}

CYCLING_ZONES = {
    'z1': {
        'name': 'Recovery',
        'ftp_percent': (0, 55),
        'tss_per_hour': 55,
        'description': 'Recuperação ativa, spin fácil',
        'color': '#90EE90'
    },
    'z2': {
        'name': 'Endurance',
        'ftp_percent': (56, 75),
        'tss_per_hour': 75,
        'description': 'Aeróbico base, long rides',
        'color': '#87CEEB'
    },
    'z3': {
        'name': 'Tempo',
        'ftp_percent': (76, 90),
        'tss_per_hour': 90,
        'description': 'Tempo sustentado, sweetspot',
        'color': '#FFA500'
    },
    'z4': {
        'name': 'Threshold',
        'ftp_percent': (91, 105),
        'tss_per_hour': 100,
        'description': 'FTP, lactate threshold',
        'color': '#FF6347'
    },
    'z5': {
        'name': 'VO2Max',
        'ftp_percent': (106, 120),
        'tss_per_hour': 120,
        'description': 'Intervalos curtos, alta intensidade',
        'color': '#DC143C'
    },
    'z6': {
        'name': 'Anaerobic',
        'ftp_percent': (121, 150),
        'tss_per_hour': 140,
        'description': 'Esforços anaeróbicos, sprints',
        'color': '#8B0000'
    }
}

RUNNING_ZONES = {
    'z1': {
        'name': 'Recovery',
        'lthr_percent': (0, 81),
        'pace_percent': (140, 999),  # % do threshold pace (mais lento)
        'tss_per_hour': 55,
        'description': 'Recuperação ativa, corrida leve',
        'color': '#90EE90'
    },
    'z2': {
        'name': 'Endurance',
        'lthr_percent': (82, 89),
        'pace_percent': (115, 140),
        'tss_per_hour': 75,
        'description': 'Aeróbico base, long runs',
        'color': '#87CEEB'
    },
    'z3': {
        'name': 'Tempo',
        'lthr_percent': (90, 94),
        'pace_percent': (105, 115),
        'tss_per_hour': 90,
        'description': 'Ritmo de maratona, comfortably hard',
        'color': '#FFA500'
    },
    'z4': {
        'name': 'Threshold',
        'lthr_percent': (95, 99),
        'pace_percent': (98, 105),
        'tss_per_hour': 100,
        'description': 'Limiar anaeróbico, ritmo de meia',
        'color': '#FF6347'
    },
    'z5': {
        'name': 'VO2Max',
        'lthr_percent': (100, 105),
        'pace_percent': (90, 98),
        'tss_per_hour': 120,
        'description': '3km-5km pace, intervalos',
        'color': '#DC143C'
    },
    'z6': {
        'name': 'Anaerobic',
        'lthr_percent': (106, 110),
        'pace_percent': (0, 90),
        'tss_per_hour': 140,
        'description': 'Sprints, velocidade máxima',
        'color': '#8B0000'
    }
}

# =============================================================================
# FUNÇÕES DE CÁLCULO DE ZONAS
# =============================================================================

def calculate_swim_zones(css: float) -> Dict[str, Dict]:
    """
    Calcula zonas de natação baseadas no CSS (Critical Swim Speed)
    
    Args:
        css: Critical Swim Speed em segundos por 100m
        
    Returns:
        Dict com zonas e seus paces correspondentes
    """
    if css <= 0:
        return {}
    
    zones = {}
    for zone_id, zone_info in SWIMMING_ZONES.items():
        min_percent, max_percent = zone_info['css_percent']
        
        # CSS menor = mais rápido, então invertemos a lógica
        # Zona 1 (recovery) = pace MAIS LENTO (120% do CSS)
        # Zona 5 (VO2) = pace MAIS RÁPIDO (95% do CSS)
        max_pace = css * (max_percent / 100)  # Pace mais lento
        min_pace = css * (min_percent / 100) if min_percent > 0 else 0  # Pace mais rápido
        
        zones[zone_id] = {
            **zone_info,
            'pace_range': (min_pace, max_pace),
            'pace_display': f"{format_swim_pace(min_pace)} - {format_swim_pace(max_pace)}"
        }
    
    return zones


def calculate_bike_zones(ftp: float) -> Dict[str, Dict]:
    """
    Calcula zonas de ciclismo baseadas no FTP (Functional Threshold Power)
    
    Args:
        ftp: FTP em watts
        
    Returns:
        Dict com zonas e suas potências correspondentes
    """
    if ftp <= 0:
        return {}
    
    zones = {}
    for zone_id, zone_info in CYCLING_ZONES.items():
        min_percent, max_percent = zone_info['ftp_percent']
        
        min_power = int(ftp * (min_percent / 100))
        max_power = int(ftp * (max_percent / 100))
        
        zones[zone_id] = {
            **zone_info,
            'power_range': (min_power, max_power),
            'power_display': f"{min_power} - {max_power}W"
        }
    
    return zones


def calculate_run_zones(lthr: int, threshold_pace: Optional[float] = None) -> Dict[str, Dict]:
    """
    Calcula zonas de corrida baseadas no LTHR e/ou threshold pace
    
    Args:
        lthr: Lactate Threshold Heart Rate (bpm)
        threshold_pace: Pace threshold em minutos por km (opcional)
        
    Returns:
        Dict com zonas e seus HR/pace correspondentes
    """
    if lthr <= 0:
        return {}
    
    zones = {}
    for zone_id, zone_info in RUNNING_ZONES.items():
        min_hr_percent, max_hr_percent = zone_info['lthr_percent']
        
        min_hr = int(lthr * (min_hr_percent / 100))
        max_hr = int(lthr * (max_hr_percent / 100))
        
        zone_data = {
            **zone_info,
            'hr_range': (min_hr, max_hr),
            'hr_display': f"{min_hr} - {max_hr} bpm"
        }
        
        # Adicionar pace zones se threshold_pace fornecido
        if threshold_pace and threshold_pace > 0:
            min_pace_percent, max_pace_percent = zone_info['pace_percent']
            
            # Pace maior = mais lento
            if max_pace_percent < 999:
                max_pace = threshold_pace * (max_pace_percent / 100)
            else:
                max_pace = 999  # Sem limite superior para Z1
                
            min_pace = threshold_pace * (min_pace_percent / 100) if min_pace_percent > 0 else 0
            
            zone_data['pace_range'] = (min_pace, max_pace)
            zone_data['pace_display'] = format_run_pace_range(min_pace, max_pace)
        
        zones[zone_id] = zone_data
    
    return zones


# =============================================================================
# ANÁLISE DE TEMPO EM ZONAS
# =============================================================================

def analyze_time_in_zones(workout: Dict, zones: Dict[str, Dict], modality: str) -> Dict[str, float]:
    """
    Analisa tempo gasto em cada zona de treinamento
    
    Args:
        workout: Workout data com HR ou power
        zones: Zonas calculadas
        modality: 'swimming', 'cycling', 'running'
        
    Returns:
        Dict com tempo (minutos) em cada zona
    """
    time_in_zones = {zone_id: 0.0 for zone_id in zones.keys()}
    
    # Placeholder - em produção, analisaria dados granulares (HR stream, power stream)
    # Por enquanto, estimamos baseado em avg HR ou avg power
    
    duration_minutes = float(workout.get('duration', 0) or 0) / 60
    
    if modality == 'cycling' and 'averagePower' in workout:
        avg_power = float(workout.get('averagePower', 0) or 0)
        for zone_id, zone_info in zones.items():
            min_power, max_power = zone_info['power_range']
            if min_power <= avg_power <= max_power:
                time_in_zones[zone_id] = duration_minutes
                break
    
    elif modality in ['running', 'swimming'] and 'averageHR' in workout:
        avg_hr = float(workout.get('averageHR', 0) or 0)
        for zone_id, zone_info in zones.items():
            if 'hr_range' in zone_info:
                min_hr, max_hr = zone_info['hr_range']
                if min_hr <= avg_hr <= max_hr:
                    time_in_zones[zone_id] = duration_minutes
                    break
    
    return time_in_zones


def calculate_zone_distribution(workouts: List[Dict], zones: Dict[str, Dict], modality: str) -> Dict:
    """
    Calcula distribuição de tempo total em zonas para múltiplos treinos
    
    Args:
        workouts: Lista de workouts
        zones: Zonas de treinamento
        modality: Modalidade
        
    Returns:
        Dict com estatísticas de distribuição
    """
    total_time_in_zones = {zone_id: 0.0 for zone_id in zones.keys()}
    
    for workout in workouts:
        workout_zones = analyze_time_in_zones(workout, zones, modality)
        for zone_id, time in workout_zones.items():
            total_time_in_zones[zone_id] += time
    
    total_time = sum(total_time_in_zones.values())
    
    distribution = {}
    for zone_id, time in total_time_in_zones.items():
        percentage = (time / total_time * 100) if total_time > 0 else 0
        distribution[zone_id] = {
            'time_minutes': time,
            'percentage': percentage,
            'zone_name': zones[zone_id]['name'],
            'color': zones[zone_id]['color']
        }
    
    return distribution


def evaluate_zone_distribution_quality(distribution: Dict, model: str = 'polarized') -> Dict:
    """
    Avalia qualidade da distribuição de zonas baseado em modelo de treinamento
    
    Args:
        distribution: Distribuição atual de zonas
        model: 'polarized', 'pyramidal', 'threshold'
        
    Returns:
        Dict com avaliação e recomendações
    """
    z1_z2_percent = distribution.get('z1', {}).get('percentage', 0) + distribution.get('z2', {}).get('percentage', 0)
    z3_percent = distribution.get('z3', {}).get('percentage', 0)
    z4_z5_percent = distribution.get('z4', {}).get('percentage', 0) + distribution.get('z5', {}).get('percentage', 0)
    
    recommendations = []
    quality_score = 0
    
    if model == 'polarized':
        # Modelo Polarizado: 75-80% Z1-Z2, 5-10% Z3, 15-20% Z4-Z5
        target_low = 75
        target_mid = 10
        target_high = 15
        
        if 70 <= z1_z2_percent <= 85:
            quality_score += 40
        else:
            recommendations.append(f"Ajustar volume Z1-Z2 para 75-80% (atual: {z1_z2_percent:.1f}%)")
        
        if z3_percent <= 15:
            quality_score += 30
        else:
            recommendations.append(f"Reduzir tempo em Z3 para <10% (atual: {z3_percent:.1f}%)")
        
        if 10 <= z4_z5_percent <= 25:
            quality_score += 30
        else:
            recommendations.append(f"Ajustar Z4-Z5 para 15-20% (atual: {z4_z5_percent:.1f}%)")
    
    elif model == 'pyramidal':
        # Modelo Piramidal: 70-75% Z1-Z2, 15-20% Z3, 10-15% Z4-Z5
        if 65 <= z1_z2_percent <= 80:
            quality_score += 40
        if 10 <= z3_percent <= 25:
            quality_score += 30
        if 5 <= z4_z5_percent <= 20:
            quality_score += 30
    
    elif model == 'threshold':
        # Modelo Threshold: 60-65% Z1-Z2, 25-30% Z3, 10-15% Z4-Z5
        if 55 <= z1_z2_percent <= 70:
            quality_score += 40
        if 20 <= z3_percent <= 35:
            quality_score += 30
        if 5 <= z4_z5_percent <= 20:
            quality_score += 30
    
    return {
        'model': model,
        'quality_score': quality_score,
        'quality_label': 'Excelente' if quality_score >= 80 else 'Bom' if quality_score >= 60 else 'Regular' if quality_score >= 40 else 'Precisa Ajustar',
        'recommendations': recommendations,
        'current_distribution': {
            'low_intensity': z1_z2_percent,
            'moderate_intensity': z3_percent,
            'high_intensity': z4_z5_percent
        }
    }


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def format_swim_pace(seconds_per_100m: float) -> str:
    """Formata pace de natação em mm:ss/100m"""
    if seconds_per_100m <= 0 or seconds_per_100m > 999:
        return "N/A"
    
    minutes = int(seconds_per_100m // 60)
    seconds = int(seconds_per_100m % 60)
    return f"{minutes:01d}:{seconds:02d}/100m"


def format_run_pace_range(min_pace: float, max_pace: float) -> str:
    """Formata range de pace de corrida em mm:ss/km"""
    if max_pace >= 999:
        return f"{format_run_pace(min_pace)}+"
    return f"{format_run_pace(min_pace)} - {format_run_pace(max_pace)}"


def format_run_pace(minutes_per_km: float) -> str:
    """Formata pace de corrida em mm:ss/km"""
    if minutes_per_km <= 0:
        return "N/A"
    
    minutes = int(minutes_per_km)
    seconds = int((minutes_per_km - minutes) * 60)
    return f"{minutes:01d}:{seconds:02d}/km"
