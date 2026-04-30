"""
Modelos de domínio - dataclasses para entidades principais.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum


class ActivityType(Enum):
    """Tipos de atividade suportados."""
    CYCLING = "cycling"
    RUNNING = "running"
    SWIMMING = "swimming"
    STRENGTH = "strength"
    OTHER = "other"


class TSSType(Enum):
    """Tipos de cálculo de TSS."""
    CYCLING_POWER = "cycling_power"
    CYCLING_HR = "cycling_hr"
    RUNNING_PACE = "running_pace"
    RUNNING_HR = "running_hr"
    SWIMMING_PACE = "swimming_pace"
    SWIMMING_HR = "swimming_hr"
    STRENGTH = "strength"
    HR_ESTIMATED = "hr_estimated"
    DURATION_ESTIMATED = "duration_estimated"
    UNKNOWN = "unknown"


@dataclass
class Activity:
    """Representa uma atividade de treino."""
    id: str
    type: ActivityType
    start_time: datetime
    duration: timedelta
    
    # Dados opcionais
    distance_meters: Optional[float] = None
    avg_power: Optional[float] = None
    normalized_power: Optional[float] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    avg_speed: Optional[float] = None  # m/s
    
    # Dados brutos originais
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.duration.total_seconds() < 0:
            raise ValueError("Duration cannot be negative")


@dataclass
class TSSResult:
    """Resultado do cálculo de TSS."""
    value: float
    type: TSSType
    intensity_factor: Optional[float] = None
    normalized_power: Optional[float] = None
    
    def __post_init__(self):
        """Garante TSS não negativo."""
        if self.value < 0:
            self.value = 0.0


@dataclass
class FitnessMetrics:
    """Métricas de fitness (CTL, ATL, TSB)."""
    date: datetime
    ctl: float  # Chronic Training Load (Fitness)
    atl: float  # Acute Training Load (Fatigue)
    tsb: float  # Training Stress Balance (Form)
    daily_tss: float = 0.0
    
    @property
    def fitness(self) -> float:
        """Alias para CTL."""
        return self.ctl
    
    @property
    def fatigue(self) -> float:
        """Alias para ATL."""
        return self.atl
    
    @property
    def form(self) -> float:
        """Alias para TSB."""
        return self.tsb
    
    def get_status(self) -> str:
        """Retorna status baseado nos valores."""
        if self.tsb > 25:
            return "very_fresh"  # Muito descansado
        elif self.tsb > 10:
            return "fresh"  # Descansado
        elif self.tsb > -10:
            return "neutral"  # Neutro
        elif self.tsb > -20:
            return "tired"  # Cansado
        else:
            return "very_tired"  # Muito cansado


@dataclass  
class PowerZone:
    """Zona de potência (Coggan)."""
    name: str
    number: int
    min_pct_ftp: float
    max_pct_ftp: float
    color: str
    description: str


@dataclass
class HeartRateZone:
    """Zona de frequência cardíaca."""
    name: str
    number: int
    min_pct_lthr: float
    max_pct_lthr: float
    color: str
    description: str
    tss_per_hour: int


@dataclass
class UserConfig:
    """Configurações do usuário."""
    ftp: float = 250.0
    threshold_pace_running: float = 300.0  # segundos/km
    threshold_pace_swimming: float = 100.0  # segundos/100m
    lthr: float = 170.0
    hr_max: float = 185.0
    hr_rest: float = 50.0
    gender: str = "male"
    
    def get_threshold_speed_running(self) -> float:
        """Retorna velocidade threshold em m/s."""
        if self.threshold_pace_running <= 0:
            return 0.0
        return 1000.0 / self.threshold_pace_running
