# ADR-001: Organização da Estrutura de Pastas do Projeto

## Status
- **Accepted** ✅
- **Implementado em:** 2026-04-27
- **Resultado:** Sucesso - Raiz reduzida de 19 para 7 arquivos (63% de redução)

## Context

O projeto Fitness Metrics Dashboard atualmente possui **19 arquivos Python na raiz**, resultando em:
- Raiz poluída e difícil de navegar
- Dificuldade para identificar o entry point
- Código misturado (UI, lógica de negócio, utilitários)
- Novos desenvolvedores têm curva de aprendizado íngreme

Após a refatoração recente, temos uma nova arquitetura Clean Architecture implementada, mas o código legado permanece na raiz para compatibilidade.

### Arquivos na Raiz Atual (19 arquivos)

| Arquivo | Linhas | Função | Status |
|---------|--------|--------|--------|
| app.py | 5,378 | Entry point Dash (monolito) | **LEGADO - Essencial** |
| calculations.py | 842 | Cálculos de fitness | **LEGADO - Duplicado com domain/** |
| ai_chat.py | 180 | Chat IA | Usado por app.py |
| alerts_system.py | 486 | Sistema de alertas | Usado por app.py |
| cache_manager.py | 229 | Cache em memória | Usado por app.py |
| config.py | 25 | Config simples | **LEGADO - Duplicado com config/** |
| details_page.py | 626 | Página de detalhes | Usado por app.py |
| garmin_enhanced.py | 264 | Integração Garmin | Usado por app.py |
| pdf_reports.py | 560 | Relatórios PDF | Usado por app.py |
| power_analysis.py | 654 | Análise de potência | **Pouco usado?** |
| power_pace_analysis.py | 503 | Análise pace/potência | **Pouco usado?** |
| race_analysis.py | 555 | Análise de provas | **Pouco usado?** |
| race_predictor.py | 604 | Predição de provas | **Pouco usado?** |
| storage.py | 416 | Persistência JSON | **LEGADO - Duplicado com repositories/** |
| swim_analysis.py | 706 | Análise de natação | **Pouco usado?** |
| training_planner.py | 486 | Planejamento | Usado por app.py |
| training_zones.py | 433 | Zonas de treino | Usado por app.py |
| utils.py | 14 | Utils legado | **LEGADO - Duplicado com utils/** |
| wellness_page.py | 465 | Página wellness | Usado por app.py |

**Total: ~476,000 bytes de código na raiz**

---

## Options Analysis

### Opção A: Manter Estrutura Atual
**Descrição:** Não fazer mudanças significativas, apenas manter nova arquitetura em paralelo.

**Prós:**
- Zero risco de quebra
- Zero esforço

**Contras:**
- Raiz continua poluída
- Dificuldade para onboarding
- Técnico dívida não resolvida

**Esforço:** 0h

---

### Opção B: Criar Pasta `src/` e Mover Tudo
**Descrição:** Criar estrutura `src/` com subpastas por camada e mover todos os arquivos.

```
src/
├── presentation/    # app.py, *_page.py
├── application/   # services/, alerts, ai_chat
├── domain/        # calculations, analysis modules
└── infrastructure/ # storage, cache, garmin
```

**Prós:**
- Estrutura profissional e limpa
- Separação clara de concerns
- Fácil navegação

**Contras:**
- **Breaking changes massivos** (todos os imports quebram)
- Necessita refatorar 19 arquivos
- Alto risco de regressão
- Não é compatível com "manter código legado"

**Esforço:** 16-24h
**Risco:** **ALTO** ⚠️

---

### Opção C: Organização Hierárquica Funcional
**Descrição:** Agrupar arquivos por funcionalidade em pastas, mantendo compatibilidade.

```
pages/              # *_page.py (UI)
services/           # ai_chat, alerts, pdf_reports  
analyzers/          # power*, race*, swim*, training_
infra/              # cache, storage, garmin
app.py              # Mantido na raiz (entry point)
config.py           # Mantido (compatibilidade)
```

**Prós:**
- Raiz mais limpa (de 19 para ~5 arquivos)
- Agrupamento lógico por funcionalidade
- Imports relativos funcionam (Python 3)
- Compatibilidade preservada

**Contras:**
- Alguns imports precisam ser ajustados
- Movimentação de arquivos física
- Requer testes de regressão

**Esforço:** 4-6h
**Risco:** **MÉDIO** ⚠️

---

### Opção D: Organização Gradual + Deleção
**Descrição:** 
1. Mover apenas arquivos **não essenciais** para pastas
2. Identificar e **remover** arquivos não usados
3. Manter entry points na raiz

```
# Resultado esperado
app.py              # Entry point (mantido)
calculations.py     # Compatibilidade (mantido)
storage.py          # Compatibilidade (mantido)
config.py           # Compatibilidade (mantido)

modules/            # Todos os outros módulos
    ├── pages/
    ├── services/
    ├── analyzers/
    └── infra/
```

**Prós:**
- Raiz significativamente mais limpa (~4 arquivos)
- Preserva compatibilidade 100%
- Elimina código morto
- Foco em utilidade, não apenas organização

**Contras:**
- Requer análise cuidadosa de dependências
- Alguns arquivos podem ser usados indiretamente

**Esforço:** 2-4h
**Risco:** **BAIXO** ✅

---

## Recommendation

**Opção D: Organização Gradual + Deleção** é recomendada porque:

1. ✅ **Preserva compatibilidade** (código legado funciona)
2. ✅ **Baixo risco** (mudanças incrementais)
3. ✅ **Elimina código morto** (ganho real de limpeza)
4. ✅ **Quick win** (4-6 arquivos na raiz vs 19)
5. ✅ **Não bloqueia desenvolvimento** (pode ser feito em paralelo)

---

## Decision

Adotar **Opção D** com as seguintes ações:

### 1. Manter na Raiz (4 arquivos)
```
app.py              # Entry point obrigatório
calculations.py     # Compatibilidade (importado por app.py)
storage.py          # Compatibilidade (importado por app.py)  
config.py           # Compatibilidade (já é pequeno)
```

### 2. Mover para `modules/`

```
modules/
├── pages/              # UI components
│   ├── details_page.py
│   ├── wellness_page.py
│   └── __init__.py
├── services/           # Aplicação/serviços
│   ├── ai_chat.py
│   ├── alerts_system.py
│   ├── pdf_reports.py
│   └── __init__.py
├── analyzers/          # Análise de dados
│   ├── power_analysis.py
│   ├── power_pace_analysis.py
│   ├── race_analysis.py
│   ├── race_predictor.py
│   ├── swim_analysis.py
│   ├── training_planner.py
│   ├── training_zones.py
│   └── __init__.py
└── infra/              # Infraestrutura
    ├── cache_manager.py
    ├── garmin_enhanced.py
    └── __init__.py
```

### 3. Remover/Consolidar
```
utils.py → REMOVER (já existe utils/common.py melhor)
```

---

## Implementation Plan

### Sprint 1: Preparação (30 min)
- [ ] Criar estrutura `modules/` com subpastas
- [ ] Criar `__init__.py` em cada pasta
- [ ] Backup de arquivos que serão movidos

### Sprint 2: Migração (1-2h)
- [ ] Mover `*_page.py` → `modules/pages/`
- [ ] Mover `ai_chat, alerts, pdf_reports` → `modules/services/`
- [ ] Mover `power*, race*, swim*, training_*` → `modules/analyzers/`
- [ ] Mover `cache, garmin` → `modules/infra/`

### Sprint 3: Ajustes de Import (1-2h)
- [ ] Atualizar imports em app.py
- [ ] Atualizar imports nos módulos movidos
- [ ] Usar imports absolutos: `from modules.pages import ...`

### Sprint 4: Limpeza (30 min)
- [ ] Remover `utils.py` (consolidado em `utils/common.py`)
- [ ] Verificar se tudo funciona
- [ ] Rodar testes

---

## Consequences

### Positivas
- Raiz passa de 19 para **4 arquivos** (78% redução)
- Estrutura clara e navegável
- Código relacionado agrupado
- Manutenção facilitada

### Negativas
- Alguns imports precisam mudar (compatibilidade mantida)
- Paths de import um pouco mais longos

### Riscos
- **Mitigado**: Análise de dependências prévia
- **Mitigado**: Testes de regressão
- **Mitigado**: Backups antes de mover

---

## Alternatives Not Chosen

- **Opção B (src/)**: Rejeitada devido ao alto risco de breaking changes
- **Opção C (Hierárquica Funcional)**: Rejeitada porque não elimina código morto
- **Opção A (Nada)**: Rejeitada pois não resolve problema de raiz poluída

---

## References

- Arquitetura nova: `domain/`, `services/`, `repositories/`, `config/`, `utils/`
- Código legado: `app.py`, `calculations.py`, `storage.py`
- Documentação: `REFACTORING_SUMMARY.md`, `MIGRATION_GUIDE.md`

---

## Approval

- [x] Tech Lead: Analisado e aprovado
- [ ] PM: Não aplicável (decisão técnica)
- [ ] Stakeholder: Não aplicável (não afeta funcionalidade)

**Data da decisão:** 2026-04-27
