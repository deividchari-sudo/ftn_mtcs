"""
Power Curve e Critical Power Analysis

Implementação de:
- Mean Maximal Power (MMP) Curve
- Critical Power (CP) Model
- W' (W-prime) - Capacidade Anaeróbia
- Power Profile

Baseado em:
- TrainingPeaks Power Profile: https://www.trainingpeaks.com/learn/articles/power-profile/
- Critical Power Model: https://www.trainingpeaks.com/learn/articles/understanding-the-critical-power-model/
"""
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PowerCurvePoint:
    """Ponto na curva de potência (duração -> potência máxima)."""
    duration_sec: float
    power: float
    date: Optional[datetime] = None
    activity_id: Optional[str] = None


@dataclass
class CriticalPowerModel:
    """Modelo de Critical Power (Monod & Scherrer 1965)."""
    cp: float  # Critical Power (W)
    w_prime: float  # W' - capacidade anaeróbia (J)
    r_squared: float  # Qualidade do fit (0-1)
    
    def predict_time(self, power: float) -> Optional[float]:
        """
        Prediz tempo máximo sustentável para uma potência.
        
        Fórmula: t = W' / (P - CP)
        
        Args:
            power: Potência alvo (W)
            
        Returns:
            Tempo em segundos, ou None se P <= CP
        """
        if power <= self.cp:
            return None  # Pode sustentar indefinidamente (teoricamente)
        
        return self.w_prime / (power - self.cp)
    
    def predict_power(self, duration_sec: float) -> float:
        """
        Prediz potência máxima sustentável por um tempo.
        
        Fórmula: P = CP + W'/t
        
        Args:
            duration_sec: Duração em segundos
            
        Returns:
            Potência máxima (W)
        """
        if duration_sec <= 0:
            return float('inf')
        
        return self.cp + (self.w_prime / duration_sec)
    
    def get_equivalent_power(self, duration_sec: float) -> float:
        """Alias para predict_power."""
        return self.predict_power(duration_sec)


@dataclass
class PowerProfile:
    """
    Power Profile do atleta (best efforts por duração).
    
    Durações padrão TrainingPeaks:
    - 5s: Neuromuscular
    - 1min: Anaeróbico
    - 5min: VO2Max
    - 20min: Threshold
    - 60min: FTP
    """
    best_5s: float
    best_1min: float
    best_5min: float
    best_20min: float
    best_60min: float
    
    def get_category(self) -> str:
        """
        Classifica o perfil do atleta baseado em best_20min (FTP proxy).
        
        Categorias baseadas em Coggan:
        - World Class: > 5.5 W/kg
        - Exceptional: 5.0-5.5 W/kg
        - Excellent: 4.5-5.0 W/kg
        - Very Good: 4.0-4.5 W/kg
        - Good: 3.5-4.0 W/kg
        - Moderate: 3.0-3.5 W/kg
        - Fair: 2.5-3.0 W/kg
        - Untrained: < 2.5 W/kg
        
        Nota: Requer peso do atleta para W/kg
        """
        # Sem peso, usamos valores absolutos (assumindo ~70kg)
        ftp_proxy = self.best_20min
        w_per_kg = ftp_proxy / 70.0  # Assumindo 70kg
        
        if w_per_kg > 5.5:
            return "World Class"
        elif w_per_kg > 5.0:
            return "Exceptional"
        elif w_per_kg > 4.5:
            return "Excellent"
        elif w_per_kg > 4.0:
            return "Very Good"
        elif w_per_kg > 3.5:
            return "Good"
        elif w_per_kg > 3.0:
            return "Moderate"
        elif w_per_kg > 2.5:
            return "Fair"
        else:
            return "Untrained"


# =============================================================================
# CÁLCULO DA CURVA DE POTÊNCIA (MMP)
# =============================================================================

