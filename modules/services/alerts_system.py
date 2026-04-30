"""
Sistema de Alertas Inteligentes
===============================

Detecta e notifica sobre situações importantes no treinamento.
Alertas de overtraining, detraining, janelas ótimas de performance, desequilíbrio.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class AlertSeverity(Enum):
    """Níveis de gravidade de alerta"""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


class AlertCategory(Enum):
    """Categorias de alertas"""
    OVERTRAINING = "overtraining"
    DETRAINING = "detraining"
    RECOVERY_WINDOW = "recovery_window"
    PERFORMANCE_WINDOW = "performance_window"
    MODALITY_IMBALANCE = "modality_imbalance"
    HRV_DECLINE = "hrv_decline"
    SLEEP_QUALITY = "sleep_quality"
    INJURY_RISK = "injury_risk"


# ==================== Alertas por Categoria ====================

def check_overtraining_risk(ctl: float, atl: float, tsb: float, 
                           history: List[Dict] = None) -> Optional[Dict]:
    """
    Detecta risco de overtraining (overreaching).
    
    Sinais:
    - ATL > 70 e TSB < -20 por 3+ dias
    - CTL aumentando muito rápido (>10 por semana)
    - TSB consistentemente negativo
    
    Args:
        ctl: Chronic Training Load
        atl: Acute Training Load
        tsb: Training Stress Balance
        history: Histórico dos últimos 30 dias (lista de dicts com ctl, atl, tsb)
        
    Returns:
        Dict com alerta ou None
    """
    alert = None
    
    if atl > 70 and tsb < -20:
        alert = {
            'category': AlertCategory.OVERTRAINING.value,
            'severity': AlertSeverity.DANGER.value,
            'title': '⚠️ Risco de Overtraining',
            'message': f'ATL muito alta ({atl:.0f}) e TSB negativo ({tsb:.0f}). Cansaço acumulado!',
            'action': 'Reduzir volume em 40-50% esta semana. Priorizar sono e recuperação.',
            'duration_days': 7
        }
    elif atl > 60 and tsb < -15:
        alert = {
            'category': AlertCategory.OVERTRAINING.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '⚠️ Possível Overtraining',
            'message': f'Carga aguda elevada ({atl:.0f}) com TSB negativo ({tsb:.0f})',
            'action': 'Considerar fazer uma semana de recuperação. Monitorar como se sente.',
            'duration_days': 3
        }
    
    # Verifica tendência nos últimos dias
    if history and len(history) >= 3:
        recent_tsb = [h.get('tsb', 0) for h in history[-3:]]
        if all(t < -10 for t in recent_tsb):
            alert = {
                'category': AlertCategory.OVERTRAINING.value,
                'severity': AlertSeverity.WARNING.value,
                'title': '⚠️ TSB Cronicamente Negativo',
                'message': f'TSB negativo por 3+ dias seguidos',
                'action': 'Semana de recuperação recomendada',
                'duration_days': 7
            }
    
    return alert


def check_detraining_risk(ctl: float, ctl_trend: List[float], 
                         days_without_training: int = None) -> Optional[Dict]:
    """
    Detecta risco de detraining (perda de forma).
    
    Sinais:
    - CTL caindo > 5% em 7 dias
    - CTL caindo > 10% em 14 dias
    - Mais de 7 dias sem treino estruturado
    
    Args:
        ctl: CTL atual
        ctl_trend: Lista com últimas 14 leituras de CTL
        days_without_training: Dias desde último treino significativo
        
    Returns:
        Dict com alerta ou None
    """
    alert = None
    
    if len(ctl_trend) >= 7:
        ctl_7d_ago = ctl_trend[-7] if len(ctl_trend) >= 7 else ctl_trend[0]
        ctl_change = ((ctl - ctl_7d_ago) / ctl_7d_ago * 100) if ctl_7d_ago > 0 else 0
        
        if ctl_change < -10:
            alert = {
                'category': AlertCategory.DETRAINING.value,
                'severity': AlertSeverity.DANGER.value,
                'title': '📉 Risco de Detraining',
                'message': f'CTL caiu {abs(ctl_change):.1f}% em 7 dias!',
                'action': 'Aumentar volume gradualmente. Começar com 4-5 sessões/semana.',
                'duration_days': 14
            }
        elif ctl_change < -5:
            alert = {
                'category': AlertCategory.DETRAINING.value,
                'severity': AlertSeverity.WARNING.value,
                'title': '📉 Tendência de Detraining',
                'message': f'CTL diminuindo ({ctl_change:.1f}% em 7 dias)',
                'action': 'Aumentar frequência de treinos para estabilizar CTL',
                'duration_days': 7
            }
    
    if days_without_training and days_without_training > 7:
        alert = {
            'category': AlertCategory.DETRAINING.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '⏸️ Pausa no Treinamento',
            'message': f'{days_without_training} dias sem treino estruturado',
            'action': 'Começar a treinar novamente, começar suave (Z1-Z2)',
            'duration_days': 3
        }
    
    return alert


def check_performance_window(ctl: float, atl: float, tsb: float, 
                            last_peak_days_ago: int = None) -> Optional[Dict]:
    """
    Detecta janela ótima de performance (prova).
    
    Condições ideais:
    - CTL estável e alto (> 60)
    - TSB entre 5 e 20 (descansado mas não muito)
    - ATL controlado
    
    Args:
        ctl: CTL atual
        atl: ATL atual
        tsb: TSB atual
        last_peak_days_ago: Dias desde último pico de fitness
        
    Returns:
        Dict com alerta ou None
    """
    if ctl > 60 and 5 < tsb < 20 and atl < 60:
        alert = {
            'category': AlertCategory.PERFORMANCE_WINDOW.value,
            'severity': AlertSeverity.INFO.value,
            'title': '🎯 Janela de Performance Ideal',
            'message': f'Fitness ótimo! CTL={ctl:.0f}, TSB={tsb:.0f}, ATL={atl:.0f}',
            'action': 'Excelente janela para prova ou treino estratégico!',
            'duration_days': 5
        }
        return alert
    
    elif ctl > 50 and -5 < tsb < 10:
        alert = {
            'category': AlertCategory.PERFORMANCE_WINDOW.value,
            'severity': AlertSeverity.INFO.value,
            'title': '✅ Bom para Performance',
            'message': f'Fitness bom para treinos intensos ou provas',
            'action': 'Ótima oportunidade para trabalho de qualidade',
            'duration_days': 3
        }
        return alert
    
    return None


def check_recovery_needed(ctl: float, atl: float, tsb: float, 
                         hrv_baseline: float = None, last_hrv: float = None) -> Optional[Dict]:
    """
    Detecta necessidade de recuperação baseado em TSB e HRV.
    
    Args:
        ctl: CTL atual
        atl: ATL atual
        tsb: TSB atual
        hrv_baseline: HRV baseline do atleta
        last_hrv: Último valor de HRV
        
    Returns:
        Dict com alerta ou None
    """
    alert = None
    
    if tsb < -15:
        alert = {
            'category': AlertCategory.RECOVERY_WINDOW.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '😴 Recuperação Necessária',
            'message': f'TSB muito negativo ({tsb:.0f}), corpo precisa de descanso',
            'action': 'Dia de descanso ou sessão muito leve (Z1)',
            'duration_days': 1
        }
    
    elif atl > 50 and tsb < -5:
        alert = {
            'category': AlertCategory.RECOVERY_WINDOW.value,
            'severity': AlertSeverity.INFO.value,
            'title': '🔋 Recuperação Recomendada',
            'message': 'Carga aguda elevada, considere dia de descanso',
            'action': 'Descanso ou treino fácil para restaurar TSB',
            'duration_days': 1
        }
    
    if hrv_baseline and last_hrv:
        hrv_drop = ((hrv_baseline - last_hrv) / hrv_baseline * 100) if hrv_baseline > 0 else 0
        if hrv_drop > 20:  # HRV caiu mais de 20%
            alert = {
                'category': AlertCategory.HRV_DECLINE.value,
                'severity': AlertSeverity.WARNING.value,
                'title': '❤️ HRV Baixo - Sistema Nervoso Fatigado',
                'message': f'HRV caiu {hrv_drop:.0f}% do baseline',
                'action': 'Priorizar são e recuperação. Dia leve ou descanso.',
                'duration_days': 2
            }
            return alert
    
    return alert


def check_modality_imbalance(swim_percent: float, bike_percent: float, 
                            run_percent: float) -> Optional[Dict]:
    """
    Detecta desequilíbrio entre modalidades (importante em triathlon).
    
    Ideal para triathlon: 20% natação, 45% ciclismo, 35% corrida
    (por TSS ou volume)
    
    Args:
        swim_percent: Percentual de TSS em natação
        bike_percent: Percentual de TSS em ciclismo
        run_percent: Percentual de TSS em corrida
        
    Returns:
        Dict com alerta ou None
    """
    total = swim_percent + bike_percent + run_percent
    
    if total == 0:
        return None
    
    # Normaliza
    swim_pct = swim_percent / total * 100
    bike_pct = bike_percent / total * 100
    run_pct = run_percent / total * 100
    
    imbalances = []
    
    if swim_pct < 10:
        imbalances.append('Natação muito baixa (ideal: 15-25%)')
    elif swim_pct > 35:
        imbalances.append('Natação muito alta (ideal: 15-25%)')
    
    if bike_pct < 35:
        imbalances.append('Ciclismo abaixo do ideal (ideal: 40-50%)')
    elif bike_pct > 60:
        imbalances.append('Ciclismo muito alto (ideal: 40-50%)')
    
    if run_pct < 20:
        imbalances.append('Corrida abaixo do ideal (ideal: 25-35%)')
    elif run_pct > 45:
        imbalances.append('Corrida muito alta (ideal: 25-35%)')
    
    if imbalances:
        return {
            'category': AlertCategory.MODALITY_IMBALANCE.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '⚖️ Desequilíbrio de Modalidades',
            'message': ' | '.join(imbalances),
            'action': 'Ajustar distribuição de treinos',
            'current_distribution': {
                'natacao': f"{swim_pct:.0f}%",
                'ciclismo': f"{bike_pct:.0f}%",
                'corrida': f"{run_pct:.0f}%"
            },
            'duration_days': 14
        }
    
    return None


def check_sleep_quality(last_7_nights: List[int]) -> Optional[Dict]:
    """
    Detecta qualidade de sono ruins.
    
    Args:
        last_7_nights: Lista com minutos de sono dos últimos 7 dias
        
    Returns:
        Dict com alerta ou None
    """
    if not last_7_nights or len(last_7_nights) < 3:
        return None
    
    avg_sleep = sum(last_7_nights) / len(last_7_nights)
    poor_nights = sum(1 for s in last_7_nights if s < 360)  # Menos de 6h
    
    if poor_nights >= 3:
        alert = {
            'category': AlertCategory.SLEEP_QUALITY.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '😴 Sono Ruim - Reduzir Treino',
            'message': f'{poor_nights} noites ruins nos últimos {len(last_7_nights)} dias. Média: {avg_sleep/60:.1f}h',
            'action': 'Reduzir intensidade. Sono é crítico para adaptação.',
            'duration_days': 3
        }
        return alert
    
    elif avg_sleep < 360:  # Menos de 6h em média
        alert = {
            'category': AlertCategory.SLEEP_QUALITY.value,
            'severity': AlertSeverity.WARNING.value,
            'title': '😴 Sono Insuficiente',
            'message': f'Média de {avg_sleep/60:.1f}h por noite. Alvo: 7-9h',
            'action': 'Priorizar sono. Reduzir tela antes de dormir.',
            'duration_days': 7
        }
        return alert
    
    return None


# ==================== Motor de Alertas ====================

def generate_alerts(current_metrics: Dict, historical_data: Dict = None) -> List[Dict]:
    """
    Gera todos os alertas relevantes para o atleta.
    
    Args:
        current_metrics: Dict com métricas atuais
                        {'ctl': float, 'atl': float, 'tsb': float, 'hrv': float, ...}
        historical_data: Dict com histórico
                        {'ctl_trend': List, 'sleep': List, 'modality_pct': Dict, ...}
        
    Returns:
        Lista de alertas ativos
    """
    alerts = []
    
    # Extrai métricas
    ctl = current_metrics.get('ctl', 0)
    atl = current_metrics.get('atl', 0)
    tsb = current_metrics.get('tsb', 0)
    hrv = current_metrics.get('hrv')
    
    # Dados históricos
    history = historical_data.get('history', []) if historical_data else []
    ctl_trend = historical_data.get('ctl_trend', []) if historical_data else []
    sleep_data = historical_data.get('sleep_data', []) if historical_data else []
    hrv_baseline = historical_data.get('hrv_baseline') if historical_data else None
    modality = historical_data.get('modality_distribution', {}) if historical_data else {}
    last_peak_days = historical_data.get('last_peak_days_ago') if historical_data else None
    
    # Checa cada tipo de alerta
    alert = check_overtraining_risk(ctl, atl, tsb, history)
    if alert:
        alerts.append(alert)
    
    alert = check_detraining_risk(ctl, ctl_trend)
    if alert:
        alerts.append(alert)
    
    alert = check_performance_window(ctl, atl, tsb, last_peak_days)
    if alert:
        alerts.append(alert)
    
    alert = check_recovery_needed(ctl, atl, tsb, hrv_baseline, hrv)
    if alert:
        alerts.append(alert)
    
    alert = check_modality_imbalance(
        modality.get('swim', 0),
        modality.get('bike', 0),
        modality.get('run', 0)
    )
    if alert:
        alerts.append(alert)
    
    alert = check_sleep_quality(sleep_data)
    if alert:
        alerts.append(alert)
    
    return alerts


def prioritize_alerts(alerts: List[Dict]) -> List[Dict]:
    """
    Ordena alertas por prioridade (DANGER > WARNING > INFO).
    
    Args:
        alerts: Lista de alertas
        
    Returns:
        Lista ordenada
    """
    severity_order = {
        AlertSeverity.DANGER.value: 0,
        AlertSeverity.WARNING.value: 1,
        AlertSeverity.INFO.value: 2
    }
    
    return sorted(alerts, key=lambda x: severity_order.get(x['severity'], 999))


# ==================== Dashboard de Alertas ====================

def create_alert_dashboard(alerts: List[Dict]) -> Dict:
    """
    Cria dashboard consolidado de alertas.
    
    Args:
        alerts: Lista de alertas ativos
        
    Returns:
        Dict com dashboard formatado
    """
    danger_count = sum(1 for a in alerts if a['severity'] == AlertSeverity.DANGER.value)
    warning_count = sum(1 for a in alerts if a['severity'] == AlertSeverity.WARNING.value)
    info_count = sum(1 for a in alerts if a['severity'] == AlertSeverity.INFO.value)
    
    # Agrupa por categoria
    by_category = {}
    for alert in alerts:
        cat = alert['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(alert)
    
    return {
        'summary': {
            'total_alerts': len(alerts),
            'danger_count': danger_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'status': 'CRITICAL' if danger_count > 0 else ('CAUTION' if warning_count > 0 else 'GOOD')
        },
        'alerts': prioritize_alerts(alerts),
        'by_category': by_category,
        'generated_at': datetime.now().isoformat()
    }


def get_next_action(alerts: List[Dict]) -> str:
    """
    Sugere próxima ação baseada em alertas.
    
    Args:
        alerts: Lista de alertas
        
    Returns:
        String com recomendação
    """
    if not alerts:
        return "✅ Tudo bem! Continue o treinamento conforme planejado."
    
    # Prioriza por ação
    for alert in prioritize_alerts(alerts):
        if alert['severity'] == AlertSeverity.DANGER.value:
            return f"🔴 {alert['action']}"
        elif alert['severity'] == AlertSeverity.WARNING.value:
            return f"🟡 {alert['action']}"
    
    return f"ℹ️ {alerts[0]['action']}"
