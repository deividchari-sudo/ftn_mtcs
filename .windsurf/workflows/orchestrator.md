---
description: Workflow Orquestrador - Analisa o input do usuário e direciona automaticamente para os workflows e agentes mais adequados de forma autônoma.
---

# Workflow Orquestrador (Auto-Router)

## Objetivo
Analisar a necessidade do usuário e direcionar automaticamente para o workflow ou agente mais adequado, orquestrando múltiplos agentes quando necessário.

## Trigger
- Qualquer request do usuário
- Input ambíguo ou que precisa de múltiplas especialidades
- "Me ajude com..." sem especificar agente ou workflow
- Contexto complexo envolvendo várias áreas

## Como Funciona

```
Input do Usuário
      ↓
[Análise de Intenção]
      ↓
┌─────────────────┐
│  Classificador  │ ← Determina tipo e complexidade
└─────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Seletor de Workflow/Agente(s)    │
│  • Simples → Agente único          │
│  • Complexo → Workflow estruturado │
│  • Multi-facetado → Orquestração   │
└─────────────────────────────────────┘
      ↓
[Execução Autônoma] → Orquestra agentes em sequência
      ↓
[Síntese de Resultados] → Entrega consolidada
```

## Lógica de Classificação

### 1. Análise de Intenção

O orquestrador analisa:
- **Ação solicitada**: criar, consertar, validar, decidir, implementar, analisar
- **Domínio**: negócio/product, técnico/esporte, código, arquitetura, teste
- **Complexidade**: simples, moderada, complexa
- **Dependências**: envolve múltiplas camadas ou especialidades?

### 2. Matriz de Decisão

| Padrão no Input | Complexidade | Direcionamento |
|----------------|--------------|----------------|
| "bug", "quebrado", "erro", "não funciona", "fix" | Simples/Média | `bug-fix` workflow |
| "novo", "feature", "criar", "implementar", "desenvolver" | Média/Alta | `discovery` → `feature-development` |
| "arquitetura", "decidir", "escolher tech", "migrar" | Média/Alta | `architecture-review` |
| "refatorar", "limpar código", "melhorar", "otimizar" | Média/Alta | `refactoring` |
| "sprint", "planejar", "backlog", "priorizar" | Simples/Média | `sprint-planning` |
| "lançar", "release", "deploy", "produção" | Simples/Média | `release` |
| "calcular", "fórmula", "métrica", "validar fisiologia" | Simples | `stakeholder-agent` |
| "KPI", "métrica de negócio", "priorizar", "PRD" | Simples | `pm-agent` |
| "como testar", "BDD", "cenario", "qualidade" | Simples | `qa-agent` |
| "API", "endpoint", "backend", "Python" | Simples | `backend-dev-agent` |
| "tela", "componente", "dashboard", "interface" | Simples | `frontend-dev-agent` |
| "DDD", "Clean Arch", "pattern", "design" | Simples | `techlead-agent` |

### 3. Detecção de Multi-Especialidade

Se o input envolve múltiplas áreas, o orquestrador ativa **modo orquestração**:

```
Input: "Quero criar uma feature de alerta de overtraining baseado em HRV e TSB"

Análise:
├── "criar feature" → Product Manager (escopo, valor)
├── "overtraining" → Stakeholder (definir thresholds científicos)
├── "HRV e TSB" → Stakeholder (validar métricas)
├── "alerta" → TechLead (arquitetura de notificações)
├── "implementar" → Backend (algoritmo de detecção)
└── "tela de alerta" → Frontend (interface)

Orquestração:
PM (discovery) → Stakeholder (specs) → TechLead (design) 
  → Backend (impl) → Frontend (impl) → QA (testes)
```

## Modes de Operação

### Mode 1: Single Agent (Simples)
**Quando usar**: Request clara, uma única especialidade

**Exemplos**:
- "Como calcular CTL?" → Stakeholder Agent
- "Implemente função de média móvel" → Backend Agent
- "Crie componente de gráfico" → Frontend Agent

**Execução**: Chama agente diretamente, retorna resultado

### Mode 2: Structured Workflow (Complexo Estruturado)
**Quando usar**: Request clara, processo definido

**Exemplos**:
- "Bug: cálculo de TSS errado" → `bug-fix` workflow
- "Nova feature de dashboard" → `feature-development` workflow
- "Quero refatorar o módulo de cálculos" → `refactoring` workflow

**Execução**: Segue workflow passo a passo

### Mode 3: Smart Orchestration (Multi-facetado)
**Quando usar**: Request complexa, múltiplas dependências, contexto amplo

**Exemplos**:
- "Crie um sistema completo de análise de recuperação"
- "Quero integrar com Strava e mostrar métricas avançadas"
- "Preciso de um dashboard novo com alertas inteligentes"

**Execução**: Orquestra múltiplos agentes em sequência coordenada

## Fluxo de Orquestração Inteligente

### Fase 1: Discovery & Scoping
```
Agente: pm-agent
Input original + contexto de negócio
Output: Escopo validado, user stories, critérios de aceitação
```