def calculate_mean_maximal_power(
    power_data: List[float],
    durations: List[int] = None
) -> List[PowerCurvePoint]:
    """
    Calcula Mean Maximal Power (MMP) para várias durações.
    
    MMP é a máxima potência média sustentada por uma duração específica.
    
    Args:
        power_data: Lista de potências (W) ao longo do tempo (1Hz típico)
        durations: Lista de durações (segundos) para calcular. 
                  Se None, usa padrões TrainingPeaks.
    
    Returns:
        Lista de PowerCurvePoint (duração -> MMP)
    """
    if not power_data or len(power_data) == 0:
        return []
    
    # Durações padrão TrainingPeaks (em segundos)
    if durations is None:
        durations = [
            1, 5, 10, 15, 30, 60,      # Curto prazo (neuromuscular/anaeróbio)
            120, 300, 600, 1200,       # Médio prazo (VO2Max/threshold)
            1800, 3600, 7200           # Longo prazo (endurance)
        ]
    
    results = []
    
    for duration in durations:
        if duration > len(power_data):
            continue  # Duração maior que dados disponíveis
        
        # Calcula média móvel de todas as janelas possíveis
        max_avg_power = 0.0
        
        for i in range(len(power_data) - duration + 1):
            window = power_data[i:i + duration]
            avg_power = sum(window) / len(window)
            max_avg_power = max(max_avg_power, avg_power)
        
        if max_avg_power > 0:
            results.append(PowerCurvePoint(
                duration_sec=duration,
                power=max_avg_power
            ))
    
    return results


def calculate_power_curve_from_activities(
    activities: List[Dict],
    duration_days: int = 90
) -> List[PowerCurvePoint]:
    """
    Calcula Power Curve a partir de múltiplas atividades.
    
    Args:
        activities: Lista de atividades com 'power_data' (array de watts)
        duration_days: Janela de tempo (dias) para considerar
    
    Returns:
        Power Curve (melhores esforços no período)
    """
    cutoff_date = datetime.now() - timedelta(days=duration_days)
    
    # Coleta todos os dados de potência recentes
    all_power_points = []
    
    for activity in activities:
        # Verifica data
        activity_date = activity.get('start_time')
        if isinstance(activity_date, str):
            try:
                activity_date = datetime.fromisoformat(activity_date.replace('Z', '+00:00'))
            except:
                continue
        
        if activity_date and activity_date < cutoff_date:
            continue
        
        # Extrai dados de potência
        power_stream = activity.get('power_stream', activity.get('power_data', []))
        if power_stream and len(power_stream) > 0:
            mmp_points = calculate_mean_maximal_power(power_stream)
            all_power_points.extend(mmp_points)
    
    # Para cada duração, pega o melhor esforço global
    duration_to_best = {}
    for point in all_power_points:
        if point.duration_sec not in duration_to_best:
            duration_to_best[point.duration_sec] = point
        elif point.power > duration_to_best[point.duration_sec].power:
            duration_to_best[point.duration_sec] = point
    
    # Ordena por duração
    results = sorted(duration_to_best.values(), key=lambda x: x.duration_sec)
    return results


# =============================================================================
# CRITICAL POWER MODEL
# =============================================================================

def calculate_critical_power(
    efforts: List[Tuple[float, float]],
    method: str = '2-parameter'
) -> Optional[CriticalPowerModel]:
    """
    Calcula Critical Power e W' a partir de esforços máximos.
    
    Modelo 2-parâmetros (Monod & Scherrer):
    Work = W' + CP × time
    
    Ou equivalentemente:
    Power = W'/time + CP
    
    Args:
        efforts: Lista de (time_sec, power_watts) - esforços máximos conhecidos
        method: '2-parameter' (padrão) ou '3-parameter' (com Pmax)
    
    Returns:
        CriticalPowerModel ou None se dados insuficientes
    """
    if len(efforts) < 2:
        return None  # Precisa de pelo menos 2 pontos
    
    # Filtra esforços válidos (power > 0, time > 0)
    valid_efforts = [(t, p) for t, p in efforts if t > 0 and p > 0]
    
    if len(valid_efforts) < 2:
        return None
    
    # Método: Regressão linear de Power vs 1/time
    # P = CP + W' × (1/t)
    # y = a + bx, onde y=P, x=1/t, a=CP, b=W'
    
    x_values = []  # 1/t
    y_values = []  # P
    
    for time_sec, power in valid_efforts:
        x_values.append(1.0 / time_sec)
        y_values.append(power)
    
    # Regressão linear simples
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    
    # Coeficientes
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        return None
    
    w_prime = (n * sum_xy - sum_x * sum_y) / denominator
    cp = (sum_y - w_prime * sum_x) / n
    
    # Calcula R² (coeficiente de determinação)
    y_mean = sum_y / n
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)
    
    # Predições
    predictions = [cp + w_prime * x for x in x_values]
    ss_res = sum((y - pred) ** 2 for y, pred in zip(y_values, predictions))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Validação: CP deve ser positivo, W' deve ser positivo
    if cp <= 0 or w_prime <= 0:
        return None
    
    return CriticalPowerModel(
        cp=cp,
        w_prime=w_prime,
        r_squared=max(0, min(1, r_squared))
    )


