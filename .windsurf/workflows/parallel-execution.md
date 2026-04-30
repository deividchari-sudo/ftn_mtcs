---
description: Workflow de Execução Paralela - Orquestração de agentes e workflows em paralelo quando há independência de tarefas, maximizando velocidade sem perder qualidade.
---

# Workflow de Execução Paralela

## Objetivo
Executar múltiplos agentes ou workflows simultaneamente quando suas tarefas são independentes, reduzindo tempo total de entrega sem comprometer qualidade ou criar conflitos.

## Quando Usar Paralelismo

### ✅ Casos Adequados para Paralelo

1. **Backend + Frontend (após API contract)**
   - TechLead define API contract
   - Backend implementa API enquanto Frontend implementa UI com mocks
   - Integração acontece ao final

2. **Features Independentes**
   - Feature A: Dashboard de sono
   - Feature B: Análise de natação
   - Podem ser desenvolvidas simultaneamente

3. **Testes + Documentação**
   - QA escreve testes BDD
   - Tech Writer (ou Dev) documenta
   - Ambos usam os mesmos requisitos

4. **Análises Múltiplas**
   - Stakeholder valida cálculos de potência
   - PM valida métricas de negócio
   - Independentes, podem rodar juntos

5. **Bugfixes Independentes**
   - Bug 1: CSS no mobile
   - Bug 2: Cálculo de TSS
   - Não interferem entre si

### ❌ Casos que DEVEM ser Sequenciais

1. **Dependência de Dados/Decisões**
   - ❌ Discovery → Arquitetura (depende)
   - ❌ Backend API → Frontend (depende de contrato)
   - ❌ Implementação → QA E2E (precisa de código)

2. **Mesmo Componente/Arquivo**
   - ❌ Dois devs no mesmo arquivo
   - ❌ Refatoração + Feature no mesmo módulo

3. **Decisões que Afetam Outros**
   - ❌ TechLead muda arquitetura enquanto Backend coda
   - ❌ PM muda requisitos durante desenvolvimento

## Modelos de Paralelismo

### Modelo 1: Divergir-Convergir (Fork-Join)

```
         ┌─→ [Agente A] ─┐
         │               │
[Start] ─┼─→ [Agente B] ─┼→ [Integração/Sync] → [Final]
         │               │
         └─→ [Agente C] ─┘
```

**Uso**: Várias análises independentes que convergem para decisão
**Exemplo**: Análise técnica, de negócio e de usuário para nova feature

### Modelo 2: Pipeline com Paralelismo

```
[Fase 1] → [Fase 2] ─┬─→ [Fase 3A] ─┐
   (seq)     (seq)    │              ├→ [Fase 4] → [Fase 5]
                      └─→ [Fase 3B] ─┘
                        (paralelo)
```

**Uso**: Fases sequenciais com paralelismo em pontos específicos
**Exemplo**: Design → API Contract → Backend + Frontend (paralelo) → Integração → QA

### Modelo 3: Swarm (Múltiplos Agentes Similares)

```
              ┌─→ [Dev 1: Task A] ─┐
[Decomposition]┼─→ [Dev 2: Task B] ├→ [Integration]
              ┼─→ [Dev 3: Task C] │
              └─→ [Dev 4: Task D] ─┘
```

**Uso**: Grande tarefa dividida em subtarefas independentes
**Exemplo**: Refatoração de múltiplos módulos, cada um por um dev

## Implementação de Paralelismo

### Fase 1: Análise de Dependências [Orchestrator]

```
Tarefa A: Implementar API de atividades
├─ Input: API Contract
├─ Output: Endpoints funcionais
└─ Dependências: [TechLead: API Contract]

Tarefa B: Implementar Dashboard de atividades
├─ Input: Mock data + Design specs
├─ Output: UI components
└─ Dependências: [TechLead: API Contract, PM: Design specs]

Tarefa C: Escrever testes BDD
├─ Input: Critérios de aceitação
├─ Output: Feature files
└─ Dependências: [PM: Critérios de aceitação]

Análise: B e C são independentes, podem rodar em paralelo
         A e B dependem do mesmo input (API Contract)
         → Executar TechLead primeiro, depois A+B+C em paralelo
```

### Fase 2: Sincronização de Handoffs

**Problema**: Como garantir que agente B receba output do agente A?

**Soluções**:

