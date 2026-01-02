"""
Analisador de Provas de Triathlon
================================

Análise pós-prova de performance, splits, pacing, HR drift, recuperação.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np


# ==================== Análise de Splits ====================

def analyze_race_splits(race_data: Dict) -> Dict:
    """
    Analisa splits da prova (por modalidade e km).
    
    Args:
        race_data: Dict com dados da prova
                  {'swim': {'distance_m': X, 'time_s': Y, 'hr_avg': Z},
                   'bike': {...},
                   'run': {...},
                   'transitions': {'t1': seconds, 't2': seconds}}
        
    Returns:
        Dict com análise de splits
    """
    analysis = {}
    total_time = 0
    
    # Analisa cada modalidade
    for modality, data in race_data.items():
        if modality == 'transitions':
            continue
        
        if data.get('time_s'):
            total_time += data['time_s']
            
            # Pace/velocidade
            if modality == 'swim':
                distance_km = data.get('distance_m', 0) / 1000
                pace_s_100m = (data['time_s'] / (distance_km * 10)) if distance_km > 0 else 0  # Segundos por 100m
                velocity = (data['distance_m'] / data['time_s']) if data['time_s'] > 0 else 0
                
                analysis[modality] = {
                    'distance_m': data.get('distance_m', 0),
                    'time_s': data['time_s'],
                    'time_formatted': format_time_seconds(data['time_s']),
                    'pace_100m_s': pace_s_100m,
                    'pace_100m_formatted': format_pace_seconds_to_mm_ss(pace_s_100m),
                    'velocity_ms': velocity,
                    'hr_avg': data.get('hr_avg', 0),
                    'hr_max': data.get('hr_max', 0),
                    'intensity_pct': (data.get('hr_avg', 0) / data.get('lthr', 150) * 100) if data.get('lthr') else 0
                }
            
            elif modality == 'bike':
                distance_km = data.get('distance_km', 0)
                velocity_kmh = (distance_km / data['time_s'] * 3600) if data['time_s'] > 0 else 0
                avg_power = data.get('avg_power_w', 0)
                
                analysis[modality] = {
                    'distance_km': distance_km,
                    'time_s': data['time_s'],
                    'time_formatted': format_time_seconds(data['time_s']),
                    'velocity_kmh': velocity_kmh,
                    'elevation_m': data.get('elevation_gain', 0),
                    'avg_power_w': avg_power,
                    'intensity_factor': (avg_power / data.get('ftp', 250)) if data.get('ftp') else 0,
                    'hr_avg': data.get('hr_avg', 0),
                    'hr_max': data.get('hr_max', 0),
                    'cadence_rpm': data.get('cadence_rpm', 0)
                }
            
            elif modality == 'run':
                distance_km = data.get('distance_km', 0)
                pace_s_km = (data['time_s'] / distance_km) if distance_km > 0 else 0  # Segundos por km
                velocity_kmh = (distance_km / data['time_s'] * 3600) if data['time_s'] > 0 else 0
                
                analysis[modality] = {
                    'distance_km': distance_km,
                    'time_s': data['time_s'],
                    'time_formatted': format_time_seconds(data['time_s']),
                    'pace_s_km': pace_s_km,
                    'pace_formatted': format_pace_seconds_to_mm_ss(pace_s_km),
                    'velocity_kmh': velocity_kmh,
                    'elevation_m': data.get('elevation_gain', 0),
                    'hr_avg': data.get('hr_avg', 0),
                    'hr_max': data.get('hr_max', 0),
                    'cadence_spm': data.get('cadence_rpm', 0)
                }
    
    # Analisa transições
    t1_time = race_data.get('transitions', {}).get('t1', 0)
    t2_time = race_data.get('transitions', {}).get('t2', 0)
    total_time += t1_time + t2_time
    
    analysis['transitions'] = {
        't1': format_time_seconds(t1_time),
        't2': format_time_seconds(t2_time),
        'total': format_time_seconds(t1_time + t2_time)
    }
    
    analysis['total_time'] = format_time_seconds(total_time)
    analysis['total_time_s'] = total_time
    
    return analysis


def format_time_seconds(seconds: float) -> str:
    """
    Formata segundos para HH:MM:SS.
    
    Padrão: Sempre retorna HH:MM:SS (com 00:MM:SS se < 1 hora)
    
    Args:
        seconds: Tempo em segundos
        
    Returns:
        String formatada como HH:MM:SS
    """
    # ✅ FIXO: Validar None antes de comparar
    if seconds is None or seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_pace_seconds_to_mm_ss(seconds: float) -> str:
    """
    Formata segundos como pace em MM:SS.
    
    Para paces (tempo por km, 100m, etc).
    Padrão: MM:SS
    
    Args:
        seconds: Tempo em segundos
        
    Returns:
        String formatada como MM:SS
    """
    # ✅ FIXO: Testar None ANTES de comparar com número
    if seconds is None or seconds < 0:
        return "00:00"
    
    try:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes > 99:
            minutes = 99
            secs = 59
        
        return f"{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError):
        return "00:00"


# ==================== Análise de Pacing ====================

def analyze_pacing_strategy(splits_by_km: List[Dict]) -> Dict:
    """
    Analisa estratégia de pacing durante a prova.
    
    Tipos:
    - Even pacing: ritmo constante
    - Negative split: acelerando
    - Positive split: desacelerando
    - Uneven: muito variável
    
    Args:
        splits_by_km: Lista com splits por km
                     [{'km': X, 'time_s': Y, 'pace': Z}, ...]
        
    Returns:
        Dict com análise de pacing
    """
    if not splits_by_km or len(splits_by_km) < 3:
        return {'status': 'Dados insuficientes para análise de pacing'}
    
    paces = [s.get('pace', 0) for s in splits_by_km]
    
    # Divide em 3 partes (início, meio, fim)
    third = len(paces) // 3
    
    if third == 0:
        first_third = paces
        second_third = []
        last_third = []
    else:
        first_third = paces[:third]
        second_third = paces[third:2*third]
        last_third = paces[2*third:]
    
    pace_start = np.mean(first_third) if first_third else 0
    pace_mid = np.mean(second_third) if second_third else 0
    pace_end = np.mean(last_third) if last_third else 0
    
    overall_mean = np.mean(paces)
    overall_std = np.std(paces)
    cv = (overall_std / overall_mean * 100) if overall_mean > 0 else 0
    
    # Classifica estratégia baseado em CV (Coefficient of Variation)
    if cv < 5:
        strategy = 'Muito consistente (excelente pacing)'
        strategy_type = 'even'
    elif cv < 10:
        strategy = 'Consistente'
        strategy_type = 'even'
    else:
        strategy = 'Variável'
        strategy_type = 'uneven'
    
    # Detecta negative/positive split
    if pace_start > 0 and pace_end > 0:
        split_diff = ((pace_start - pace_end) / pace_start * 100)
        if split_diff < -5:  # Acelerou no final
            strategy = 'Negative split (acelerou no final)'
            strategy_type = 'negative'
        elif split_diff > 5:  # Desacelerou no final
            strategy = 'Positive split (desacelerou no final)'
            strategy_type = 'positive'
    
    return {
        'strategy': strategy,
        'strategy_type': strategy_type,
        'pace_start_s': pace_start,
        'pace_start_formatted': format_pace_seconds_to_mm_ss(pace_start),
        'pace_mid_s': pace_mid,
        'pace_mid_formatted': format_pace_seconds_to_mm_ss(pace_mid),
        'pace_end_s': pace_end,
        'pace_end_formatted': format_pace_seconds_to_mm_ss(pace_end),
        'overall_mean_s': overall_mean,
        'overall_mean_formatted': format_pace_seconds_to_mm_ss(overall_mean),
        'consistency_cv': cv,
        'recommendation': get_pacing_recommendation(strategy_type, cv)
    }


def get_pacing_recommendation(strategy_type: str, consistency_cv: float) -> str:
    """Recomendação baseada em pacing."""
    if strategy_type == 'positive' and consistency_cv > 15:
        return 'Trabalhar início mais conservador e pacing consistente'
    elif strategy_type == 'positive':
        return 'Começar um pouco mais rápido para evitar desaceleração'
    elif strategy_type == 'negative':
        return 'Excelente pacing! Conseguiu acelerar no final'
    elif consistency_cv < 5:
        return 'Pacing perfeito! Manter essa estratégia'
    else:
        return 'Trabalhar consistência de ritmo'


# ==================== Heart Rate Drift ====================

def analyze_hr_drift(hr_data: List[float], duration_s: float, modality: str) -> Dict:
    """
    Analisa drift de frequência cardíaca (aumento de HR em intensidade constante).
    
    Indica fadiga cardiovascular e falta de fitness relativo.
    
    Args:
        hr_data: Lista de HR por segundo
        duration_s: Duração total em segundos
        modality: 'swim', 'bike', ou 'run'
        
    Returns:
        Dict com análise
    """
    if not hr_data or len(hr_data) < 60:
        return {}
    
    # Divide em primeira e segunda metade
    mid_point = len(hr_data) // 2
    first_half = hr_data[:mid_point]
    second_half = hr_data[mid_point:]
    
    hr_first = np.mean(first_half)
    hr_second = np.mean(second_half)
    
    drift_bpm = hr_second - hr_first
    drift_percent = (drift_bpm / hr_first * 100) if hr_first > 0 else 0
    
    # Avalia
    if drift_percent < 2:
        interpretation = 'Excelente estabilidade cardiovascular'
        rating = 'Excelente'
    elif drift_percent < 5:
        interpretation = 'Boa estabilidade, um pouco de fadiga'
        rating = 'Bom'
    elif drift_percent < 10:
        interpretation = 'Drift moderado, indica fadiga'
        rating = 'Moderado'
    else:
        interpretation = 'Drift elevado, fitness baixo para intensidade'
        rating = 'Pobre'
    
    return {
        'hr_first_half': int(hr_first),
        'hr_second_half': int(hr_second),
        'drift_bpm': int(drift_bpm),
        'drift_percent': drift_percent,
        'interpretation': interpretation,
        'rating': rating,
        'recommendation': 'Aumentar fitness cardiovascular com treinos Z2 aeróbicos' if drift_percent > 5 else 'Continuar com treino atual'
    }


# ==================== Pós-Prova ====================

def analyze_recovery_progress(race_date: datetime, metrics_timeline: List[Dict]) -> Dict:
    """
    Analisa recuperação após prova.
    
    Args:
        race_date: Data da prova
        metrics_timeline: Timeline de CTL/ATL/TSB/HRV após prova
        
    Returns:
        Dict com análise de recuperação
    """
    if not metrics_timeline:
        return {}
    
    # Identifica ponto mais baixo (CTL mais baixo = maior queda)
    ctl_values = [m.get('ctl', 0) for m in metrics_timeline]
    lowest_ctl = min(ctl_values) if ctl_values else 0
    days_to_lowest = ctl_values.index(lowest_ctl) if lowest_ctl in ctl_values else 0
    
    # Recuperação de CTL
    ctl_recovery = ctl_values[-1] - lowest_ctl if ctl_values else 0
    
    # Avalia
    analysis = {
        'days_since_race': len(metrics_timeline),
        'lowest_ctl': lowest_ctl,
        'days_to_lowest': days_to_lowest,
        'ctl_recovery': ctl_recovery,
        'current_ctl': ctl_values[-1] if ctl_values else 0
    }
    
    # Valida se recuperação está no caminho certo
    if len(metrics_timeline) >= 7:
        week_ctl = ctl_values[-7]
        current_ctl = ctl_values[-1]
        ctl_gain = current_ctl - week_ctl
        
        expected_gain = 5  # ~5 CTL por semana em recuperação ativa
        
        if ctl_gain < expected_gain / 2:
            analysis['status'] = 'Recuperação lenta'
            analysis['recommendation'] = 'Aumentar volume de treino'
        elif ctl_gain > expected_gain * 1.5:
            analysis['status'] = 'Recuperação rápida'
            analysis['recommendation'] = 'Bom progresso, continuar'
        else:
            analysis['status'] = 'Recuperação normal'
            analysis['recommendation'] = 'Progresso conforme esperado'
    
    return analysis


# ==================== Comparação com Treinos ====================

def compare_race_with_training(race_data: Dict, training_data: List[Dict]) -> Dict:
    """
    Compara performance da prova com treinos similares.
    
    Args:
        race_data: Dados da prova (com splits, HR, power)
        training_data: Histórico de treinos similares
        
    Returns:
        Dict com comparação
    """
    comparison = {}
    
    # Para cada modalidade, compara
    for modality in ['swim', 'bike', 'run']:
        if modality not in race_data:
            continue
        
        race_metric = race_data[modality]
        
        # Filtra treinos similares
        similar_training = [t for t in training_data 
                           if t.get('type') == modality and 
                           abs(t.get('duration_s', 0) - race_metric.get('time_s', 0)) < 600]  # +/- 10 min
        
        if not similar_training:
            comparison[modality] = {'status': 'Sem treinos similares para comparação'}
            continue
        
        # Calcula média de treinos similares
        avg_hr = np.mean([t.get('hr_avg', 0) for t in similar_training])
        
        race_hr = race_metric.get('hr_avg', 0)
        hr_diff = race_hr - avg_hr
        
        comparison[modality] = {
            'race_hr_avg': int(race_hr),
            'training_hr_avg': int(avg_hr),
            'hr_diff': int(hr_diff),
            'interpretation': get_hr_comparison_interpretation(hr_diff, avg_hr)
        }
    
    return comparison


def get_hr_comparison_interpretation(hr_diff: float, training_avg: float) -> str:
    """Interpreta diferença de HR."""
    if hr_diff < -10:
        return 'HR mais baixo que treinos - melhor condição'
    elif hr_diff < 5:
        return 'HR similar aos treinos - performance consistente'
    elif hr_diff < 15:
        return 'HR um pouco elevado - efeito da prova'
    else:
        return 'HR muito elevado - indicador de esforço supramáximo'


# ==================== Relatório Completo de Prova ====================

def generate_race_report(race_data: Dict, training_data: List[Dict] = None, 
                        metrics_timeline: List[Dict] = None) -> Dict:
    """
    Gera relatório completo da prova.
    
    Args:
        race_data: Dados da prova
        training_data: Histórico de treinos para comparação
        metrics_timeline: Timeline pós-prova para análise de recuperação
        
    Returns:
        Dict com relatório completo
    """
    report = {
        'race_date': race_data.get('date', datetime.now().isoformat()),
        'race_type': race_data.get('race_type', 'Triathlon'),
        'generated_at': datetime.now().isoformat()
    }
    
    # Análise de splits
    splits_analysis = analyze_race_splits(race_data)
    report['splits'] = splits_analysis
    
    # Análise de pacing (se houver dados de km splits)
    if race_data.get('km_splits'):
        pacing_analysis = analyze_pacing_strategy(race_data['km_splits'])
        report['pacing'] = pacing_analysis
    
    # Análise de HR drift (por modalidade)
    report['hr_drift'] = {}
    for modality in ['swim', 'bike', 'run']:
        if modality in race_data and race_data[modality].get('hr_data'):
            drift = analyze_hr_drift(
                race_data[modality]['hr_data'],
                race_data[modality].get('time_s', 0),
                modality
            )
            if drift:
                report['hr_drift'][modality] = drift
    
    # Comparação com treinos
    if training_data:
        comparison = compare_race_with_training(race_data, training_data)
        report['comparison_with_training'] = comparison
    
    # Análise de recuperação
    if metrics_timeline:
        recovery = analyze_recovery_progress(race_data.get('date'), metrics_timeline)
        report['recovery'] = recovery
    
    return report


# ==================== Checklist de Prova ====================

def create_race_checklist(race_type: str, race_date: datetime, 
                         days_to_race: int) -> Dict:
    """
    Cria checklist de preparação para prova.
    
    Args:
        race_type: Tipo de prova ('sprint', 'olympic', 'half', 'ironman')
        race_date: Data da prova
        days_to_race: Dias faltando
        
    Returns:
        Dict com checklist categorizado
    """
    checklist = {
        'race_info': {
            'race_type': race_type,
            'race_date': race_date.isoformat(),
            'days_to_race': days_to_race
        },
        'training': [],
        'nutrition': [],
        'equipment': [],
        'logistics': []
    }
    
    if days_to_race > 14:
        checklist['training'].extend([
            {'item': 'Brick workouts regulares', 'priority': 'high'},
            {'item': 'Treinos em zona de prova', 'priority': 'high'},
            {'item': 'Teste de equipamento', 'priority': 'medium'}
        ])
    elif days_to_race > 7:
        checklist['training'].extend([
            {'item': 'Reduzir volume gradualmente', 'priority': 'high'},
            {'item': 'Manter 1-2 sessões de qualidade', 'priority': 'high'},
            {'item': 'Descanso extra (1h+ por dia)', 'priority': 'high'}
        ])
    else:
        checklist['training'].extend([
            {'item': 'Semana de taper completa', 'priority': 'high'},
            {'item': 'Dia antes: treino muito leve', 'priority': 'high'},
            {'item': 'Dia da prova: aquecimento leve', 'priority': 'high'}
        ])
    
    # Nutrição
    checklist['nutrition'].extend([
        {'item': 'Carbo-loading (se > 2h prova)', 'priority': 'high'},
        {'item': 'Testar nutrição durante treinos', 'priority': 'high'},
        {'item': 'Hidratação e eletrólitos', 'priority': 'high'},
        {'item': 'Café da manhã tido testado', 'priority': 'medium'}
    ])
    
    # Equipamento
    checklist['equipment'].extend([
        {'item': 'Wetsuit (se aplicável)', 'priority': 'high'},
        {'item': 'Bike afinada e testada', 'priority': 'high'},
        {'item': 'Capacete com furação (aerodinâmica)', 'priority': 'high'},
        {'item': 'Sapatos afinados', 'priority': 'high'},
        {'item': 'Óculos (natação + ciclismo)', 'priority': 'high'},
        {'item': 'Luvas e kit emergência', 'priority': 'medium'}
    ])
    
    # Logística
    checklist['logistics'].extend([
        {'item': 'Rota para venue e chegada', 'priority': 'high'},
        {'item': 'Estacionamento', 'priority': 'medium'},
        {'item': 'Registro e busca de número', 'priority': 'high'},
        {'item': 'Reconhecimento do percurso', 'priority': 'medium'},
        {'item': 'Dormir bem noite anterior', 'priority': 'high'}
    ])
    
    return checklist
