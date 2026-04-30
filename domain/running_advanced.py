"""
Running Advanced Metrics - P2 Implementation

Funcionalidades de análise avançada de corrida:
- NGP (Normalized Graded Pace)
- Running Effectiveness (RE)
- Time in Zones Distribution
- Aerobic Decoupling (versão corrida)
- Peak Performances Running

Baseado em TrainingPeaks e literatura científica.
"""
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


# =============================================================================
# NGP - NORMALIZED GRADED PACE
# =============================================================================

@dataclass
class NGPCalculation:
    """Resultado do cálculo de NGP."""
    ngp_sec_per_km: float  # Pace ajustado (s/km)
    raw_pace_sec_per_km: float  # Pace original (s/km)
    elevation_gain_m: float  # Ganho de elevação
    elevation_loss_m: float  # Perda de elevação
    distance_m: float  # Distância total
    adjustment_factor: float  # Fator de ajuste aplicado


def calculate_ngp(
    pace_sec_per_km: float,
    grade_percent: float,
    distance_m: float,
    method: str = 'daniels'
) -> float:
    """
    Calcula Normalized Graded Pace (NGP).
    
    NGP ajusta o pace baseado na inclinação/declive do terreno,
    permitindo comparação justa entre treinos em terrenos diferentes.
    
    Fórmulas baseadas em:
    - Daniels & Daniels (2001): Energia cost of grade running
    - Minetti et al. (2002): Energy cost of walking and running
    
    Args:
        pace_sec_per_km: Pace atual (s/km)
        grade_percent: Inclinação (%), positivo = subida, negativo = descida
        distance_m: Distância percorrida (metros)
        method: 'daniels' (padrão) ou 'minetti'
    
    Returns:
        NGP ajustado (s/km) - equivalente a correr em plano
    """
    if pace_sec_per_km <= 0:
        return 0.0
    
    if method == 'daniels':
        # Fórmula aproximada baseada em Daniels & Daniels:
        # Custo energético aumenta ~4-5% por 1% de inclinação
        # Ganho de velocidade em descida é menor que perda em subida
        
        if grade_percent > 0:  # Subida
            # Custo: ~4.5% por 1% de inclinação
            cost_factor = 1 + (grade_percent * 0.045)
        else:  # Descida
            # Benefício: ~2.5% por 1% de declive (assimetria)
            cost_factor = 1 + (grade_percent * 0.025)
        
        ngp = pace_sec_per_km * cost_factor
        
    elif method == 'minetti':
        # Fórmula mais precisa de Minetti et al.
        # Custo energético de corrida por inclinação
        
        # Coeficiente de custo energético (J/kg/m)
        # Mínimo em -5% a -10%, aumenta em subidas e descidas íngremes
        if grade_percent > 0:
            # Subida: custo aumenta
            energy_cost = 3.8 + (0.067 * grade_percent) + (0.0002 * grade_percent ** 2)
        else:
            # Descida: custo diminui até certo ponto
            energy_cost = 3.8 + (0.03 * grade_percent)
        
        # NGP é proporcional ao custo energético
        base_cost = 3.8  # Custo em plano
        ngp = pace_sec_per_km * (energy_cost / base_cost)
        
    else:
        raise ValueError(f"Método desconhecido: {method}")
    
    return max(0, ngp)


def calculate_ngp_from_gps_data(
    pace_data: List[float],  # s/km
    elevation_data: List[float],  # metros
    grade_method: str = 'daniels'
) -> List[float]:
    """
    Calcula NGP a partir de dados GPS com elevação.
    
    Args:
        pace_data: Lista de paces (s/km) por ponto
        elevation_data: Lista de elevações (m) por ponto
        grade_method: Método de cálculo
    
    Returns:
        Lista de NGPs (s/km) por ponto
    """
    if len(pace_data) != len(elevation_data) or len(pace_data) < 2:
        return pace_data  # Retorna original se dados inválidos
    
    ngp_values = []
    
    for i in range(len(pace_data)):
        if i == 0:
            grade = 0.0  # Primeiro ponto assume plano
        else:
            # Calcula inclinação entre pontos consecutivos
            elevation_change = elevation_data[i] - elevation_data[i-1]
            # Assume ~10m por ponto em média (ajustar conforme necessário)
            horizontal_distance = 10.0
            grade = (elevation_change / horizontal_distance) * 100
        
        ngp = calculate_ngp(pace_data[i], grade, 10.0, grade_method)
        ngp_values.append(ngp)
    
    return ngp_values


