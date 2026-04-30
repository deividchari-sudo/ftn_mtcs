# Gap Analysis: Nosso Projeto vs TrainingPeaks

**Data:** 2026-04-27  
**Objetivo:** Identificar funcionalidades faltantes para alcançar paridade com TrainingPeaks

---

## 🎯 Funcionalidades TrainingPeaks (Core)

### ✅ JÁ IMPLEMENTADO

| Funcionalidade | Status | Localização | Cobertura Testes |
|----------------|--------|-------------|------------------|
| **TSS (Training Stress Score)** | ✅ Completo | `domain/calculations.py` | 40+ testes |
| **rTSS (Running TSS)** | ✅ Completo | `domain/calculations.py` | 25+ testes |
| **sTSS (Swimming TSS)** | ✅ Completo | `domain/calculations.py` | 20+ testes |
| **hrTSS (HR-based TSS)** | ✅ Completo | `domain/calculations.py` | 15+ testes |
| **CTL (Fitness)** | ✅ Completo | `domain/calculations.py` | 30+ testes |
| **ATL (Fatigue)** | ✅ Completo | `domain/calculations.py` | 30+ testes |
| **TSB (Form)** | ✅ Completo | `domain/calculations.py` | 30+ testes |
| **TRIMP** | ✅ Completo | `domain/calculations.py` | 10+ testes |
| **Zonas de FC** | ✅ Completo | `domain/calculations.py` | 15+ testes |
| **Zonas de Potência** | ✅ Parcial | `modules/analyzers/training_zones.py` | Básico |
| **Power Profile** | ✅ Parcial | `modules/analyzers/power_analysis.py` | Básico |
| **Análise de Natação (CSS)** | ✅ Completo | `modules/analyzers/swim_analysis.py` | 20+ testes |
| **Predição de Corrida** | ✅ Parcial | `modules/analyzers/race_predictor.py` | Básico |
| **Integração Garmin** | ✅ Completo | `modules/infra/garmin_enhanced.py` | Manual |

**Total: 14 funcionalidades core implementadas**

---

## 🔍 FUNCIONALIDADES FALTANTES (Gap Identificado)

### 🔴 ALTA PRIORIDADE (Core TrainingPeaks)

#### 1. **Power Curve / Power Profile Completo** 
**O que é:** Curva de potência do atleta (best efforts por duração)  
**Usado para:** Tracking de progressão, identificação de pontos fracos  
**Referência:** https://www.trainingpeaks.com/learn/articles/power-profile/

**Status atual:** Parcial (`power_analysis.py`)  
**Gap:** Não calcula MMP (Mean Maximal Power) para todas as durações (5s, 1min, 5min, 20min, etc)  
**Esforço:** 4-6h  
**Prioridade:** P0

#### 2. **Critical Power (CP) e W' (W-prime)**
**O que é:** Modelo fisiológico de potência crítica e capacidade anaeróbia  
**Usado para:** Predição de esforços, pacing em provas  
**Referência:** https://www.trainingpeaks.com/learn/articles/understanding-the-critical-power-model/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 6-8h  
**Prioridade:** P0

#### 3. **Variability Index (VI) e Intensity Factor (IF)**
**O que é:** Métricas de "suavidade" do treino (VI = NP/AVG)  
**Usado para:** Análise de quebra de ritmo, pacing  
**Referência:** https://www.trainingpeaks.com/learn/articles/what-is-variability-index/

**Status atual:** ❌ Não implementado  
**Gap:** Não calcula VI  
**Esforço:** 2-3h  
**Prioridade:** P1

#### 4. **Efficiency Factor (EF)**
**O que é:** NP / FC média (eficiência cardíaca)  
**Usado para:** Tracking de eficiência aeróbia  
**Referência:** https://www.trainingpeaks.com/learn/articles/efficiency-factor-decoupling/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 2-3h  
**Prioridade:** P1

#### 5. **Decoupling (Pwr:HR)**
**O que é:** Relação entre potência e FC durante treino longo  
**Usado para:** Identificar fadiga em treinos longos  
**Referência:** https://www.trainingpeaks.com/learn/articles/efficiency-factor-decoupling/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 4-6h  
**Prioridade:** P1

---

### 🟡 MÉDIA PRIORIDADE (Advanced Metrics)

#### 6. **Normalized Graded Pace (NGP)**
**O que é:** Pace ajustado por elevação (corrida trail)  
**Usado para:** Comparação justa de treinos em terreno variado  
**Referência:** https://www.trainingpeaks.com/learn/articles/normalized-graded-pace/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 4-6h  
**Prioridade:** P2

#### 7. **Running Effectiveness (RE)**
**O que é:** Velocidade / Potência (eficiência de corrida)  
**Usado para:** Tracking de eficiência de stride (com Stryd)  
**Referência:** https://www.trainingpeaks.com/learn/articles/running-effectiveness/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 3-4h  
**Prioridade:** P2

#### 8. **Time in Zones (Distribution)**
**O que é:** Distribuição de tempo em cada zona de FC/Potência  
**Usado para:** Análise de polarização do treino  
**Referência:** TrainingPeaks dashboard

**Status atual:** Parcial  
**Gap:** Calcula mas não persiste/exibe bem  
**Esforço:** 2-3h  
**Prioridade:** P2

