"""
Advanced Metrics - P3 Implementation

Funcionalidades de baixa prioridade para alcançar 90%+ paridade TrainingPeaks:
- TSS by Sport (PMC separado por modalidade)
- ACWR (Acute:Chronic Workload Ratio)
- Sleep/HRV Integration básica
- Season Planning (Annual Training Plan)
"""
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from domain.calculations import calculate_fitness_metrics, FitnessMetrics
from domain.models import ActivityType


# =============================================================================
# TSS BY SPORT - PMC SEPARADO POR MODALIDADE
# =============================================================================

@dataclass
class SportMetrics:
    """Métricas de fitness por esporte."""
    sport: str
    ctl: float  # Chronic Training Load
    atl: float  # Acute Training Load
    tsb: float  # Training Stress Balance
    daily_tss_history: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def get_fitness_trend(self, days: int = 7) -> str:
        """Retorna tendência de fitness (subindo/estável/caindo)."""
        if len(self.daily_tss_history) < days * 2:
            return "insufficient_data"
        
        recent = sum(tss for _, tss in self.daily_tss_history[-days:]) / days
        previous = sum(tss for _, tss in self.daily_tss_history[-days*2:-days]) / days
        
        diff = recent - previous
        if diff > 5:
            return "increasing"
        elif diff < -5:
            return "decreasing"
        else:
            return "stable"


@dataclass
class MultiSportPMC:
    """Performance Management Chart multi-esporte."""
    global_metrics: FitnessMetrics  # PMC geral (todos os esportes)
    sport_metrics: Dict[str, SportMetrics]  # PMC por esporte
    
    def get_sport_balance(self) -> Dict[str, float]:
        """
        Calcula balanceamento entre esportes.
        
        Retorna percentual de TSS por esporte.
        """
        total_tss = sum(
            sum(tss for _, tss in sport.daily_tss_history)
            for sport in self.sport_metrics.values()
        )
        
        if total_tss == 0:
            return {}
        
        balance = {}
        for sport_name, sport in self.sport_metrics.items():
            sport_tss = sum(tss for _, tss in sport.daily_tss_history)
            balance[sport_name] = (sport_tss / total_tss) * 100
        
        return balance
    
    def detect_imbalance(self, threshold: float = 60.0) -> List[str]:
        """
        Detecta desbalanceamento (um esporte dominante).
        
        Args:
            threshold: Limite percentual para alerta (default 60%)
        
        Returns:
            Lista de esportes acima do threshold
        """
        balance = self.get_sport_balance()
        return [sport for sport, pct in balance.items() if pct > threshold]