#### Opção A: Handoff Explícito (Padrão)
```
Agente A produz → Orchestrator coleta → Agente B consome
```

#### Opção B: Shared Context
```
Contexto compartilhado entre agentes paralelos:
- API Contract (read-only)
- Design specs (read-only)
- Requisitos (read-only)
```

#### Opção C: Event-Driven
```
Agente A emite: "API v1 defined"
Agente B e C escutam e iniciam quando recebem
```

### Fase 3: Execução Paralela

```python
# Pseudocode de orquestração paralela
async def parallel_execution():
    # Fase sequencial: Preparação
    api_contract = await techlead_agent.define_api()
    
    # Fase paralela: Backend + Frontend + QA
    backend_task = backend_dev_agent.implement_api(api_contract)
    frontend_task = frontend_dev_agent.implement_ui(api_contract)
    qa_task = qa_agent.write_bdd_tests(api_contract)
    
    # Aguarda todas completarem
    backend_result, frontend_result, qa_result = await gather(
        backend_task, frontend_task, qa_task
    )
    
    # Fase sequencial: Integração
    integration_result = await integration_phase(
        backend_result, frontend_result
    )
    
    return integration_result
```

### Fase 4: Resolução de Conflitos

**Conflitos Potenciais**:
- Backend mudou API enquanto Frontend codava
- PM mudou requisitos durante desenvolvimento
- Dois agentes assumiram coisas diferentes

**Estratégias**:
1. **Imutabilidade**: Inputs não mudam durante execução paralela
2. **Versionamento**: API v1.0, mudanças vão para v1.1 (pós-release)
3. **Code Freeze**: Durante execução paralela, requisitos/API congelados
4. **Merge Points**: Sincronização obrigatória em pontos chave

## Exemplos Práticos

### Exemplo 1: Feature com Backend + Frontend Paralelo

```
[TechLead] API Contract
    │
    ├─→ [Backend] Implement API ─┐
    │                            │
    ├─→ [Frontend] Implement UI ─┼─→ [Integration] ─→ [QA]
    │                            │      (sync)        (e2e)
    └─→ [QA] BDD Scenarios ──────┘
```

**Tempo Total**:
- Sequencial: TechLead (1h) + Backend (4h) + Frontend (4h) + QA (2h) = **11h**
- Paralelo: TechLead (1h) + max(Backend, Frontend, QA) (4h) + Integration (1h) + QA E2E (1h) = **7h**
- **Economia: 4h (36%)**

### Exemplo 2: Análises Múltiplas para Decisão

```
[Input: Nova feature de plano de treino]
    │
    ├─→ [PM] Business Case ───────────┐
    │                                   │
    ├─→ [Stakeholder] Technical Specs ──┼─→ [Synthesis] ─→ [Decision]
    │                                   │   (Orchestrator)   (Go/No-Go)
    └─→ [TechLead] Feasibility ─────────┘
```

**Benefício**: Decisão mais rápida com múltiplas perspectivas simultâneas

### Exemplo 3: Refatoração de Múltiplos Módulos

```
[Analysis: 5 módulos precisam refatoração]
    │
    ├─→ [Backend Dev 1] Módulo A (auth) ─┐
    ├─→ [Backend Dev 2] Módulo B (calc) ─┤
    ├─→ [Backend Dev 1] Módulo C (api) ──┼─→ [Integration Tests]
    ├─→ [Backend Dev 2] Módulo D (db) ──┤
    └─→ [Backend Dev 1] Módulo E (cache) ┘
```

**Regras**:
- Módulos devem ser independentes (não compartilham estado)
- Cada módulo tem sua própria suite de testes
- Integration tests rodam após todos terminarem

## Implementação no Orchestrator

### Extensão do Orchestrator para Suportar Paralelismo

```yaml
# orchestrator-parallel-config.yaml
workflow: feature-development
mode: parallel-enabled

phases:
  - name: setup
    type: sequential
    agent: techlead-agent
    output: api_contract
    
  - name: implementation
    type: parallel
    branches:
      - name: backend
        agent: backend-dev-agent
        input: api_contract
        output: api_implementation
        
      - name: frontend
        agent: frontend-dev-agent
        input: api_contract
        output: ui_implementation
        
      - name: qa-prep
        agent: qa-agent
        input: api_contract
        output: test_suite
    
  - name: integration
    type: sequential
    depends_on: [backend, frontend]
    agent: qa-agent
    input: [api_implementation, ui_implementation]
    
  - name: final-qa
    type: sequential
    depends_on: [integration, qa-prep]
    agent: qa-agent
    input: [integrated_system, test_suite]
```

