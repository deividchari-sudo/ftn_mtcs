"""
Constantes centralizadas do aplicativo.

Todas as constantes que eram espalhadas pelos módulos devem estar aqui.
"""

# =============================================================================
# CONSTANTES DE TEMPO
# =============================================================================

# Constantes de tempo para médias móveis exponenciais (EMA) - TrainingPeaks standard
CTL_TIME_CONSTANT = 42  # dias para Chronic Training Load (Fitness)
ATL_TIME_CONSTANT = 7   # dias para Acute Training Load (Fatigue)

# =============================================================================
# CONSTANTES DE FC E TSS
# =============================================================================

# Multiplicadores de intensidade por zona de FC (TrainingPeaks hrTSS estimation)
# Baseado em: https://www.trainingpeaks.com/learn/articles/estimating-training-stress-score-tss/
HR_ZONE_TSS_PER_HOUR = {
    1: 55,   # Zone 1 (Recovery): ~55 TSS/hour
    2: 75,   # Zone 2 (Endurance): ~75 TSS/hour  
    3: 90,   # Zone 3 (Tempo): ~90 TSS/hour
    4: 100,  # Zone 4 (Threshold): 100 TSS/hour (by definition)
    5: 120,  # Zone 5 (VO2Max): ~120 TSS/hour
    6: 140,  # Zone 6 (Anaerobic): ~140 TSS/hour
}

# Constantes de gênero para cálculo TRIMP (Banister)
TRIMP_GENDER_MALE = {'k': 1.92, 'factor': 0.64}
TRIMP_GENDER_FEMALE = {'k': 1.67, 'factor': 0.86}

# =============================================================================
# CONSTANTES DE ZONAS DE TREINAMENTO
# =============================================================================

# Zonas de FC baseadas em % do LTHR (TrainingPeaks standard)
HR_ZONES_LTHR = {
    1: (0, 80),      # < 81% LTHR (Recovery)
    2: (81, 89),     # 81-89% LTHR (Endurance)
    3: (90, 93),     # 90-93% LTHR (Tempo)
    4: (94, 99),     # 94-99% LTHR (Threshold)
    5: (100, 102),   # 100-102% LTHR (VO2Max)
    6: (103, 106),   # 103-106% LTHR (VO2Max high)
}

# Zonas de potência (Coggan)
POWER_ZONES_FTP = {
    1: (0, 0.55),      # Active Recovery
    2: (0.56, 0.75),   # Endurance
    3: (0.76, 0.90),   # Tempo
    4: (0.91, 1.05),   # Threshold
    5: (1.06, 1.20),   # VO2Max
    6: (1.21, 1.50),   # Anaerobic
    7: (1.51, float('inf')),  # Neuromuscular
}

# =============================================================================
# CONSTANTES DE LOCALIZAÇÃO
# =============================================================================

MONTHS_PT_BR = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

# =============================================================================
# THRESHOLDS E LIMITES
# =============================================================================

# Limites para alertas de treinamento
TSB_FRESH = 25          # TSB > 25 = muito descansado (pode perder forma)
TSB_OPTIMAL = (5, 25)   # TSB 5-25 = pronto para competir
TSB_HEAVY = -10         # TSB < -10 = fadiga acumulando
TSB_OVERREACHING = -30  # TSB < -30 = risco de overtraining

CTL_EXCELLENT = 50
CTL_GOOD = 40
CTL_MODERATE = 30

ATL_HIGH = 80
ATL_MODERATE = 60
ATL_LOW = 40