def calculate_pmc_by_sport(
    activities: List[Dict],
    sport_mapping: Dict[str, str] = None
) -> MultiSportPMC:
    """
    Calcula PMC separado por esporte.
    
    Args:
        activities: Lista de atividades com 'sport_type' e 'tss'
        sport_mapping: Mapeamento de tipos para nomes padronizados
                      (ex: {'cycling': 'Bike', 'running': 'Run'})
    
    Returns:
        MultiSportPMC com métricas gerais e por esporte
    """
    if sport_mapping is None:
        sport_mapping = {
            'cycling': 'Bike',
            'running': 'Run',
            'swimming': 'Swim',
            'strength_training': 'Strength',
            'other': 'Other'
        }
    
    # Separa TSS por esporte
    sport_daily_tss: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
    global_daily_tss: List[Tuple[datetime, float]] = []
    
    # Agrupa por data
    date_to_sport_tss: Dict[datetime, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    for activity in activities:
        # Extrai data
        date_str = activity.get('start_time') or activity.get('startTimeLocal')
        if isinstance(date_str, str):
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00').replace('+00:00', ''))
                date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            except:
                continue
        elif isinstance(date_str, datetime):
            date = date_str.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            continue
        
        # Extrai TSS
        tss = activity.get('tss', 0)
        if isinstance(tss, dict):
            tss = tss.get('value', 0)
        tss = float(tss) if tss else 0
        
        # Extrai tipo de esporte
        sport_type = activity.get('sport_type') or activity.get('activityType', {}).get('typeKey', 'other')
        sport_name = sport_mapping.get(sport_type, sport_mapping.get('other', 'Other'))
        
        # Acumula por data e esporte
        date_to_sport_tss[date][sport_name] += tss
    
    # Converte para listas
    all_dates = sorted(date_to_sport_tss.keys())
    
    for date in all_dates:
        daily_total = 0
        for sport, tss in date_to_sport_tss[date].items():
            sport_daily_tss[sport].append((date, tss))
            daily_total += tss
        global_daily_tss.append((date, daily_total))
    
    # Calcula métricas por esporte
    sport_metrics = {}
    for sport, daily_tss in sport_daily_tss.items():
        if len(daily_tss) >= 7:  # Precisa de pelo menos 7 dias
            metrics = calculate_fitness_metrics(daily_tss)
            if metrics:
                latest = metrics[-1]
                sport_metrics[sport] = SportMetrics(
                    sport=sport,
                    ctl=latest.ctl,
                    atl=latest.atl,
                    tsb=latest.tsb,
                    daily_tss_history=daily_tss
                )
    
    # Calcula métricas globais
    global_metrics_list = calculate_fitness_metrics(global_daily_tss)
    global_metrics = global_metrics_list[-1] if global_metrics_list else FitnessMetrics(
        date=datetime.now(), ctl=0, atl=0, tsb=0, daily_tss=0
    )
    
    return MultiSportPMC(
        global_metrics=global_metrics,
        sport_metrics=sport_metrics
    )


# =============================================================================
# ACWR - ACUTE:CHRONIC WORKLOAD RATIO
# =============================================================================

@dataclass
class ACWRResult:
    """Resultado do cálculo de ACWR."""
    acute_load: float      # Carga aguda (7 dias)
    chronic_load: float    # Carga crônica (28 dias)
    ratio: float           # ACWR
    risk_level: str        # Nível de risco
    recommendation: str    # Recomendação
    
    def is_in_sweet_spot(self) -> bool:
        """Verifica se está na zona ótima (0.8-1.3)."""
        return 0.8 <= self.ratio <= 1.3


def calculate_acwr(
    daily_tss: List[Tuple[datetime, float]],
    acute_days: int = 7,
    chronic_days: int = 28
) -> Optional[ACWRResult]:
    """
    Calcula Acute:Chronic Workload Ratio (ACWR).
    
    Fórmula: ACWR = Carga Aguda / Carga Crônica
    
    Zonas de risco (Gabbett, 2016):
    - < 0.8: Undertraining (risco de descondicionamento)
    - 0.8-1.3: Sweet Spot (ótimo, menor risco de lesão)
    - > 1.5: Alto risco de lesão (spike de carga)
    
    Args:
        daily_tss: Lista de (data, TSS)
        acute_days: Janela aguda (default 7 dias)
        chronic_days: Janela crônica (default 28 dias)
    
    Returns:
        ACWRResult ou None se dados insuficientes
    """
    if len(daily_tss) < chronic_days:
        return None
    
    # Ordena por data
    sorted_tss = sorted(daily_tss, key=lambda x: x[0])
    
    # Extrai valores TSS
    all_tss = [tss for _, tss in sorted_tss]
    
    # Calcula carga aguda (últimos N dias)
    acute_load = sum(all_tss[-acute_days:]) / acute_days
    
    # Calcula carga crônica (média dos últimos M dias)
    chronic_load = sum(all_tss[-chronic_days:]) / chronic_days
    
    if chronic_load == 0:
        return None
    
    # Calcula ratio
    ratio = acute_load / chronic_load
    
    # Determina nível de risco
    if ratio < 0.8:
        risk_level = "undertraining"
        recommendation = "Aumentar carga gradualmente para evitar descondicionamento."
    elif ratio <= 1.0:
        risk_level = "optimal_low"
        recommendation = "Zona ótima. Manter carga atual ou aumentar gradualmente."
    elif ratio <= 1.3:
        risk_level = "optimal_high"
        recommendation = "Zona ótima com progressão. Monitorar fadiga."
    elif ratio <= 1.5:
        risk_level = "caution"
        recommendation = "Atenção: Spike de carga. Priorizar recuperação."
    else:
        risk_level = "high_risk"
        recommendation = "ALERTA: Alto risco de lesão. Reduzir carga imediatamente!"
    
    return ACWRResult(
        acute_load=round(acute_load, 1),
        chronic_load=round(chronic_load, 1),
        ratio=round(ratio, 2),
        risk_level=risk_level,
        recommendation=recommendation
    )


def calculate_acwr_by_sport(
    activities: List[Dict]
) -> Dict[str, ACWRResult]:
    """
    Calcula ACWR separado por esporte.
    
    Returns:
        Dict com ACWR de cada esporte
    """
    # Separa atividades por esporte
    sport_activities: Dict[str, List[Dict]] = defaultdict(list)
    
    for activity in activities:
        sport_type = activity.get('sport_type') or activity.get('activityType', {}).get('typeKey', 'other')
        sport_activities[sport_type].append(activity)
    
    # Calcula ACWR para cada esporte
    acwr_by_sport = {}
    for sport, acts in sport_activities.items():
        # Extrai daily TSS
        daily_tss = []
        for act in acts:
            date_str = act.get('start_time') or act.get('startTimeLocal')
            if isinstance(date_str, str):
                try:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00').replace('+00:00', ''))
                except:
                    continue
            elif isinstance(date_str, datetime):
                date = date_str
            else:
                continue
            
            tss = act.get('tss', 0)
            if isinstance(tss, dict):
                tss = tss.get('value', 0)
            tss = float(tss) if tss else 0
            
            daily_tss.append((date, tss))
        
        if len(daily_tss) >= 28:
            acwr = calculate_acwr(daily_tss)
            if acwr:
                acwr_by_sport[sport] = acwr
    
    return acwr_by_sport


# =============================================================================
# SLEEP/HRV INTEGRATION BÁSICA
# =============================================================================

@dataclass
class WellnessMetrics:
    """Métricas de bem-estar e recuperação."""
    date: datetime
    sleep_hours: float
    sleep_quality: int  # 1-5
    hrv_rmssd: Optional[float]  # ms
    hrv_score: Optional[int]  # 1-10 (relativo à baseline)
    resting_hr: Optional[int]
    fatigue_score: Optional[int]  # 1-10
    soreness_score: Optional[int]  # 1-10
    stress_score: Optional[int]  # 1-10
    
    def get_readiness_score(self) -> int:
        """
        Calcula readiness score (0-100) para treino.
        
        Baseado em HRV, sono e fadiga subjetiva.
        """
        score = 50  # Base
        
        # HRV (40% do peso)
        if self.hrv_score:
            score += (self.hrv_score - 5) * 4  # -20 a +20
        
        # Sono (30% do peso)
        if self.sleep_hours > 0:
            sleep_score = min(self.sleep_hours / 8 * 15, 15)  # 0-15
            score += sleep_score
        
        if self.sleep_quality > 0:
            score += (self.sleep_quality - 3) * 3  # -6 a +6
        
        # Fadiga (30% do peso)
        if self.fatigue_score:
            score -= (self.fatigue_score - 5) * 3  # -15 a +15
        
        return max(0, min(100, int(score)))
    
    def get_recommendation(self) -> str:
        """Recomendação baseada em readiness."""
        readiness = self.get_readiness_score()
        
        if readiness >= 80:
            return "Pronto para treino intenso ou prova."
        elif readiness >= 60:
            return "Bom para treino moderado. Evitar máximos."
        elif readiness >= 40:
            return "Priorizar recuperação. Treino leve ou descanso."
        else:
            return "Descanso ativo recomendado. Verificar sinais de overtraining."


class WellnessTracker:
    """Tracker de métricas de bem-estar."""
    
    def __init__(self):
        self.metrics_history: List[WellnessMetrics] = []
        self.hrv_baseline: Optional[float] = None
    
    def add_metric(self, metric: WellnessMetrics):
        """Adiciona métrica diária."""
        self.metrics_history.append(metric)
        self.metrics_history.sort(key=lambda x: x.date)
        
        # Atualiza baseline de HRV (média dos últimos 7 dias)
        self._update_hrv_baseline()
    
    def _update_hrv_baseline(self):
        """Calcula baseline de HRV."""
        recent_hrv = [
            m.hrv_rmssd for m in self.metrics_history[-7:]
            if m.hrv_rmssd is not None
        ]
        
        if len(recent_hrv) >= 3:
            self.hrv_baseline = sum(recent_hrv) / len(recent_hrv)
    
    def get_hrv_trend(self, days: int = 7) -> str:
        """Retorna tendência de HRV."""
        if len(self.metrics_history) < days * 2:
            return "insufficient_data"
        
        recent = [
            m.hrv_rmssd for m in self.metrics_history[-days:]
            if m.hrv_rmssd is not None
        ]
        previous = [
            m.hrv_rmssd for m in self.metrics_history[-days*2:-days]
            if m.hrv_rmssd is not None
        ]
        
        if not recent or not previous:
            return "insufficient_data"
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        diff_percent = ((recent_avg - previous_avg) / previous_avg) * 100
        
        if diff_percent > 5:
            return "increasing_good"  # HRV subindo = recuperação melhor
        elif diff_percent < -10:
            return "decreasing_warning"  # HRV caindo = fadiga acumulada
        else:
            return "stable"
    
    def detect_overtraining_risk(self) -> bool:
        """
        Detecta sinais de risco de overtraining.
        
        Sinais:
        - HRV caindo consistentemente
        - FC de repouso aumentando
        - Sono ruim + fadiga alta
        """
        if len(self.metrics_history) < 7:
            return False
        
        recent = self.metrics_history[-7:]
        
        # HRV caindo
        hrv_values = [m.hrv_rmssd for m in recent if m.hrv_rmssd]
        if len(hrv_values) >= 5:
            if hrv_values[-1] < hrv_values[0] * 0.9:  # Queda de 10%
                # Verifica se FC de repouso subiu
                resting_hrs = [m.resting_hr for m in recent if m.resting_hr]
                if len(resting_hrs) >= 5:
                    if resting_hrs[-1] > resting_hrs[0] * 1.05:  # Subida de 5%
                        return True
        
        # Sono ruim + fadiga alta
        bad_sleep_count = sum(1 for m in recent if m.sleep_quality <= 2)
        high_fatigue_count = sum(1 for m in recent if m.fatigue_score and m.fatigue_score >= 7)
        
        if bad_sleep_count >= 4 and high_fatigue_count >= 4:
            return True
        
        return False


# =============================================================================
# SEASON PLANNING - ANNUAL TRAINING PLAN (BÁSICO)
# =============================================================================

class TrainingPhase(Enum):
    """Fases de periodização."""
    BASE = "Base"                    # Endurance foundation
    BUILD = "Build"                  # Intensity increase
    PEAK = "Peak"                    # Race preparation
    RACE = "Race"                    # Competition
    TRANSITION = "Transition"        # Recovery/off-season


@dataclass
class SeasonPlan:
    """Plano anual de treinamento simplificado."""
    name: str
    start_date: datetime
    end_date: datetime
    phases: List[Tuple[TrainingPhase, datetime, datetime]] = field(default_factory=list)
    target_races: List[Tuple[str, datetime, str]] = field(default_factory=list)  # (nome, data, prioridade)
    
    def get_current_phase(self, date: datetime = None) -> Optional[TrainingPhase]:
        """Retorna fase atual."""
        if date is None:
            date = datetime.now()
        
        for phase, start, end in self.phases:
            if start <= date <= end:
                return phase
        return None
    
    def get_weekly_hours_target(self, date: datetime = None) -> int:
        """Retorna target de horas semanais para a fase."""
        phase = self.get_current_phase(date)
        
        targets = {
            TrainingPhase.BASE: 8,
            TrainingPhase.BUILD: 10,
            TrainingPhase.PEAK: 8,
            TrainingPhase.RACE: 6,
            TrainingPhase.TRANSITION: 4
        }
        
        return targets.get(phase, 6)
    
    def get_intensity_distribution(self, date: datetime = None) -> Dict[str, float]:
        """
        Retorna distribuição de intensidade (80/20 ou 70/30).
        
        Returns:
            Dict com % de tempo em cada zona
        """
        phase = self.get_current_phase(date)
        
        # 80/20 para base, 70/30 para build/peak
        if phase == TrainingPhase.BASE:
            return {
                "zone1_2": 80.0,  # Aeróbio fácil
                "zone3": 10.0,    # Tempo
                "zone4_5": 10.0   # Threshold/VO2Max
            }
        elif phase in [TrainingPhase.BUILD, TrainingPhase.PEAK]:
            return {
                "zone1_2": 70.0,
                "zone3": 15.0,
                "zone4_5": 15.0
            }
        elif phase == TrainingPhase.RACE:
            return {
                "zone1_2": 60.0,
                "zone3": 20.0,
                "zone4_5": 20.0
            }
        else:  # Transition
            return {
                "zone1_2": 90.0,
                "zone3": 10.0,
                "zone4_5": 0.0
            }


def create_season_plan(
    name: str,
    start_date: datetime,
    target_race_date: datetime,
    race_type: str = "marathon"
) -> SeasonPlan:
    """
    Cria plano anual simplificado.
    
    Estrutura típica:
    - Base: 12-16 semanas
    - Build: 6-8 semanas
    - Peak: 2-3 semanas
    - Race: 1 semana
    - Transition: 2-4 semanas
    
    Args:
        name: Nome do plano
        start_date: Data de início
        target_race_date: Data da prova alvo
        race_type: Tipo de prova (marathon, half, olympic, sprint)
    
    Returns:
        SeasonPlan configurado
    """
    # Calcula durações baseadas no tipo de prova
    if race_type == "marathon":
        base_weeks, build_weeks, peak_weeks = 16, 8, 3
    elif race_type == "half":
        base_weeks, build_weeks, peak_weeks = 12, 6, 2
    else:  # sprint/olympic tri
        base_weeks, build_weeks, peak_weeks = 8, 4, 2
    
    phases = []
    current_date = start_date
    
    # Base
    base_end = current_date + timedelta(weeks=base_weeks)
    phases.append((TrainingPhase.BASE, current_date, base_end))
    current_date = base_end
    
    # Build
    build_end = current_date + timedelta(weeks=build_weeks)
    phases.append((TrainingPhase.BUILD, current_date, build_end))
    current_date = build_end
    
    # Peak
    peak_end = current_date + timedelta(weeks=peak_weeks)
    phases.append((TrainingPhase.PEAK, current_date, peak_end))
    current_date = peak_end
    
    # Race (semana da prova)
    race_end = target_race_date + timedelta(days=1)
    phases.append((TrainingPhase.RACE, current_date, race_end))
    current_date = race_end
    
    # Transition (até o fim do ano ou 4 semanas)
    transition_end = min(
        current_date + timedelta(weeks=4),
        datetime(start_date.year, 12, 31)
    )
    phases.append((TrainingPhase.TRANSITION, current_date, transition_end))
    
    return SeasonPlan(
        name=name,
        start_date=start_date,
        end_date=transition_end,
        phases=phases,
        target_races=[(f"{race_type.title()}", target_race_date, "A")]
    )


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def calculate_weekly_summary(
    activities: List[Dict],
    week_start: datetime = None
) -> Dict:
    """
    Calcula resumo semanal de treinamento.
    
    Returns:
        Dict com totais da semana
    """
    if week_start is None:
        # Início desta semana (segunda)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=7)
    
    # Filtra atividades da semana
    week_activities = []
    for act in activities:
        date_str = act.get('start_time') or act.get('startTimeLocal')
        if isinstance(date_str, str):
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00').replace('+00:00', ''))
            except:
                continue
        elif isinstance(date_str, datetime):
            date = date_str
        else:
            continue
        
        if week_start <= date < week_end:
            week_activities.append(act)
    
    # Calcula totais
    total_duration = sum(act.get('duration', 0) for act in week_activities)
    total_distance = sum(act.get('distance', 0) for act in week_activities)
    total_tss = sum(
        float(act.get('tss', 0) if not isinstance(act.get('tss'), dict) else act.get('tss', {}).get('value', 0))
        for act in week_activities
    )
    
    # Por esporte
    by_sport = defaultdict(lambda: {'duration': 0, 'distance': 0, 'tss': 0, 'count': 0})
    for act in week_activities:
        sport = act.get('sport_type') or act.get('activityType', {}).get('typeKey', 'other')
        by_sport[sport]['duration'] += act.get('duration', 0)
        by_sport[sport]['distance'] += act.get('distance', 0)
        by_sport[sport]['tss'] += float(act.get('tss', 0) if not isinstance(act.get('tss'), dict) else act.get('tss', {}).get('value', 0))
        by_sport[sport]['count'] += 1
    
    return {
        'week_start': week_start,
        'week_end': week_end,
        'total_duration_hours': round(total_duration / 3600, 1),
        'total_distance_km': round(total_distance / 1000, 1),
        'total_tss': round(total_tss, 1),
        'activity_count': len(week_activities),
        'by_sport': dict(by_sport)
    }