### Fase 2: Domain Validation
```
Agente: stakeholder-agent (se envolver métricas/calculos)
Input: Requisitos do PM + especificações técnicas necessárias
Output: Regras fisiológicas validadas, fórmulas definidas, thresholds
```

### Fase 3: Architecture Design
```
Agente: techlead-agent (se decisão arquitetural necessária)
Input: Requisitos validados
Output: ADR (se necessário), contratos de API, arquitetura
```

### Fase 4: Implementation Backend
```
Agente: backend-dev-agent
Input: Arquitetura + regras de negócio
Output: Código backend implementado
```

### Fase 5: Implementation Frontend
```
Agente: frontend-dev-agent
Input: API disponível + mockups/requisitos visuais
Output: Interface implementada
```

### Fase 6: Quality Assurance
```
Agente: qa-agent
Input: Código implementado + critérios de aceitação
Output: Testes BDD, regressão, sign-off
```

### Fase 7: Synthesis
```
Orquestrador consolida todos os outputs
Entrega resposta integrada ao usuário
```

## Exemplos de Orquestração

### Exemplo 1: Feature Completa
```
Input: "Crie um sistema de análise de potência avançada para ciclistas"

Fase 1 - PM:
  "Descoberta: Sistema de análise de potência"
  → PRD, user stories, priorização

Fase 2 - Stakeholder:
  "Definir métricas: CP curve, W', FRC, power profile"
  → Fórmulas, constantes, validações científicas

Fase 3 - TechLead:
  "Arquitetura para cálculos de potência e storage de time-series"
  → ADR, API contract, schema

Fase 4 - Backend:
  "Implementar cálculos CP/W', Power Profile, storage"
  → Serviços de domínio, API endpoints

Fase 5 - Frontend:
  "Dashboard de análise de potência com CP chart e Power Profile"
  → Componentes visuais, integração API

Fase 6 - QA:
  "Testes para cálculos de potência e interface"
  → BDD scenarios, testes de precisão

Resultado: Feature completa, testada, documentada
```

### Exemplo 2: Bug Complexo
```
Input: "Os cálculos de PMC estão divergindo do TrainingPeaks"

Fase 1 - QA:
  "Investigar divergência PMC"
  → Reprodução, logs, comparação de valores

Fase 2 - Stakeholder:
  "Validar cálculos CTL/ATL/TSB esperados"
  → Valores corretos, constantes, fórmulas oficiais

Fase 3 - Backend:
  "Corrigir implementação de PMC"
  → Fix nos cálculos exponenciais

Fase 4 - QA:
  "Validar correção"
  → Testes de regressão, comparação com TrainingPeaks

Resultado: Bug corrigido e validado
```

### Exemplo 3: Arquitetura + Implementação
```
Input: "Preciso integrar com Strava e processar atividades automaticamente"

Fase 1 - PM:
  "Discovery: Integração Strava"
  → Escopo, user value, priorização

Fase 2 - TechLead:
  "Arquitetura: Integração externa, webhooks, processamento async"
  → ADR, filas, workers, retry policy

Fase 3 - Backend:
  "Implementar integração Strava"
  → OAuth, API client, webhook handler, worker

Fase 4 - QA:
  "Testar integração"
  → Contract tests, E2E, resilience testing

Resultado: Integração implementada e robusta
```

## Interação com Usuário

### Opção 1: Autônomo Completo
Orquestrador decide e executa tudo automaticamente, reportando progresso:
```
🤖 Orquestrador: Detectei uma request de feature complexa.
   Iniciando discovery automático com PM Agent...

[Após Fase 1]
✅ PM: Discovery concluído. 3 user stories identificadas.
   Prosseguindo para validação técnica com Stakeholder...

[Após Fase 2]
✅ Stakeholder: Métricas validadas. Fórmulas definidas.
   Iniciando design arquitetural...
...
```

### Opção 2: Interativo (Padrão)
Orquestrador propõe plano e pede confirmação:
```
🤖 Orquestrador: Analisei sua request "[input]".

Detectei: Feature complexa envolvendo métricas de treinamento

Plano sugerido:
  1. PM Agent → Discovery e escopo
  2. Stakeholder Agent → Validação científica
  3. TechLead Agent → Arquitetura
  4. Backend Agent → Implementação
  5. QA Agent → Testes

Deseja prosseguir com este plano? [Y/n]
Ou prefere ajustar? [descreva mudanças]
```

### Opção 3: Sugestão de Workflow
Orquestrador sugere workflow específico:
```
🤖 Orquestrador: Sua request se encaixa no workflow `feature-development`.

Resumo do que será feito:
  - Design técnico
  - Implementação backend
  - Implementação frontend  
  - Testes BDD
  - Validação PM

Iniciar workflow? [Y/n]
```

## Comando de Uso

```bash
# Ativa o orquestrador com input
/windsurf "[sua request aqui - o orquestrador vai direcionar]"

# Ou explicitamente
/windsurf orchestrator "[sua request]"

# Ou atalhos de intenção
/windsurf "criar feature de ..."     → Discovery + Feature Dev
/windsurf "consertar bug em ..."     → Bug Fix
/windsurf "refatorar código de ..."  → Refactoring
/windsurf "como implementar ..."     → Architecture Review
/windsurf "sprint planning"          → Sprint Planning
/windsurf "lançar release"           → Release
```