### Comando de Uso

```bash
# Modo paralelo automático (orchestrador detecta independência)
/windsurf parallel "Implementar feature de análise de potência"

# Modo paralelo explícito
/windsurf parallel-execution "Refatorar módulos A, B e C independentemente"

# Com configuração de dependências
/windsurf orchestrator "Desenvolver feature X" --parallel-mode=fork-join
```

## Métricas de Paralelismo

### Speedup
```
Speedup = Tempo Sequencial / Tempo Paralelo

Exemplo:
- Sequencial: 10h
- Paralelo: 6h
- Speedup: 1.67x (67% mais rápido)
```

### Eficiência
```
Eficiência = Speedup / Número de Agentes

Exemplo:
- Speedup: 1.67x
- Agentes: 2
- Eficiência: 83.5% (bom, <100% devido a overhead de sync)
```

### Overhead de Coordenação
```
Overhead = Tempo Paralelo - (Tempo Sequencial / Número de Agentes)

Exemplo:
- Tempo Paralelo: 6h
- Tempo Sequencial / N: 10h / 2 = 5h
- Overhead: 1h (integração, comunicação)
```

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Conflitos de merge | Média | Alto | Pequenos commits frequentes, branches feature-based |
| Requisitos mudam | Baixa | Alto | Freeze de requisitos durante execução paralela |
| Handoff mal documentado | Média | Médio | Templates obrigatórios de output |
| Integração complexa | Alta | Médio | Testes de contrato, CI/CD rigoroso |
| Comunicação insuficiente | Média | Médio | Daily syncs, documentação compartilhada |

## Checklist de Paralelismo

Antes de executar em paralelo:

- [ ] Dependências mapeadas e resolvidas
- [ ] Inputs claros e imutáveis para cada agente
- [ ] Outputs esperados definidos
- [ ] Pontos de sincronização identificados
- [ ] Estratégia de resolução de conflitos
- [ ] Testes de integração planejados
- [ ] Rollback plan se algo der errado
- [ ] Comunicação entre agentes estabelecida

## Padrões de Paralelismo Recomendados

### Padrão 1: Read-Only Shared Context
```
Contexto (read-only):
├── API Contract v1.0
├── Design Mockups
└── Requirements Document

Agente A ─┬─→ Leitura do Contexto ─→ Trabalho independente
          │
Agente B ─┘
```

### Padrão 2: Producer-Consumer
```
Agente A (Producer) → Queue → Agente B (Consumer)
                           → Agente C (Consumer)
```

### Padrão 3: Scatter-Gather
```
Input → [Splitter] → Tarefa 1 ─┐
                    Tarefa 2 ─┼→ [Aggregator] → Output
                    Tarefa 3 ─┘
```

## Exemplo Completo: Feature de Dashboard

```
[Start]
  │
  ▼
[PM] Define requisitos e KPIs ────────────────────┐
  │                                               │
  ▼                                               │
[TechLead] Design arquitetura e API contract ─────┼→ Contexto Compartilhado
  │                                               │    (imutável)
  ├─→ [Stakeholder] Valida métricas de display ─┘
  │
  ▼ (Fork)
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
▼             ▼             ▼             ▼
[Backend]   [Frontend]    [Backend]    [QA]
API         Dashboard     Cálculos     BDD Tests
de dados    Componente    agregados    
  │             │             │             │
  └─────────────┴─────────────┴─────────────┘
                    │
                    ▼ (Join)
            [Integration]
         Backend + Frontend
                    │
                    ▼
            [QA] E2E Tests
                    │
                    ▼
            [PM] Sign-off
                    │
                    ▼
               [Release]
```

**Agentes em Paralelo**: Backend, Frontend (componente), Backend (cálculos), QA (BDD)
**Speedup esperado**: 1.5x - 2x vs. sequencial

## Próximo Workflow

Após paralelismo bem-sucedido:
- Se conflitos encontrados: **bug-fix** ou **refactoring**
- Se integração complexa: **architecture-review**
- Se tudo OK: **release** ou próxima **sprint-planning**
