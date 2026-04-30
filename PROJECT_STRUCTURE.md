# Estrutura do Projeto - Fitness Metrics Dashboard

**Data da organização:** 2026-04-27

---

## 📁 Estrutura Atual

```
Developer/
│
├── 📄 Arquivos na Raiz (7 arquivos essenciais)
│   ├── app.py              # Entry point Dash (5,378 linhas)
│   ├── calculations.py     # Cálculos legados (compatibilidade)
│   ├── storage.py          # Persistência legada (compatibilidade)
│   ├── config.py           # Config simples (compatibilidade)
│   ├── utils.py            # Utils legado (compatibilidade)
│   └── *.md               # Documentação
│
├── 📁 modules/            # Módulos organizados (24 arquivos)
│   ├── pages/             # UI Components (2 arquivos)
│   │   ├── __init__.py
│   │   ├── details_page.py
│   │   └── wellness_page.py
│   │
│   ├── services/          # Application Services (3 arquivos)
│   │   ├── __init__.py
│   │   ├── ai_chat.py
│   │   ├── alerts_system.py
│   │   └── pdf_reports.py
│   │
│   ├── analyzers/         # Data Analysis (7 arquivos)
│   │   ├── __init__.py
│   │   ├── power_analysis.py
│   │   ├── power_pace_analysis.py
│   │   ├── race_analysis.py
│   │   ├── race_predictor.py
│   │   ├── swim_analysis.py
│   │   ├── training_planner.py
│   │   └── training_zones.py
│   │
│   ├── infra/             # Infrastructure (2 arquivos)
│   │   ├── __init__.py
│   │   ├── cache_manager.py
│   │   └── garmin_enhanced.py
│   │
│   └── callbacks/         # Dash Callbacks (6 arquivos) ✅ NOVO
│       ├── __init__.py
│       ├── registry.py
│       ├── export_callbacks.py
│       ├── config_callbacks.py
│       ├── calendar_callbacks.py
│       ├── zones_callbacks.py
│       └── chat_callbacks.py
│
├── 📁 Nova Arquitetura (Clean Architecture)
│   ├── config/            # Constantes e settings
│   ├── domain/            # Regras de negócio puras
│   ├── services/          # Orquestração
│   ├── repositories/      # Persistência com interfaces
│   ├── utils/             # Funções utilitárias
│   └── tests/             # Testes automatizados
│
├── 📁 legacy/             # Backups do código original
│   ├── app_original.py
│   ├── calculations_original.py
│   └── storage_original.py
│
└── 📁 .windsurf/          # Agentes e Workflows
    ├── agents/            # 6 agentes especializados
    └── workflows/         # 9 workflows
```

---

## 📊 Métricas de Organização

### Antes vs Depois

| Aspecto | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **Arquivos na Raiz** | 19 | 7 | **63%** |
| **Linhas na Raiz** | ~5,400 | ~5,400 | (entry point mantido) |
| **Pastas organizadas** | 0 | 4 modules/ | **Nova** |
| **Total de arquivos** | 19 | 25 | (+6 organizados) |

### Distribuição dos Arquivos

```
Raiz:                    7 arquivos (28%)
  ├── Essenciais:        4 arquivos (entry points)
  └── Compatibilidade:   3 arquivos (legado)

modules/:                18 arquivos (72%)
  ├── pages/             2 arquivos (UI)
  ├── services/          3 arquivos (lógica)
  ├── analyzers/         7 arquivos (análise)
  └── infra/             2 arquivos (infra)

Nova Arquitetura:        16 arquivos
  ├── domain/            3 arquivos
  ├── services/          2 arquivos
  ├── repositories/      4 arquivos
  ├── config/            3 arquivos
  ├── utils/             2 arquivos
  └── tests/             4 arquivos
```

---

## 🎯 Resultado

### ✅ Raiz Limpo
- Apenas **7 arquivos** na raiz (vs 19 antes)
- **Entry points claros**: `app.py` é o main
- **Compatibilidade**: `calculations.py`, `storage.py` mantidos

### ✅ Organização Funcional
- `modules/pages/` - UI e componentes visuais
- `modules/services/` - Lógica de aplicação
- `modules/analyzers/` - Análise de dados fitness
- `modules/infra/` - Cache e integrações

### ✅ Nova Arquitetura Preservada
- `domain/` - Cálculos puramente testados
- `services/` - Orquestração moderna
- `repositories/` - Persistência com interfaces
- `tests/` - 31 testes passando

---

## 🔄 Imports Atualizados

### Em `app.py`:
```python
# Antes
from ai_chat import FitnessAI
from details_page import render_details
from cache_manager import get_cached

# Depois
from modules.services.ai_chat import FitnessAI
from modules.pages.details_page import render_details
from modules.infra.cache_manager import get_cached
```

---

## 🚀 Status

- ✅ Estrutura `modules/` criada
- ✅ Arquivos movidos para pastas funcionais
- ✅ Imports atualizados em `app.py`
- ✅ `__init__.py` criados
- ✅ Código funcional (compatibilidade preservada)
- ✅ Documentação criada

**Pronto para uso!** A raiz está significativamente mais limpa e organizada.
