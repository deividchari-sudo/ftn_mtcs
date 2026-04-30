# Guia de Migração - Nova Arquitetura

**Versão**: 1.0  
**Data**: 2026-04-27

---

## 🚀 Como Usar a Nova Arquitetura

### Exemplo 1: Calcular TSS para uma Atividade

#### Antigo (ainda funciona)
```python
from calculations import compute_tss_variants, load_config

config = load_config()
workout = {
    'activityType': {'typeKey': 'cycling'},
    'duration': 3600,
    'averagePower': 200,
}

result = compute_tss_variants(workout, config)
tss = result.get('tss', 0)
```

#### Novo (recomendado)
```python
from services.calculations_service import CalculationsService
from domain.models import UserConfig

config = UserConfig(
    ftp=250,
    threshold_pace_running=300,
    threshold_pace_swimming=100,
    lthr=170
)

service = CalculationsService(config)

workout = {
    'activityType': {'typeKey': 'cycling'},
    'duration': 3600,
    'averagePower': 200,
}

result = service.calculate_tss(workout)
print(f"TSS: {result.value}")
print(f"Tipo: {result.type}")
print(f"IF: {result.intensity_factor}")
```

---

### Exemplo 2: Calcular Métricas de Fitness (CTL, ATL, TSB)

#### Antigo
```python
from calculations import calculate_fitness_metrics

daily_tss = [
    (datetime(2024, 1, 1), 100),
    (datetime(2024, 1, 2), 120),
    # ...
]

metrics = calculate_fitness_metrics(daily_tss)
```

#### Novo
```python
from services.calculations_service import CalculationsService
from domain.models import UserConfig
from datetime import datetime, timedelta

config = UserConfig(ftp=250, lthr=170)
service = CalculationsService(config)

# Preparar dados
daily_tss = [
    (datetime(2024, 1, 1), 100.0),
    (datetime(2024, 1, 2), 120.0),
    # ...
]

# Calcular
metrics = service.calculate_fitness_trends(daily_tss)

# Usar resultados
for m in metrics:
    print(f"Data: {m.date}")
    print(f"  CTL (Fitness): {m.ctl}")
    print(f"  ATL (Fatigue): {m.atl}")
    print(f"  TSB (Form): {m.tsb}")
    print(f"  Status: {m.get_status()}")
```

---

### Exemplo 3: Usar Repositories

#### Salvar Workouts
```python
from repositories.factory import create_workout_repository

# Criar repository (usa JSON por padrão)
repo = create_workout_repository()

# Salvar workout
workout = {
    'activityId': '12345',
    'activityType': {'typeKey': 'cycling'},
    'duration': 3600,
    'distance': 30000,
    'averagePower': 200,
}

repo.save(workout)

# Buscar todos
all_workouts = repo.get_all()

# Buscar por ID
workout = repo.get_by_id('12345')

# Buscar por período
from datetime import datetime, timedelta
start = datetime.now() - timedelta(days=7)
end = datetime.now()
recent = repo.get_by_date_range(start, end)
```

#### Salvar Métricas
```python
from repositories.factory import create_metrics_repository

repo = create_metrics_repository()

# Salvar métrica diária
metric = {
    'date': datetime.now().isoformat(),
    'ctl': 45.5,
    'atl': 62.3,
    'tsb': -16.8,
}

repo.save(metric)

# Buscar últimas 7 métricas
latest = repo.get_latest(7)
```

---

### Exemplo 4: Enriquecer Workouts com TSS (Batch)

```python
from services.calculations_service import CalculationsService
from domain.models import UserConfig
from repositories.factory import create_workout_repository

# Config
config = UserConfig(ftp=250, lthr=170)
service = CalculationsService(config)

# Carregar workouts
repo = create_workout_repository()
workouts = repo.get_all()

# Calcular TSS para todos
enriched = service.enrich_workouts_with_tss(workouts)

# enriched agora tem 'tss', 'tss_type', 'intensity_factor'
for w in enriched:
    print(f"{w['activityId']}: {w['tss']:.1f} TSS ({w['tss_type']})")

# Salvar de volta (opcional)
repo.save_many(enriched)
```

---

### Exemplo 5: Usar Models de Domínio Diretamente

```python
from domain.models import Activity, UserConfig, ActivityType
from domain.calculations import calculate_tss_for_activity
from datetime import datetime, timedelta

# Criar atividade manualmente
activity = Activity(
    id='manual-001',
    type=ActivityType.CYCLING,
    start_time=datetime.now(),
    duration=timedelta(hours=1, minutes=30),
    avg_power=210,
    normalized_power=215,
    avg_hr=155
)

# Config
config = UserConfig(ftp=250, lthr=170)

# Calcular TSS
result = calculate_tss_for_activity(activity, config)

print(f"TSS: {result.value}")
print(f"Tipo: {result.type.value}")
print(f"IF: {result.intensity_factor:.3f}")
```

---

### Exemplo 6: Usar Constants Centralizadas