## Templates de Input para Melhor Direcionamento

### Para Features
```
"Crie [feature] para [usuário] que resolve [problema]"
"Implementar [funcionalidade] que [benefício]"
"Nova feature: [nome] - [descrição breve]"
```

### Para Bugs
```
"Bug: [comportamento atual] deveria ser [comportamento esperado]"
"Erro em [módulo]: [descrição do erro]"
"[Funcionalidade] não funciona quando [condição]"
```

### Para Refatoração
```
"Refatorar [módulo] para [objetivo: melhorar performance/testabilidade/etc]"
"Melhorar código de [área] - está [problema: complexo/duplicado/lento]"
"Limpar débito técnico em [módulo]"
```

### Para Arquitetura
```
"Decidir: [opção A] vs [opção B] para [contexto]"
"Arquitetura para [requisito]"
"Migrar de [atual] para [novo]"
```

## Checklist de Orquestração

- [ ] Input analisado e classificado
- [ ] Agente(s) ou workflow identificado(s)
- [ ] Modo de operação definido (single/structured/orchestration)
- [ ] Sequência de execução planejada
- [ ] Dependências entre agentes mapeadas
- [ ] Handoffs definidos (outputs → inputs)
- [ ] Execução realizada
- [ ] Resultados sintetizados
- [ ] Entrega consolidada ao usuário

## Vantagens do Orquestrador

1. **Zero cognitive load**: Usuário não precisa saber qual agente usar
2. **Coordenação automática**: Agentes trabalham em sequência sem intervenção
3. **Contexto preservado**: Output de um agente alimenta o próximo
4. **Completeness**: Garante que todas as fases necessárias sejam cobertas
5. **Eficiência**: Não perde tempo com handoffs manuais

## Execução Paralela Avançada

### Detecção Automática de Paralelismo

O orchestrator pode detectar automaticamente quando tarefas são independentes:

```
Input: "Implementar feature de análise de potência"

Análise de Dependências:
├── TechLead: API Contract
│   └── Output: api_contract.json
│
├── Backend: Cálculos CP/W' (depende de api_contract)
│   └── Input: api_contract.json
│   └── Output: calculation_service.py
│
├── Frontend: Dashboard Power Profile (depende de api_contract)
│   └── Input: api_contract.json
│   └── Output: power-profile.component.ts
│
└── QA: BDD Tests (depende de api_contract)
    └── Input: api_contract.json
    └── Output: power.feature

Análise: Backend, Frontend e QA dependem apenas do API Contract
→ Podem executar em PARALELO após TechLead terminar
```

### Modo Fork-Join Automático

```bash
# Orchestrator detecta e executa em paralelo automaticamente
/windsurf "Desenvolver feature X"

[Orchestrator] Detectadas 3 tarefas independentes após fase de design
             Executando em paralelo...

[Backend Dev]  ████████████████████ 100% (4h)
[Frontend Dev] ████████████████████ 100% (4h)  ← paralelo
[QA Agent]     ████████████████░░░░  80% (3h)  ← paralelo

Sincronizando resultados...
[Integration]  ████████░░░░░░░░░░░░  40% (1h)
```

### Configuração de Paralelismo

```yaml
# Configuração implícita no orchestrator
parallel_mode: auto  # auto | sequential | force-parallel
max_parallel_agents: 3
synchronization_points:
  - after: design_phase
  - before: integration_phase
```

### Benefícios do Paralelismo Inteligente

| Cenário | Sequencial | Paralelo | Economia |
|---------|-----------|----------|----------|
| Backend + Frontend | 8h | 5h | 37% |
| Análises (PM + Stakeholder + TechLead) | 3h | 1.5h | 50% |
| Refatoração de 3 módulos | 6h | 2.5h | 58% |
| Bugfixes independentes | 4h | 1.5h | 62% |

### Quando NÃO Paralelizar

O orchestrator mantém sequencial quando:
- 🚫 Tarefa B depende do output completo da Tarefa A
- 🚫 Mesmo arquivo/componente sendo modificado
- 🚫 Decisões arquiteturais pendentes
- 🚫 Requisitos ainda não estabilizados
- 🚫 Integração complexa esperada (precisa de coordenação)

### Sincronização e Merge

Após execução paralela:

```
Fase Paralela:
├─→ [Backend] Output: api endpoints
├─→ [Frontend] Output: ui components
└─→ [QA] Output: test suite

Sincronização:
[Integrator] Consolida outputs → Valida compatibilidade
                                    ↓
[QA E2E] Testa sistema integrado → Sign-off
```

## Próximo Workflow

Após orquestração, o resultado é:
- Feature implementada → `release`
- Bug corrigido → `release` (hotfix)
- Arquitetura definida → `feature-development`
- Discovery completo → esperando aprovação para desenvolvimento
- Execução paralela → `parallel-execution` para gerenciamento
