"""
Planejador Inteligente de Treinos
==================================

Módulo para sugerir planos de treinamento baseados em ciência do treino.
Implementa periodização, distribuição 80/20, templates de semanas, auto-ajuste CTL/ATL/TSB.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TrainingPhase(Enum):
    """Fases de periodização"""
    BASE = "base"  # Construção de base aeróbica
    BUILD = "build"  # Trabalho de intensidade
    PEAK = "peak"  # Pré-competição
    TAPER = "taper"  # Redução para recuperação
    RECOVERY = "recovery"  # Semana de recuperação ativa


class TrainingModel(Enum):
    """Modelos de distribuição de treino"""
    POLARIZED = "polarized"  # 80% Z1-Z2, 5% Z3-Z4, 15% Z5-Z6
    PYRAMIDAL = "pyramidal"  # 60% Z1-Z2, 30% Z3-Z4, 10% Z5-Z6
    THRESHOLD = "threshold"  # 50% Z1-Z2, 40% Z3-Z4, 10% Z5-Z6


class Modality(Enum):
    """Modalidades de triathlon"""
    SWIM = "swim"
    BIKE = "bike"
    RUN = "run"


# ==================== Template de Semanas ====================

WEEKLY_TEMPLATES = {
    'base_building': {
        'name': 'Base Building Week',
        'phase': TrainingPhase.BASE,
        'description': 'Foco em volume aeróbico, bom para começar ou recuperar',
        'target_tss': {'swim': 80, 'bike': 400, 'run': 200},
        'sessions': [
            {'day': 'Monday', 'modality': 'run', 'type': 'recovery', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Tuesday', 'modality': 'bike', 'type': 'endurance', 'duration_min': 90, 'intensity': 'Z2'},
            {'day': 'Wednesday', 'modality': 'swim', 'type': 'drill_work', 'duration_min': 45, 'intensity': 'Z2'},
            {'day': 'Thursday', 'modality': 'run', 'type': 'endurance', 'duration_min': 60, 'intensity': 'Z2'},
            {'day': 'Friday', 'modality': 'swim', 'type': 'aerobic', 'duration_min': 40, 'intensity': 'Z2'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'long_slow', 'duration_min': 150, 'intensity': 'Z1-Z2'},
            {'day': 'Sunday', 'modality': 'run', 'type': 'long_slow', 'duration_min': 90, 'intensity': 'Z1-Z2'}
        ]
    },
    'build_threshold': {
        'name': 'Build - Threshold Work',
        'phase': TrainingPhase.BUILD,
        'description': 'Aumentar capacidade de threshold (FTP, CSS, LTHR)',
        'target_tss': {'swim': 100, 'bike': 500, 'run': 250},
        'sessions': [
            {'day': 'Monday', 'modality': 'run', 'type': 'recovery', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Tuesday', 'modality': 'bike', 'type': 'threshold', 'duration_min': 90, 'intensity': '4x8min Z4'},
            {'day': 'Wednesday', 'modality': 'swim', 'type': 'threshold', 'duration_min': 60, 'intensity': '3x5min Z4'},
            {'day': 'Thursday', 'modality': 'run', 'type': 'tempo', 'duration_min': 70, 'intensity': '3x8min Z3-Z4'},
            {'day': 'Friday', 'modality': 'swim', 'type': 'aerobic', 'duration_min': 45, 'intensity': 'Z2'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'mixed', 'duration_min': 150, 'intensity': 'Z2 + 2x10min Z4'},
            {'day': 'Sunday', 'modality': 'run', 'type': 'long_slow', 'duration_min': 100, 'intensity': 'Z1-Z2'}
        ]
    },
    'build_vo2max': {
        'name': 'Build - VO2 Max',
        'phase': TrainingPhase.BUILD,
        'description': 'Desenvolvimento de capacidade anaeróbica e VO2 Max',
        'target_tss': {'swim': 110, 'bike': 550, 'run': 280},
        'sessions': [
            {'day': 'Monday', 'modality': 'swim', 'type': 'aerobic', 'duration_min': 45, 'intensity': 'Z2'},
            {'day': 'Tuesday', 'modality': 'run', 'type': 'vo2max', 'duration_min': 80, 'intensity': '5x4min Z5'},
            {'day': 'Wednesday', 'modality': 'bike', 'type': 'vo2max', 'duration_min': 90, 'intensity': '5x4min Z5'},
            {'day': 'Thursday', 'modality': 'swim', 'type': 'threshold', 'duration_min': 60, 'intensity': '4x5min Z4'},
            {'day': 'Friday', 'modality': 'run', 'type': 'recovery', 'duration_min': 40, 'intensity': 'Z1'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'endurance', 'duration_min': 150, 'intensity': 'Z2'},
            {'day': 'Sunday', 'modality': 'run', 'type': 'long_slow', 'duration_min': 100, 'intensity': 'Z1-Z2'}
        ]
    },
    'peak_race_prep': {
        'name': 'Peak - Race Preparation',
        'phase': TrainingPhase.PEAK,
        'description': 'Preparação específica para prova, treino com intensidade de prova',
        'target_tss': {'swim': 120, 'bike': 600, 'run': 300},
        'sessions': [
            {'day': 'Monday', 'modality': 'swim', 'type': 'aerobic', 'duration_min': 40, 'intensity': 'Z2'},
            {'day': 'Tuesday', 'modality': 'bike', 'type': 'brick', 'duration_min': 120, 'intensity': 'Z2 + run Z3'},
            {'day': 'Wednesday', 'modality': 'swim', 'type': 'threshold', 'duration_min': 60, 'intensity': 'Z4'},
            {'day': 'Thursday', 'modality': 'run', 'type': 'tempo', 'duration_min': 80, 'intensity': '2x15min Z3-Z4'},
            {'day': 'Friday', 'modality': 'bike', 'type': 'recovery', 'duration_min': 45, 'intensity': 'Z1'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'long_slow', 'duration_min': 180, 'intensity': 'Z2'},
            {'day': 'Sunday', 'modality': 'run', 'type': 'long_slow', 'duration_min': 120, 'intensity': 'Z1-Z2'}
        ]
    },
    'taper_week': {
        'name': 'Taper Week',
        'phase': TrainingPhase.TAPER,
        'description': 'Redução de volume, mantém alguma intensidade para manter fitness',
        'target_tss': {'swim': 60, 'bike': 250, 'run': 120},
        'sessions': [
            {'day': 'Monday', 'modality': 'run', 'type': 'recovery', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Tuesday', 'modality': 'swim', 'type': 'threshold', 'duration_min': 40, 'intensity': '2x3min Z4'},
            {'day': 'Wednesday', 'modality': 'bike', 'type': 'tempo', 'duration_min': 60, 'intensity': '2x5min Z3'},
            {'day': 'Thursday', 'modality': 'run', 'type': 'recovery', 'duration_min': 35, 'intensity': 'Z1'},
            {'day': 'Friday', 'modality': 'swim', 'type': 'aerobic', 'duration_min': 30, 'intensity': 'Z2'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'recovery', 'duration_min': 45, 'intensity': 'Z1'},
            {'day': 'Sunday', 'modality': 'rest', 'type': 'rest_day', 'duration_min': 0, 'intensity': 'Rest'}
        ]
    },
    'recovery_week': {
        'name': 'Recovery Week',
        'phase': TrainingPhase.RECOVERY,
        'description': 'Semana de recuperação ativa, baixo volume e intensidade',
        'target_tss': {'swim': 50, 'bike': 150, 'run': 80},
        'sessions': [
            {'day': 'Monday', 'modality': 'rest', 'type': 'rest_day', 'duration_min': 0, 'intensity': 'Rest'},
            {'day': 'Tuesday', 'modality': 'swim', 'type': 'easy', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Wednesday', 'modality': 'bike', 'type': 'easy', 'duration_min': 45, 'intensity': 'Z1'},
            {'day': 'Thursday', 'modality': 'run', 'type': 'easy', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Friday', 'modality': 'swim', 'type': 'easy', 'duration_min': 30, 'intensity': 'Z1'},
            {'day': 'Saturday', 'modality': 'bike', 'type': 'easy', 'duration_min': 60, 'intensity': 'Z1'},
            {'day': 'Sunday', 'modality': 'run', 'type': 'easy', 'duration_min': 45, 'intensity': 'Z1'}
        ]
    }
}


# ==================== Planejador Principal ====================

def suggest_training_phase(current_ctl: float, target_ctl: float, 
                          weeks_to_target: int, last_phase: str = None) -> str:
    """
    Sugere fase de treinamento baseada em CTL atual e alvo.
    
    Args:
        current_ctl: CTL atual
        target_ctl: CTL alvo
        weeks_to_target: Semanas disponíveis
        last_phase: Última fase realizada
        
    Returns:
        Fase recomendada (BASE, BUILD, PEAK, TAPER, RECOVERY)
    """
    ctl_deficit = target_ctl - current_ctl
    ctl_percent = current_ctl / target_ctl if target_ctl > 0 else 0
    
    # Lógica de progressão
    if ctl_percent < 0.7:
        return TrainingPhase.BASE.value  # Construir base
    elif ctl_percent < 0.85 and weeks_to_target > 4:
        return TrainingPhase.BUILD.value  # Construir mais antes de peak
    elif ctl_percent < 0.95 and weeks_to_target > 2:
        # Decidir entre BUILD e PEAK
        if last_phase == TrainingPhase.BUILD.value:
            return TrainingPhase.PEAK.value
        else:
            return TrainingPhase.BUILD.value
    elif weeks_to_target > 2:
        return TrainingPhase.PEAK.value  # Próximo de alvo, partir para prova
    elif weeks_to_target == 2:
        return TrainingPhase.TAPER.value  # Uma semana antes de prova
    elif weeks_to_target == 1:
        return TrainingPhase.TAPER.value  # Semana de prova, taper final
    else:
        return TrainingPhase.RECOVERY.value  # Pós-prova


def suggest_training_model(current_ctl: float, phase: str) -> str:
    """
    Sugere modelo de distribuição de treino.
    
    Args:
        current_ctl: CTL atual
        phase: Fase de treinamento
        
    Returns:
        Modelo recomendado (POLARIZED, PYRAMIDAL, THRESHOLD)
    """
    if phase == TrainingPhase.BASE.value:
        return TrainingModel.POLARIZED.value  # Base: 80% Z1-Z2
    elif phase == TrainingPhase.BUILD.value:
        if current_ctl < 50:
            return TrainingModel.PYRAMIDAL.value  # Build inicial: Piramidal
        else:
            return TrainingModel.THRESHOLD.value  # Build avançado: Threshold
    elif phase == TrainingPhase.PEAK.value:
        return TrainingModel.THRESHOLD.value  # Peak: Muito threshold
    else:
        return TrainingModel.POLARIZED.value  # Taper/Recovery: Recuperação ativa


def suggest_weekly_plan(current_ctl: float, target_ctl: float, 
                       weeks_to_target: int, last_phase: str = None) -> Dict:
    """
    Sugere plano semanal completo.
    
    Args:
        current_ctl: CTL atual
        target_ctl: CTL alvo
        weeks_to_target: Semanas até alvo
        last_phase: Última fase (para continuidade)
        
    Returns:
        Dict com sugestão de semana completa
    """
    # Determina fase
    phase = suggest_training_phase(current_ctl, target_ctl, weeks_to_target, last_phase)
    
    # Determina modelo
    model = suggest_training_model(current_ctl, phase)
    
    # Seleciona template apropriado
    template_key = select_template_for_phase(phase, model)
    template = WEEKLY_TEMPLATES[template_key]
    
    # Ajusta intensidade baseado em CTL
    adjusted_template = adjust_template_by_ctl(template, current_ctl, target_ctl)
    
    return {
        'phase': phase,
        'model': model,
        'template_name': template['name'],
        'template_key': template_key,
        'description': template['description'],
        'target_tss': template['target_tss'],
        'sessions': adjusted_template['sessions'],
        'recommendations': generate_phase_recommendations(phase, current_ctl)
    }


def select_template_for_phase(phase: str, model: str) -> str:
    """
    Seleciona template baseado em fase e modelo.
    """
    if phase == TrainingPhase.BASE.value:
        return 'base_building'
    elif phase == TrainingPhase.BUILD.value:
        if model == TrainingModel.POLARIZED.value:
            return 'build_vo2max'  # Mais polarizado = mais VO2Max
        else:
            return 'build_threshold'  # Mais threshold = Threshold work
    elif phase == TrainingPhase.PEAK.value:
        return 'peak_race_prep'
    elif phase == TrainingPhase.TAPER.value:
        return 'taper_week'
    else:  # RECOVERY
        return 'recovery_week'


def adjust_template_by_ctl(template: Dict, current_ctl: float, target_ctl: float) -> Dict:
    """
    Ajusta template baseado em CTL atual.
    
    Args:
        template: Template original
        current_ctl: CTL atual
        target_ctl: CTL alvo
        
    Returns:
        Template ajustado
    """
    ctl_percent = current_ctl / target_ctl if target_ctl > 0 else 0
    
    adjusted = template.copy()
    adjusted['sessions'] = []
    
    for session in template['sessions']:
        session_copy = session.copy()
        
        # Ajusta duração baseado em CTL
        if ctl_percent < 0.7:
            # CTL baixo: reduzir duração
            session_copy['duration_min'] = int(session_copy['duration_min'] * 0.85)
        elif ctl_percent > 0.95:
            # CTL próximo do alvo: aumentar duração
            if session_copy['intensity'] != 'Rest':
                session_copy['duration_min'] = int(session_copy['duration_min'] * 1.1)
        
        adjusted['sessions'].append(session_copy)
    
    return adjusted


def generate_phase_recommendations(phase: str, current_ctl: float) -> List[str]:
    """
    Gera recomendações específicas para a fase.
    """
    recommendations = []
    
    if phase == TrainingPhase.BASE.value:
        recommendations = [
            "Foco em volume consistente",
            "Construir base aeróbica sólida",
            "Possível fazer testes de FTP/CSS/LTHR",
            "Priorizar técnica em todas as modalidades",
            "Dormir bem e comer adequadamente"
        ]
    elif phase == TrainingPhase.BUILD.value:
        recommendations = [
            "Aumentar intensidade gradualmente",
            "1-2 sessões de qualidade por modalidade por semana",
            "Monitorar CTL/ATL para evitar overtraining",
            "Manter dias de recuperação",
            "Trabalhar pontos fracos"
        ]
    elif phase == TrainingPhase.PEAK.value:
        recommendations = [
            "Treinar em intensidade de prova",
            "Brick workouts (bike + run) para aclimatação",
            "Treinar em horário da prova se possível",
            "Teste de nutrição durante treinos",
            "Reduzir volume lentamente"
        ]
    elif phase == TrainingPhase.TAPER.value:
        recommendations = [
            "Reduzir volume em 50-60%",
            "Manter alguma intensidade (ex: 2x5min Z4)",
            "Priorizar sono e recuperação",
            "Não fazer teste de FTP ou treinos novos",
            "Checar equipamento e nutrição"
        ]
    elif phase == TrainingPhase.RECOVERY.value:
        recommendations = [
            "Recuperação ativa (Z1-Z2)",
            "Foco em regeneração",
            "Possível fazer massagem ou stretching",
            "Avaliar treino anterior (o que funcionou?)",
            "Voltar a treinar quando CTL recupera"
        ]
    
    return recommendations


# ==================== Periodização Anual ====================

def generate_annual_plan(event_date: datetime, current_ctl: float, 
                        target_ctl: float) -> Dict:
    """
    Gera plano de periodização anual.
    
    Args:
        event_date: Data da prova alvo
        current_ctl: CTL atual
        target_ctl: CTL alvo
        
    Returns:
        Dict com plano de 52 semanas
    """
    today = datetime.now()
    days_to_event = (event_date - today).days
    weeks_to_event = max(1, days_to_event // 7)
    
    if weeks_to_event < 4:
        return {'error': 'Evento está muito próximo (< 4 semanas)'}
    
    # Aloca semanas para cada fase
    weeks_allocation = allocate_training_weeks(weeks_to_event, target_ctl - current_ctl)
    
    annual_plan = {
        'event_date': event_date.isoformat(),
        'weeks_to_event': weeks_to_event,
        'target_ctl': target_ctl,
        'starting_ctl': current_ctl,
        'phases': weeks_allocation,
        'monthly_breakdown': generate_monthly_breakdown(weeks_allocation, current_ctl, target_ctl)
    }
    
    return annual_plan


def allocate_training_weeks(total_weeks: int, ctl_gain_needed: float) -> Dict[str, int]:
    """
    Aloca semanas para cada fase de treinamento.
    
    Fórmula básica:
    - 20% BASE
    - 50% BUILD
    - 20% PEAK
    - 10% TAPER/RECOVERY (alternando)
    """
    base_weeks = max(4, int(total_weeks * 0.20))
    build_weeks = max(8, int(total_weeks * 0.50))
    peak_weeks = max(3, int(total_weeks * 0.20))
    taper_weeks = total_weeks - base_weeks - build_weeks - peak_weeks
    
    return {
        'base': base_weeks,
        'build': build_weeks,
        'peak': peak_weeks,
        'taper': taper_weeks
    }


def generate_monthly_breakdown(weeks_allocation: Dict, current_ctl: float, 
                              target_ctl: float) -> List[Dict]:
    """
    Gera breakdown mensal com CTL esperado.
    """
    breakdown = []
    cumulative_weeks = 0
    ctl_gain_per_week = (target_ctl - current_ctl) / sum(weeks_allocation.values()) if sum(weeks_allocation.values()) > 0 else 0
    
    phases_ordered = ['base', 'build', 'peak', 'taper']
    
    for phase in phases_ordered:
        weeks = weeks_allocation.get(phase, 0)
        if weeks == 0:
            continue
        
        months_in_phase = weeks / 4.3  # semanas por mês
        expected_ctl = current_ctl + (cumulative_weeks * ctl_gain_per_week)
        
        breakdown.append({
            'phase': phase,
            'weeks': weeks,
            'months': f"{months_in_phase:.1f}",
            'starting_ctl': expected_ctl,
            'ending_ctl': expected_ctl + (weeks * ctl_gain_per_week)
        })
        
        cumulative_weeks += weeks
    
    return breakdown


# ==================== Auto-ajuste ====================

def auto_adjust_plan(current_metrics: Dict, original_plan: Dict) -> Dict:
    """
    Ajusta plano automaticamente baseado no progresso real.
    
    Args:
        current_metrics: {'ctl': float, 'atl': float, 'tsb': float}
        original_plan: Plano original
        
    Returns:
        Plano ajustado com recomendações
    """
    ctl = current_metrics.get('ctl', 0)
    atl = current_metrics.get('atl', 0)
    tsb = current_metrics.get('tsb', 0)
    
    adjustments = []
    
    # Avalia progresso de CTL
    if ctl > original_plan['target_ctl']:
        adjustments.append({
            'type': 'ahead_of_schedule',
            'action': 'CTL atingiu alvo, considere aumentar intensidade',
            'suggestion': 'Passar para próxima fase mais cedo'
        })
    elif ctl < original_plan['starting_ctl']:
        adjustments.append({
            'type': 'behind_schedule',
            'action': 'CTL diminuindo, aumentar consistência',
            'suggestion': 'Adicionar 1-2 sessões por semana'
        })
    
    # Avalia overtraining risk
    if atl > 70 and tsb < -15:
        adjustments.append({
            'type': 'overtraining_risk',
            'action': 'Risco de overtraining detectado',
            'suggestion': 'Fazer semana de recuperação agora'
        })
    
    # Avalia undertraining
    if atl < 40 and tsb > 20:
        adjustments.append({
            'type': 'undertraining',
            'action': 'Treino insuficiente',
            'suggestion': 'Aumentar volume para acelerar CTL'
        })
    
    return {
        'original_plan': original_plan,
        'current_metrics': current_metrics,
        'adjustments': adjustments,
        'recommendation': adjustments[0]['suggestion'] if adjustments else 'Plano no caminho certo'
    }