def calculate_critical_power_from_power_curve(
    power_curve: List[PowerCurvePoint],
    min_duration: int = 120,   # 2min
    max_duration: int = 1200  # 20min
) -> Optional[CriticalPowerModel]:
    """
    Calcula CP a partir da Power Curve.
    
    Usa pontos entre 2-20 minutos (faixa ótima para CP).
    
    Args:
        power_curve: Lista de PowerCurvePoint
        min_duration: Duração mínima (segundos)
        max_duration: Duração máxima (segundos)
    
    Returns:
        CriticalPowerModel ou None
    """
    # Filtra pontos na faixa ideal para CP
    efforts = [
        (p.duration_sec, p.power)
        for p in power_curve
        if min_duration <= p.duration_sec <= max_duration
    ]
    
    if len(efforts) < 2:
        return None
    
    return calculate_critical_power(efforts)


# =============================================================================
# MÉTRICAS AVANÇADAS
# =============================================================================

def calculate_variability_index(
    normalized_power: float,
    average_power: float
) -> float:
    """
    Calcula Variability Index (VI).
    
    VI = NP / AVG
    
    Interpretação:
    - VI < 1.05: Muito uniforme (contrarrelógio, solo)
    - VI 1.05-1.10: Moderado (critérium)
    - VI > 1.10: Variável (montanha, MTB)
    
    Args:
        normalized_power: Potência normalizada (NP)
        average_power: Potência média (AVG)
    
    Returns:
        Variability Index
    """
    if average_power <= 0:
        return 0.0
    
    return normalized_power / average_power


def calculate_efficiency_factor(
    normalized_power: float,
    average_hr: float
) -> float:
    """
    Calcula Efficiency Factor (EF).
    
    EF = NP / HR
    
    Usado para tracking de eficiência aeróbia ao longo do tempo.
    EF aumentando = fitness aeróbio melhorando.
    
    Args:
        normalized_power: Potência normalizada (W)
        average_hr: Frequência cardíaca média (bpm)
    
    Returns:
        Efficiency Factor (W/bpm)
    """
    if average_hr <= 0:
        return 0.0
    
    return normalized_power / average_hr


def calculate_intensity_factor(
    normalized_power: float,
    ftp: float
) -> float:
    """
    Calcula Intensity Factor (IF).
    
    IF = NP / FTP
    
    Interpretação:
    - IF = 1.0: Exatamente no FTP
    - IF > 1.0: Acima do FTP
    - IF < 1.0: Abaixo do FTP
    
    Args:
        normalized_power: Potência normalizada
        ftp: Functional Threshold Power
    
    Returns:
        Intensity Factor
    """
    if ftp <= 0:
        return 0.0
    
    return normalized_power / ftp


def calculate_decoupling(
    first_half_ef: float,
    second_half_ef: float
) -> float:
    """
    Calcula Aerobic Decoupling (Pwr:HR).
    
    Decoupling = (EF_inicial - EF_final) / EF_inicial × 100
    
    Interpretação:
    - < 5%: Excelente endurance base
    - 5-10%: Adequado
    - > 10%: Precisa trabalhar endurance base
    
    Args:
        first_half_ef: Efficiency Factor da primeira metade
        second_half_ef: Efficiency Factor da segunda metade
    
    Returns:
        Decoupling (%)
    """
    if first_half_ef <= 0:
        return 0.0
    
    decoupling = ((first_half_ef - second_half_ef) / first_half_ef) * 100
    return decoupling


# =============================================================================
# PEAK PERFORMANCES (PERSONAL RECORDS)
# =============================================================================

def find_peak_performances(
    power_data: List[float],
    standard_durations: List[int] = None
) -> Dict[str, float]:
    """
    Encontra melhores esforços (Personal Records) para durações padrão.
    
    Args:
        power_data: Stream de potência (W)
        standard_durations: Durações para verificar
    
    Returns:
        Dict com PRs (ex: {'1min': 350, '5min': 300, ...})
    """
    if standard_durations is None:
        standard_durations = [5, 60, 300, 600, 1200, 3600]  # 5s, 1min, 5min, 10min, 20min, 60min
    
    prs = {}
    
    for duration in standard_durations:
        if duration > len(power_data):
            continue
        
        max_power = 0.0
        for i in range(len(power_data) - duration + 1):
            avg = sum(power_data[i:i+duration]) / duration
            max_power = max(max_power, avg)
        
        if max_power > 0:
            key = f"{duration}s" if duration < 60 else f"{duration//60}min"
            prs[key] = round(max_power, 1)
    
    return prs
