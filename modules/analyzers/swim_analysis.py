"""
Análise Completa de Natação - Critical Swim Speed, Pace e Eficiência
====================================================================

Módulo para análise profissional de atividades de natação.
Calcula CSS (Critical Swim Speed), zonas de pace, SWOLF, eficiência de técnica.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# ==================== CSS (Critical Swim Speed) ====================

def calculate_css_from_tests(distance1_m: float, time1_s: float, 
                             distance2_m: float, time2_s: float) -> float:
    """
    Calcula CSS (Critical Swim Speed) a partir de dois testes.
    
    Metodologia: Teste de 400m e 200m (ou similar)
    Fórmula: CSS = (D2 - D1) / (T2 - T1) onde D2 < D1
    Ou para dados simples: CSS = velocidade mantida sustentável
    
    Exemplo:
    - Teste 1: 400m em 400 segundos (1.0 m/s)
    - Teste 2: 200m em 160 segundos (1.25 m/s)
    - CSS = (200 - 400) / (160 - 400) = -200 / -240 = 0.833 m/s
    - Ou usar velocidade média ponderada das performances
    
    Args:
        distance1_m: Distância do teste 1 em metros (mais longo)
        time1_s: Tempo do teste 1 em segundos
        distance2_m: Distância do teste 2 em metros (mais curto/rápido)
        time2_s: Tempo do teste 2 em segundos
        
    Returns:
        CSS em m/s (metros por segundo)
    """
    if time1_s == time2_s or time1_s <= 0 or time2_s <= 0:
        return 0.0
    
    # Validação básica
    if distance1_m <= 0 or distance2_m <= 0:
        return 0.0
    
    # Método 1: Fórmula de Riegel adaptada para CSS
    # CSS = diferença de distância / diferença de tempo
    d_diff = abs(distance2_m - distance1_m)
    t_diff = abs(time2_s - time1_s)
    
    if t_diff == 0:
        return 0.0
    
    css_riegel = d_diff / t_diff
    
    # Método 2: Velocidade média dos dois testes (alternativa)
    vel1 = distance1_m / time1_s
    vel2 = distance2_m / time2_s
    css_avg = (vel1 + vel2) / 2
    
    # Retorna a velocidade mais conservadora (menor)
    # pois CSS deve ser mantível por tempo prolongado
    return min(css_riegel, css_avg)


def estimate_css_from_workouts(swims: List[Dict]) -> Optional[float]:
    """
    Estima CSS a partir do histórico de treinos de natação.
    
    Procura por treinos de threshold (5-20 min no ritmo máximo sustentável)
    e calcula uma média ponderada.
    
    Args:
        swims: Lista de dicts com histórico de natação
               Esperado: {'distance_m': float, 'duration_s': float, 'type': str}
        
    Returns:
        CSS estimado em m/s, ou None se dados insuficientes
    """
    if not swims or len(swims) < 3:
        return None
    
    # Filtra treinos de threshold/tempo (5-20 minutos)
    threshold_swims = []
    for swim in swims:
        duration_s = swim.get('duration_s', 0)
        
        # ✅ FIXO: Validar duration_s > 0
        if duration_s <= 0:
            continue
        
        duration_min = duration_s / 60
        swim_type = swim.get('type', '').lower()
        
        # Identifica treinos de threshold
        if (5 <= duration_min <= 20 and 'threshold' in swim_type) or \
           (5 <= duration_min <= 20 and swim.get('intensity', 0) > 0.85):
            threshold_swims.append(swim)
    
    if not threshold_swims:
        # Se não houver threshold identificado, usa as mais rápidas
        # ✅ FIXO: Validar durante_s > 0 antes de dividir
        valid_swims = [s for s in swims if s.get('duration_s', 0) > 0 and s.get('distance_m', 0) > 0]
        if not valid_swims:
            return None
        
        swims_sorted = sorted(valid_swims, 
                             key=lambda x: x.get('distance_m', 0) / x.get('duration_s', 0),
                             reverse=True)
        threshold_swims = swims_sorted[:5]  # Top 5 mais rápidas
    
    if not threshold_swims:
        return None
    
    # Calcula velocidade média dos threshold swims
    css_values = []
    for swim in threshold_swims:
        duration_s = swim.get('duration_s', 0)
        distance_m = swim.get('distance_m', 0)
        
        if duration_s > 0 and distance_m > 0:
            velocity = distance_m / duration_s
            css_values.append(velocity)
    
    if not css_values:
        return None
    
    return np.mean(css_values)


def css_to_pace_format(css_ms: float) -> str:
    """
    Converte CSS em m/s para formato de pace (MM:SS por 100m).
    
    Padrão: MM:SS (minutos:segundos)
    
    Args:
        css_ms: CSS em metros por segundo
        
    Returns:
        String no formato "MM:SS" representando tempo para completar 100m
    """
    if css_ms is None or css_ms <= 0:
        return "00:00"
    
    try:
        pace_s = 100 / css_ms  # Segundos para completar 100m
        minutes = int(pace_s // 60)
        seconds = int(pace_s % 60)
        
        # Limita a 99:59 máximo
        if minutes > 99:
            minutes = 99
            seconds = 59
        
        return f"{minutes:02d}:{seconds:02d}"
    except (ValueError, ZeroDivisionError):
        return "00:00"


# ==================== Zonas de Natação ====================

SWIM_ZONES = {
    'z1': {'name': 'Recuperação', 'percent_css': (0, 80), 'tss_hour': 55, 'description': 'Recuperação ativa'},
    'z2': {'name': 'Resistência', 'percent_css': (81, 88), 'tss_hour': 75, 'description': 'Treino aeróbico base'},
    'z3': {'name': 'Tempo', 'percent_css': (89, 95), 'tss_hour': 90, 'description': 'Ritmo moderado-intenso'},
    'z4': {'name': 'Limiar', 'percent_css': (96, 100), 'tss_hour': 100, 'description': 'CSS - Limiar crítico'},
    'z5': {'name': 'VO2 Máx', 'percent_css': (101, 110), 'tss_hour': 120, 'description': 'Acima de CSS'}
}


def calculate_swim_zones(css_ms: float) -> Dict[str, Dict]:
    """
    Calcula as 5 zonas de natação baseadas em CSS.
    
    Princípio: % maior = velocidade maior = tempo menor por 100m
    Z1: 0-80% CSS = mais lento
    Z5: 101-110% CSS = mais rápido
    
    Args:
        css_ms: CSS em metros por segundo
        
    Returns:
        Dict com zonas e seus ranges de pace
    """
    # ✅ FIXO: Validar CSS - rejeitar valores impossíveis
    # CSS máximo humano: ~2.5 m/s (elite), amadores: 0.8-1.5 m/s
    # CSS mínimo razoável: 0.3 m/s
    if css_ms is None or css_ms <= 0 or css_ms < 0.3 or css_ms > 3.0:
        return {}  # Retorna vazio para valores impossíveis
    
    zones = {}
    
    for zone_key, zone_info in SWIM_ZONES.items():
        min_percent, max_percent = zone_info['percent_css']
        
        # Calcula velocidades (m/s)
        # min_percent MENOR = velocidade MENOR = tempo MAIOR
        # max_percent MAIOR = velocidade MAIOR = tempo MENOR
        min_vel = (min_percent / 100) * css_ms
        max_vel = (max_percent / 100) * css_ms
        
        # Converte para pace por 100m
        # Velocidade maior (max_vel) = tempo menor (min_pace_s)
        # Velocidade menor (min_vel) = tempo maior (max_pace_s)
        
        if max_vel > 0:
            min_pace_s = 100 / max_vel  # Tempo mínimo (zona rápida)
        else:
            min_pace_s = 0
            
        if min_vel > 0:
            max_pace_s = 100 / min_vel  # Tempo máximo (zona lenta)
        else:
            max_pace_s = 999
        
        # Formata paces
        min_pace_formatted = f"{int(min_pace_s // 60):02d}:{int(min_pace_s % 60):02d}"
        max_pace_formatted = f"{int(max_pace_s // 60):02d}:{int(max_pace_s % 60):02d}"
        
        zones[zone_key] = {
            **zone_info,
            'velocity_range_ms': (min_vel, max_vel),
            'pace_range_s': (min_pace_s, max_pace_s),  # Em segundos por 100m
            'pace_range_formatted': (min_pace_formatted, max_pace_formatted)
        }
    
    return zones


# ==================== SWOLF - Eficiência ====================

def calculate_swolf(distance_m: float, duration_s: float, stroke_count: int) -> float:
    """
    Calcula SWOLF (Swim Golf) - índice de eficiência de natação.
    
    SWOLF = Tempo de comprimento de piscina + Número de braçadas em comprimento
    (padrão: calcula por 25m ou 50m dependendo da piscina)
    
    Valores:
    - < 35: Excelente (elite)
    - 35-40: Muito bom
    - 40-45: Bom
    - 45-50: Moderado
    - > 50: Precisa de trabalho técnico
    
    Args:
        distance_m: Distância total em metros
        duration_s: Duração total em segundos
        stroke_count: Número total de braçadas
        
    Returns:
        SWOLF score (tempo + braçadas por comprimento)
    """
    if distance_m <= 0 or duration_s <= 0 or stroke_count <= 0:
        return 0
    
    # ✅ FIXO: Pool detection heurística melhorada
    # Regra:
    # - Se 1500m: é 60x25m (piscina 25m) - MAIS COMUM em triathlon
    # - Se 1200m: é 48x25m (piscina 25m)
    # - Se 1000m: é 40x25m (piscina 25m)
    # 
    # Piscinas 50m são menos comuns em triathlon
    # Mas podem aparecer em treino específico
    #
    # Heurística: Default 25m (mais comum)
    # Só muda para 50m se CLARAMENTE é múltiplo de 50
    # E tem padrão que sugere 50m (ex: 2000m = 40x50m)
    
    pool_length = 25  # Default para piscina 25m (mais comum)
    
    # Detecta piscina 50m apenas em casos claros
    if distance_m % 50 == 0 and distance_m % 25 != 0:
        # É múltiplo de 50 MAS NÃO de 25
        # Exemplo: 2050m (41x50m), 50m (1x50m)
        pool_length = 50
    elif distance_m == 2000 or distance_m == 1000:
        # Casos ambíguos: 2000m pode ser 80x25m ou 40x50m
        # Default para 25m (mais comum em triathlon)
        pool_length = 25
    
    # Número de comprimentos de piscina
    num_lengths = distance_m / pool_length
    
    if num_lengths == 0:
        return 0
    
    # Tempo médio por comprimento
    time_per_length = duration_s / num_lengths
    
    # Braçadas médias por comprimento
    strokes_per_length = stroke_count / num_lengths
    
    # SWOLF por comprimento
    swolf = time_per_length + strokes_per_length
    
    return swolf


def interpret_swolf(swolf: float) -> Dict[str, str]:
    """
    Interpreta o score SWOLF.
    
    Args:
        swolf: Score SWOLF
        
    Returns:
        Dict com interpretação e recomendações
    """
    if swolf < 35:
        return {
            'level': 'Excelente',
            'color': 'success',
            'description': 'Técnica elite',
            'recommendation': 'Manter esta eficiência'
        }
    elif swolf < 40:
        return {
            'level': 'Muito Bom',
            'color': 'success',
            'description': 'Excelente eficiência técnica',
            'recommendation': 'Focar em velocidade, técnica já é muito boa'
        }
    elif swolf < 45:
        return {
            'level': 'Bom',
            'color': 'info',
            'description': 'Eficiência sólida',
            'recommendation': 'Trabalhar redução de braçadas mantendo velocidade'
        }
    elif swolf < 50:
        return {
            'level': 'Moderado',
            'color': 'warning',
            'description': 'Há espaço para melhora',
            'recommendation': 'Treinos técnicos 2x/semana, drill work'
        }
    else:
        return {
            'level': 'Precisa Melhoria',
            'color': 'danger',
            'description': 'Eficiência comprometida',
            'recommendation': 'Priorizar técnica, trabalhar com drills, reduza intensidade'
        }


# ==================== Distance Per Stroke (DPS) ====================

def calculate_dps(distance_m: float, stroke_count: int) -> float:
    """
    Calcula DPS (Distance Per Stroke) - distância coberta por braçada.
    
    Indica economia de movimento e eficiência técnica.
    
    Valores típicos:
    - Élite: 2.0-2.5 metros/braçada
    - Intermediário: 1.5-2.0 metros/braçada
    - Iniciante: 1.0-1.5 metros/braçada
    
    Args:
        distance_m: Distância total em metros
        stroke_count: Número total de braçadas
        
    Returns:
        DPS em metros por braçada
    """
    # ✅ FIXO: Validar inputs - rejeitar negativos e valores impossíveis
    if stroke_count <= 0 or distance_m <= 0:
        return 0
    
    dps = distance_m / stroke_count
    
    # Sanity check: DPS máximo fisicamente possível é ~3.5 m/braçada (Michael Phelps)
    # DPS mínimo razoável: 0.5 m/braçada
    if dps > 5.0 or dps < 0.1:
        return 0  # Valor fisicamente impossível
    
    return dps


def interpret_dps(dps: float) -> Dict[str, str]:
    """
    Interpreta DPS baseado no nível de nado.
    
    Args:
        dps: Distance Per Stroke em m/braçada
        
    Returns:
        Dict com interpretação
    """
    if dps >= 2.0:
        return {
            'level': 'Excelente',
            'color': 'success',
            'description': 'Economia excelente de movimento',
            'recommendation': 'Manter técnica'
        }
    elif dps >= 1.7:
        return {
            'level': 'Muito Bom',
            'color': 'success',
            'description': 'Boa economia de braçadas',
            'recommendation': 'Trabalhar ritmo mantendo economia'
        }
    elif dps >= 1.4:
        return {
            'level': 'Bom',
            'color': 'info',
            'description': 'Economia razoável',
            'recommendation': 'Drills de comprimento e técnica'
        }
    elif dps >= 1.1:
        return {
            'level': 'Moderado',
            'color': 'warning',
            'description': 'Muitas braçadas para distância',
            'recommendation': 'Focar em saque e catch, work on stroke length'
        }
    else:
        return {
            'level': 'Baixo',
            'color': 'danger',
            'description': 'Muito ineficiente',
            'recommendation': 'Aulas de técnica, reduzir velocidade para melhorar forma'
        }


# ==================== Stroke Rate ====================

def calculate_stroke_rate(stroke_count: int, duration_s: float) -> float:
    """
    Calcula frequência de braçada (strokes por minuto).
    
    Valores típicos:
    - Sprinter/Croler: 60-80 SPM
    - Distance: 50-70 SPM
    - Triathlon: 70-100 SPM (mais rápido por ser economia)
    
    Args:
        stroke_count: Número total de braçadas
        duration_s: Duração em segundos
        
    Returns:
        Strokes per minute (SPM)
    """
    if duration_s <= 0 or stroke_count <= 0:
        return 0
    
    # ✅ FIXO: Adicionar validação de valores impossíveis
    # Máximo fisicamente possível: ~10 braçadas por segundo = 600 SPM
    # Mínimo fisicamente possível: ~0.5 braçadas por segundo = 30 SPM
    
    duration_min = duration_s / 60
    spm = stroke_count / duration_min
    
    # Sanity checks - CRÍTICO: rejeitar valores fisiologicamente impossíveis
    # Máximo: ~200 SPM (elite sprinters em burst curto)
    # Mínimo: ~20 SPM (muito lento, praticamente inviável)
    if spm > 200 or spm < 20:
        # Valor fisiologicamente impossível
        return 0
    
    return spm


def analyze_swim_efficiency(swims: List[Dict]) -> Dict:
    """
    Análise completa de eficiência de natação.
    
    Args:
        swims: Lista de treinos de natação
        
    Returns:
        Dict com análise consolidada
    """
    if not swims:
        return {}
    
    analysis = {
        'total_swims': len(swims),
        'total_distance_m': 0,
        'total_duration_h': 0,
        'avg_pace_100m': 0,
        'avg_swolf': 0,
        'avg_dps': 0,
        'avg_spm': 0,
        'swims_by_type': {},
        'best_swolf': {'swim': None, 'swolf': float('inf')},
        'worst_swolf': {'swim': None, 'swolf': 0},
        'trend': 'stable'
    }
    
    swolf_scores = []
    dps_scores = []
    spm_scores = []
    pace_scores = []
    
    for swim in swims:
        distance = swim.get('distance_m', 0)
        duration = swim.get('duration_s', 0)
        strokes = swim.get('stroke_count', 0)
        swim_type = swim.get('type', 'unknown')
        
        if distance > 0 and duration > 0:
            # Accumula totais
            analysis['total_distance_m'] += distance
            analysis['total_duration_h'] += duration / 3600
            
            # Calcula métricas
            if strokes > 0:
                swolf = calculate_swolf(distance, duration, strokes)
                swolf_scores.append(swolf)
                
                dps = calculate_dps(distance, strokes)
                dps_scores.append(dps)
                
                spm = calculate_stroke_rate(strokes, duration)
                spm_scores.append(spm)
            
            pace = (duration / distance) * 100  # segundos por 100m
            pace_scores.append(pace)
            
            # Agrupa por tipo
            if swim_type not in analysis['swims_by_type']:
                analysis['swims_by_type'][swim_type] = 0
            analysis['swims_by_type'][swim_type] += 1
            
            # Rastreia melhor/pior SWOLF
            if swolf_scores:
                if swolf_scores[-1] < analysis['best_swolf']['swolf']:
                    analysis['best_swolf'] = {'swim': swim, 'swolf': swolf_scores[-1]}
                if swolf_scores[-1] > analysis['worst_swolf']['swolf']:
                    analysis['worst_swolf'] = {'swim': swim, 'swolf': swolf_scores[-1]}
    
    # Calcula médias
    if swolf_scores:
        analysis['avg_swolf'] = np.mean(swolf_scores)
        # Tendência nos últimos 5
        if len(swolf_scores) >= 5:
            recent = swolf_scores[-5:]
            if np.mean(recent[-3:]) < np.mean(recent[:3]):
                analysis['trend'] = 'improving'
            elif np.mean(recent[-3:]) > np.mean(recent[:3]):
                analysis['trend'] = 'declining'
    
    if dps_scores:
        analysis['avg_dps'] = np.mean(dps_scores)
    
    if spm_scores:
        analysis['avg_spm'] = np.mean(spm_scores)
    
    if pace_scores:
        analysis['avg_pace_100m'] = np.mean(pace_scores)
    
    return analysis


# ==================== Análise de Distribuição ====================

def analyze_swim_by_zone(swims: List[Dict], css_ms: float) -> Dict:
    """
    Analisa distribuição de treinos por zona de natação.
    
    Args:
        swims: Lista de treinos
        css_ms: CSS em m/s para calcular zonas
        
    Returns:
        Dict com distribuição por zona
    """
    zones = calculate_swim_zones(css_ms)
    distribution = {zone: {'count': 0, 'distance_m': 0, 'duration_s': 0, 'tss': 0} 
                   for zone in zones.keys()}
    
    total_distance = 0
    total_duration = 0
    
    for swim in swims:
        distance = swim.get('distance_m', 0)
        duration = swim.get('duration_s', 0)
        
        if distance > 0 and duration > 0:
            total_distance += distance
            total_duration += duration
            
            # Calcula velocidade média do swim
            velocity = distance / duration
            
            # ✅ FIXO: Evitar lacunas entre zonas
            # Encontra a zona mais próxima
            zone_found = False
            
            # Primeiro tenta encontrar zona exata
            for zone_key, zone_info in zones.items():
                min_vel, max_vel = zone_info['velocity_range_ms']
                # ✅ Inclusão: <= max_vel (não exclusivo)
                if min_vel <= velocity <= max_vel:
                    distribution[zone_key]['count'] += 1
                    distribution[zone_key]['distance_m'] += distance
                    distribution[zone_key]['duration_s'] += duration
                    zone_found = True
                    break
            
            # Se não encontrou (velocidade acima de Z5 ou abaixo de Z1)
            if not zone_found:
                # Identifica velocidade muito alta (> Z5)
                z5_max = zones['z5']['velocity_range_ms'][1]
                if velocity > z5_max:
                    distribution['z5']['count'] += 1
                    distribution['z5']['distance_m'] += distance
                    distribution['z5']['duration_s'] += duration
                # Identifica velocidade muito baixa (< Z1 mínimo)
                else:
                    distribution['z1']['count'] += 1
                    distribution['z1']['distance_m'] += distance
                    distribution['z1']['duration_s'] += duration
    
    # Calcula percentuais
    for zone in distribution.values():
        zone['percent_distance'] = (zone['distance_m'] / total_distance * 100) if total_distance > 0 else 0
        zone['percent_time'] = (zone['duration_s'] / total_duration * 100) if total_duration > 0 else 0
    
    return distribution


def evaluate_swim_distribution(distribution: Dict) -> Dict[str, any]:
    """
    Avalia se a distribuição de treino segue princípios científicos.
    
    Princípio 80/20: 80% Z1-Z2, 10% Z3-Z4, 10% Z5
    
    Args:
        distribution: Distribuição por zona
        
    Returns:
        Dict com avaliação e recomendações
    """
    z1_z2_pct = distribution.get('z1', {}).get('percent_distance', 0) + \
                distribution.get('z2', {}).get('percent_distance', 0)
    z3_z4_pct = distribution.get('z3', {}).get('percent_distance', 0) + \
                distribution.get('z4', {}).get('percent_distance', 0)
    z5_pct = distribution.get('z5', {}).get('percent_distance', 0)
    
    recommendations = []
    
    if z1_z2_pct < 70:
        recommendations.append(f"Aumentar volume Z1-Z2 (atual: {z1_z2_pct:.0f}%, alvo: 70-80%)")
    elif z1_z2_pct > 85:
        recommendations.append(f"Reduzir Z1-Z2, adicionar mais trabalho de qualidade")
    
    if z3_z4_pct < 5:
        recommendations.append(f"Adicionar treinos threshold/tempo (Z3-Z4)")
    elif z3_z4_pct > 20:
        recommendations.append(f"Reduzir Z3-Z4, focar em recuperação")
    
    if z5_pct < 5 and z5_pct > 0:
        recommendations.append(f"Aumentar VO2Max work (Z5)")
    elif z5_pct > 15:
        recommendations.append(f"Reduzir Z5, risco de overtraining")
    
    return {
        'distribution': {
            'z1_z2': z1_z2_pct,
            'z3_z4': z3_z4_pct,
            'z5': z5_pct
        },
        'is_balanced': 70 <= z1_z2_pct <= 85 and 5 <= z3_z4_pct <= 15 and 5 <= z5_pct <= 15,
        'recommendations': recommendations if recommendations else ['Distribuição equilibrada!']
    }


# ==================== Relatório de Natação ====================

def generate_swim_report(swims: List[Dict], css_ms: float = None) -> Dict:
    """
    Gera relatório completo de análise de natação.
    
    Args:
        swims: Lista de treinos de natação
        css_ms: CSS em m/s (calcula automaticamente se não fornecer)
        
    Returns:
        Dict com relatório completo
    """
    if not css_ms:
        css_ms = estimate_css_from_workouts(swims) or 1.1  # CSS mínimo para iniciante
    
    efficiency = analyze_swim_efficiency(swims)
    zones = calculate_swim_zones(css_ms)
    distribution = analyze_swim_by_zone(swims, css_ms)
    evaluation = evaluate_swim_distribution(distribution)
    
    return {
        'css': {
            'ms': css_ms,
            'pace_100m': css_to_pace_format(css_ms),
            'description': 'Velocidade crítica sustentável'
        },
        'zones': zones,
        'efficiency': efficiency,
        'distribution': distribution,
        'evaluation': evaluation,
        'generated_at': datetime.now().isoformat()
    }