```python
from config.constants import (
    CTL_TIME_CONSTANT,
    ATL_TIME_CONSTANT,
    HR_ZONE_TSS_PER_HOUR,
    MONTHS_PT_BR,
    POWER_ZONES_FTP,
)

# Usar constantes
print(f"CTL usa {CTL_TIME_CONSTANT} dias de média móvel")
print(f"Zona 4 de FC: {HR_ZONE_TSS_PER_HOUR[4]} TSS/h")

# Iterar sobre zonas de potência
for zone, (min_pct, max_pct) in POWER_ZONES_FTP.items():
    print(f"Zona {zone}: {min_pct*100:.0f}%-{max_pct*100:.0f}% FTP")
```

---

## 🧪 Rodar Testes

### Todos os testes
```bash
python -m pytest tests/ -v
```

### Testes unitários apenas
```bash
python -m pytest tests/unit/ -v
```

### Testes de integração
```bash
python -m pytest tests/integration/ -v
```

### Com cobertura
```bash
python -m pytest tests/ --cov=domain --cov=services --cov=repositories --cov-report=html
```

---

## 📁 Estrutura de Imports

### Domain Layer
```python
from domain.models import Activity, UserConfig, TSSResult, FitnessMetrics
from domain.calculations import (
    calculate_tss_cycling,
    calculate_rtss_running,
    calculate_stss_swimming,
    calculate_hrtss,
    calculate_fitness_metrics,
)
```

### Services Layer
```python
from services.calculations_service import CalculationsService
```

### Repositories Layer
```python
from repositories.factory import (
    create_workout_repository,
    create_metrics_repository,
    create_config_repository,
)
from repositories.interfaces import (
    WorkoutRepositoryInterface,
    MetricsRepositoryInterface,
)
```

### Config
```python
from config.constants import *
from config.settings import load_config, save_config
```

### Utils
```python
from utils.common import (
    parse_start_time,
    type_key,
    modality_bucket,
    safe_float,
    shift_month,
)
```

---

## 🔧 Configuração

### Configurações Padrão
```python
from domain.models import UserConfig

# Usar defaults
config = UserConfig()

# Ou customizar
config = UserConfig(
    ftp=280,                      # Seu FTP atual
    threshold_pace_running=280,   # 4:40/km
    threshold_pace_swimming=95,  # 1:35/100m
    lthr=175,
    hr_max=190,
    hr_rest=48,
)
```

### Salvar/Recuperar Configurações
```python
from repositories.factory import create_config_repository

repo = create_config_repository()

# Salvar
repo.save({
    'ftp': 280,
    'lthr': 175,
    'gender': 'male'
})

# Carregar
config_dict = repo.load()
```

---

## ⚡ Performance

### Batch Processing
Para processar muitos workouts, use sempre batch:

```python
# ✅ BOM: Batch
results = service.calculate_batch_tss(workouts_list)

# ❌ EVITAR: Loop individual
results = [service.calculate_tss(w) for w in workouts_list]  # Mais lento
```

### Lazy Loading
Repositories carregam dados sob demanda:

```python
repo = create_workout_repository()

# Não carrega nada ainda
workout = repo.get_by_id('123')  # Carrega apenas se necessário
```

---

## 🐛 Debugging

### Verificar Cálculos
```python
from domain.calculations import calculate_tss_cycling

# Debug step-by-step
duration = 3600
power = 210
ftp = 250

if __name__ == "__main__":
    # Manual calculation
    duration_hours = duration / 3600  # 1.0
    intensity_factor = power / ftp      # 0.84
    tss_manual = (intensity_factor ** 2) * duration_hours * 100
    
    print(f"Manual: {tss_manual}")
    
    # Function result
    tss_result = calculate_tss_cycling(duration, power, ftp)
    print(f"Function: {tss_result}")
    
    assert abs(tss_manual - tss_result) < 0.01
```

---

## 📚 Recursos

- **REFACTORING_SUMMARY.md**: Resumo completo da refatoração
- **REFACTORING_ANALYSIS.md**: Análise de code smells
- **REFACTORING_PLAN.md**: Plano detalhado de refatoração
- **tests/**: Suite completa de testes

---

## 💡 Dicas

1. **Sempre use UserConfig**: Centraliza todas as configurações do atleta
2. **Prefira Services**: Para operações complexas, use CalculationsService
3. **Use Domain para lógica pura**: Cálculos independentes de I/O
4. **Repositories para persistência**: Abstraia onde os dados são guardados
5. **Testes são documentação**: Veja `tests/unit/test_calculations.py` para exemplos

---

## 🤝 Compatibilidade

O código antigo (`calculations.py`, `app.py`, `storage.py`) continua funcionando!

A nova arquitetura é **opt-in**. Você pode migrar gradualmente:
1. Novas features: use nova arquitetura
2. Código existente: mantenha funcionando
3. Refatoração gradual: substitua quando conveniente

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se os testes passam: `python -m pytest tests/ -v`
2. Consulte os exemplos neste guia
3. Veja a documentação nos módulos (docstrings)
4. Compare com código legado em `legacy/`