# =============================================================================
# RUNNING EFFECTIVENESS (RE)
# =============================================================================

@dataclass
class RunningEffectiveness:
    """Métricas de eficiência de corrida."""
    re_ms_w: float  # RE em m/s/W (requer Stryd ou estimativa)
    speed_mps: float  # Velocidade (m/s)
    power_watts: float  # Potência estimada ou medida
    grade_percent: float  # Inclinação (%)
    
    def get_category(self) -> str:
        """
        Categoriza RE do atleta.
        
        Valores típicos (Coggan & Allen):
        - Elite: > 0.95 m/s/W
        - Avançado: 0.90-0.95 m/s/W
        - Intermediário: 0.85-0.90 m/s/W
        - Iniciante: < 0.85 m/s/W
        """
        if self.re_ms_w > 0.95:
            return "Elite"
        elif self.re_ms_w > 0.90:
            return "Avançado"
        elif self.re_ms_w > 0.85:
            return "Intermediário"
        else:
            return "Iniciante"


def calculate_running_effectiveness(
    speed_mps: float,
    power_watts: float,
    grade_percent: float = 0.0
) -> Optional[RunningEffectiveness]:
    """
    Calcula Running Effectiveness (RE).
    
    RE = velocidade / potência (m/s/W)
    
    Indica quão eficientemente o atleta converte potência em velocidade.
    RE mais alto = stride mais eficiente.
    
    Nota: Requer potência (Stryd) ou estimativa de potência de corrida.
    
    Args:
        speed_mps: Velocidade (m/s)
        power_watts: Potência (W) - do Stryd ou estimada
        grade_percent: Inclinação (%)
    
    Returns:
        RunningEffectiveness ou None se dados inválidos
    """
    if speed_mps <= 0 or power_watts <= 0:
        return None
    
    re = speed_mps / power_watts
    
    return RunningEffectiveness(
        re_ms_w=re,
        speed_mps=speed_mps,
        power_watts=power_watts,
        grade_percent=grade_percent
    )


def estimate_running_power(
    speed_mps: float,
    grade_percent: float = 0.0,
    weight_kg: float = 70.0,
    method: str = 'di prampero'
) -> float:
    """
    Estima potência de corrida sem Stryd.
    
    Fórmula baseada em Di Prampero et al. (1993):
    
    Potência = Custo energético × velocidade × peso
    
    Custo energético:
    - Plano: ~3.8 J/kg/m (Di Prampero)
    - Inclinação: aumenta conforme grade
    
    Args:
        speed_mps: Velocidade (m/s)
        grade_percent: Inclinação (%)
        weight_kg: Peso do atleta (kg)
        method: 'di prampero' (padrão)
    
    Returns:
        Potência estimada (W)
    """
    if speed_mps <= 0:
        return 0.0
    
    # Custo energético em plano (J/kg/m)
    base_cost = 3.8
    
    # Ajuste por inclinação (simplificado)
    if grade_percent > 0:
        # Subida: +0.067 J/kg/m por % de inclinação (aproximado)
        energy_cost = base_cost + (0.067 * grade_percent)
    elif grade_percent < -5:
        # Descida íngreme: custo aumenta novamente (freio)
        energy_cost = base_cost + (0.02 * abs(grade_percent + 5))
    else:
        # Descida leve: custo diminui
        energy_cost = base_cost + (0.03 * grade_percent)
    
    # Potência = custo × velocidade × peso
    power = energy_cost * speed_mps * weight_kg
    
    return max(0, power)


# =============================================================================
# TIME IN ZONES DISTRIBUTION
# =============================================================================