#### 9. **Peak Performances (Best Efforts)**
**O que é:** Melhores esforços por duração (1min, 5min, 10min, etc)  
**Usado para:** Tracking de PRs, detecção de forma  
**Referência:** TrainingPeaks Personal Records

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 4-6h  
**Prioridade:** P2

#### 10. **Aerobic Decoupling ( aerobic efficiency)**
**O que é:** Quebra da relação potência/FC ao longo do tempo  
**Usado para:** Avaliar endurance base  
**Referência:** https://www.trainingpeaks.com/learn/articles/aerobic-decoupling/

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 3-4h  
**Prioridade:** P2

---

### 🟢 BAIXA PRIORIDADE (Nice to Have)

#### 11. **TSS por Sport (Modalidade)**
**O que é:** CTL/ATL/TSB separado por esporte (bike, run, swim)  
**Usado para:** Análise de desbalanceamento  
**Referência:** TrainingPeaks PMC by Sport

**Status atual:** ❌ Não implementado  
**Gap:** PMC é global apenas  
**Esforço:** 6-8h  
**Prioridade:** P3

#### 12. **Acute:Chronic Workload Ratio (ACWR)**
**O que é:** Ratio ATL/CTL (ou rolling 7d / 28d)  
**Usado para:** Prevenção de lesões (sweet spot 0.8-1.3)  
**Referência:** Research: Gabbett, 2016

**Status atual:** Indireto (ATL/CTL já temos)  
**Gap:** Não calcula ratio específico  
**Esforço:** 2-3h  
**Prioridade:** P3

#### 13. **Sleep, HRV, Wellness Tracking**
**O que é:** Métricas de recuperação e bem-estar  
**Usado para:** Análise de readiness para treino  
**Referência:** TrainingPeaks Wellness dashboard

**Status atual:** Parcial (`wellness_page.py`)  
**Gap:** Básico, não integrado com PMC  
**Esforço:** 8-10h  
**Prioridade:** P3

#### 14. **Fitness History / Season Planning**
**O que é:** Visualização de longo prazo e planejamento sazonal  
**Usado para:** Periodização anual  
**Referência:** TrainingPeaks Annual Training Plan

**Status atual:** ❌ Não implementado  
**Gap:** Zero implementação  
**Esforço:** 10-12h  
**Prioridade:** P3

---

## 📊 Resumo do Gap

### Por Prioridade

| Prioridade | Quantidade | Esforço Estimado |
|------------|------------|------------------|
| 🔴 P0 (Crítico) | 2 funcionalidades | 10-14h |
| 🟡 P1 (Alta) | 3 funcionalidades | 8-12h |
| 🟠 P2 (Média) | 5 funcionalidades | 17-23h |
| 🟢 P3 (Baixa) | 4 funcionalidades | 26-33h |

**Total:** 14 funcionalidades faltantes | **Esforço Total:** 61-82h

### Por Categoria

| Categoria | Implementado | Faltando | % Completo |
|-----------|--------------|----------|------------|
| Métricas Básicas (TSS/CTL/ATL) | 6 | 0 | 100% ✅ |
| Métricas Avançadas (CP/VI/EF) | 0 | 4 | 0% 🔴 |
| Análise de Potência | 2 | 3 | 40% 🟡 |
| Análise de Corrida | 2 | 3 | 40% 🟡 |
| Recovery/Wellness | 1 | 2 | 33% 🟠 |
| Planejamento | 0 | 2 | 0% 🔴 |

---

## 🎯 Recomendação de Implementação

### Fase 1 (P0 - Core): 10-14h
1. ✅ **Power Curve / MMP** (4-6h)
2. ✅ **Critical Power + W'** (6-8h)

### Fase 2 (P1 - Advanced): 8-12h  
3. ✅ **Variability Index** (2-3h)
4. ✅ **Efficiency Factor** (2-3h)
5. ✅ **Decoupling** (4-6h)

### Fase 3 (P2 - Nice): 17-23h
6. ⏳ **NGP** (4-6h)
7. ⏳ **Running Effectiveness** (3-4h)
8. ⏳ **Time in Zones** (2-3h)
9. ⏳ **Peak Performances** (4-6h)
10. ⏳ **Aerobic Decoupling** (3-4h)

### Fase 4 (P3 - Future): 26-33h
11. ⏳ **TSS by Sport** (6-8h)
12. ⏳ **ACWR** (2-3h)
13. ⏳ **Sleep/HRV Integration** (8-10h)
14. ⏳ **Season Planning** (10-12h)

---

## 🏆 Meta de Paridade

Para alcançar **80% de paridade** com TrainingPeaks (nível suficiente para atletas sérios):

**Necessário implementar:**
- ✅ Todos os P0 (2 funcionalidades)
- ✅ Todos os P1 (3 funcionalidades)  
- 🟡 60% dos P2 (3 de 5 funcionalidades)

**Total:** 8 funcionalidades | **Esforço:** 35-49h | **Prazo Estimado:** 1-2 semanas

---

## 📚 Referências

- TrainingPeaks Education: https://www.trainingpeaks.com/learn/
- Power Profile: https://www.trainingpeaks.com/learn/articles/power-profile/
- Critical Power: https://www.trainingpeaks.com/learn/articles/understanding-the-critical-power-model/
- VI & IF: https://www.trainingpeaks.com/learn/articles/what-is-variability-index/
- EF & Decoupling: https://www.trainingpeaks.com/learn/articles/efficiency-factor-decoupling/

---

**Próximo passo:** Priorizar P0 e iniciar implementação