@dataclass
class ZoneDistribution:
    """Distribuição de tempo em zonas."""
    zone: int
    name: str
    time_sec: float
    percentage: float
    tss: float
    
    def format_time(self) -> str:
        """Formata tempo como HH:MM:SS."""
        hours = int(self.time_sec // 3600)
        minutes = int((self.time_sec % 3600) // 60)
        seconds = int(self.time_sec % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class RunningZone(Enum):
    """Zonas de corrida baseadas em pace ou FC."""
    RECOVERY = (1, "Recovery", "< 80% threshold")
    ENDURANCE = (2, "Endurance", "80-90% threshold")
    TEMPO = (3, "Tempo", "90-100% threshold")
    THRESHOLD = (4, "Threshold", "100-105% threshold")
    VO2MAX = (5, "VO2Max", "105-120% threshold")
    SPRINT = (6, "Sprint", "> 120% threshold")
    
    def __init__(self, number, name, description):
        self.number = number
        self.zone_name = name
        self.description = description


def calculate_time_in_zones(
    pace_data: List[float],  # s/km
    threshold_pace_sec_per_km: float,
    duration_per_point: float = 1.0  # segundos por ponto (default 1Hz)
) -> List[ZoneDistribution]:
    """
    Calcula distribuição de tempo em zonas de pace.
    
    Args:
        pace_data: Lista de paces (s/km)
        threshold_pace_sec_per_km: Pace de threshold (s/km)
        duration_per_point: Duração de cada ponto (segundos)
    
    Returns:
        Lista de ZoneDistribution por zona
    """
    if not pace_data or threshold_pace_sec_per_km <= 0:
        return []
    
    # Conta tempo em cada zona
    zone_times = defaultdict(float)
    zone_tss = defaultdict(float)
    total_time = len(pace_data) * duration_per_point
    
    for pace in pace_data:
        if pace <= 0:
            continue
        
        # Calcula intensidade relativa ao threshold
        intensity = threshold_pace_sec_per_km / pace  # > 1 = mais rápido
        
        # Determina zona baseada em intensidade
        if intensity < 0.8:
            zone = 1  # Recovery
        elif intensity < 0.9:
            zone = 2  # Endurance
        elif intensity < 1.0:
            zone = 3  # Tempo
        elif intensity < 1.05:
            zone = 4  # Threshold
        elif intensity < 1.2:
            zone = 5  # VO2Max
        else:
            zone = 6  # Sprint
        
        zone_times[zone] += duration_per_point
        
        # TSS por zona (simplificado)
        if zone == 1:
            tss_rate = 40  # TSS/hour
        elif zone == 2:
            tss_rate = 60
        elif zone == 3:
            tss_rate = 80
        elif zone == 4:
            tss_rate = 100
        elif zone == 5:
            tss_rate = 120
        else:
            tss_rate = 140
        
        zone_tss[zone] += (duration_per_point / 3600) * tss_rate
    
    # Monta resultado
    zone_names = {
        1: "Recovery",
        2: "Endurance",
        3: "Tempo",
        4: "Threshold",
        5: "VO2Max",
        6: "Sprint"
    }
    
    results = []
    for zone_num in sorted(zone_times.keys()):
        time_in_zone = zone_times[zone_num]
        percentage = (time_in_zone / total_time) * 100 if total_time > 0 else 0
        
        results.append(ZoneDistribution(
            zone=zone_num,
            name=zone_names[zone_num],
            time_sec=time_in_zone,
            percentage=round(percentage, 1),
            tss=round(zone_tss[zone_num], 1)
        ))
    
    return results


# =============================================================================
# AEROBIC DECOUPLING (VERSÃO COMPLETA)
# =============================================================================

@dataclass
class AerobicDecoupling:
    """Resultado de análise de decoupling."""
    first_half_ef: float  # EF primeira metade
    second_half_ef: float  # EF segunda metade
    decoupling_percent: float  # % de decoupling
    interpretation: str  # Interpretação
    
    def get_recommendation(self) -> str:
        """Retorna recomendação baseada no decoupling."""
        if self.decoupling_percent < 5:
            return "Excelente endurance base. Pode aumentar volume."
        elif self.decoupling_percent < 10:
            return "Endurance adequado. Manter treinamento atual."
        else:
            return "Priorizar treinos de endurance base (Zona 2)."


def calculate_aerobic_decoupling(
    first_half_np: float,
    first_half_hr: float,
    second_half_np: float,
    second_half_hr: float
) -> AerobicDecoupling:
    """
    Calcula Aerobic Decoupling completo com interpretação.
    
    Args:
        first_half_np: Normalized Power primeira metade (W)
        first_half_hr: FC média primeira metade (bpm)
        second_half_np: Normalized Power segunda metade (W)
        second_half_hr: FC média segunda metade (bpm)
    
    Returns:
        AerobicDecoupling com análise completa
    """
    # EF de cada metade
    ef_first = first_half_np / first_half_hr if first_half_hr > 0 else 0
    ef_second = second_half_np / second_half_hr if second_half_hr > 0 else 0
    
    # Decoupling
    if ef_first > 0:
        decoupling = ((ef_first - ef_second) / ef_first) * 100
    else:
        decoupling = 0.0
    
    # Interpretação
    if decoupling < 5:
        interpretation = "Excelente"
    elif decoupling < 10:
        interpretation = "Adequado"
    else:
        interpretation = "Precisa melhorar"
    
    return AerobicDecoupling(
        first_half_ef=round(ef_first, 3),
        second_half_ef=round(ef_second, 3),
        decoupling_percent=round(decoupling, 1),
        interpretation=interpretation
    )


# =============================================================================
# PEAK PERFORMANCES RUNNING
# =============================================================================

def find_running_pr(
    pace_data: List[float],  # s/km
    distance_m: float,
    standard_distances: List[float] = None
) -> Dict[str, float]:
    """
    Encontra PRs (Personal Records) de corrida por distância.
    
    Args:
        pace_data: Lista de paces (s/km)
        distance_m: Distância total do treino (m)
        standard_distances: Distâncias padrão para verificar (m)
    
    Returns:
        Dict com PRs (ex: {'5K': 1200, '10K': 2500, ...}) em segundos
    """
    if standard_distances is None:
        standard_distances = [
            400,     # 400m
            800,     # 800m
            1000,    # 1K
            1609,    # 1 mile
            3000,    # 3K
            5000,    # 5K
            10000,   # 10K
            21097,   # Half marathon
            42195,   # Marathon
        ]
    
    if not pace_data or distance_m <= 0:
        return {}
    
    # Calcula tempo acumulado para cada ponto
    cumulative_time = []
    total_time = 0
    
    for pace in pace_data:
        if pace > 0:
            # Tempo para percorrer 1km ao pace atual
            time_for_km = pace  # já é em s/km
            # Assume 1 ponto = 10m (ajustar conforme necessário)
            time_for_point = time_for_km / 100  # 10m = 1/100 km
            total_time += time_for_point
        cumulative_time.append(total_time)
    
    prs = {}
    
    for target_dist in standard_distances:
        if target_dist > distance_m:
            continue
        
        # Encontra melhor tempo para essa distância
        best_time = float('inf')
        
        # Janela deslizante
        for i in range(len(cumulative_time)):
            for j in range(i + 1, len(cumulative_time)):
                # Distância aproximada entre pontos i e j
                dist_ij = (j - i) * 10  # 10m por ponto
                
                if abs(dist_ij - target_dist) < 20:  # Tolerância de 20m
                    time_ij = cumulative_time[j] - cumulative_time[i]
                    best_time = min(best_time, time_ij)
        
        if best_time < float('inf'):
            # Formata nome da distância
            if target_dist < 1000:
                name = f"{target_dist}m"
            elif target_dist == 1609:
                name = "1Mile"
            elif target_dist == 21097:
                name = "Half"
            elif target_dist == 42195:
                name = "Marathon"
            else:
                name = f"{target_dist//1000}K"
            
            prs[name] = round(best_time, 1)
    
    return prs
