# Sistema Multi-Agent de Desenvolvimento

Sistema de agentes especializados e workflows para desenvolvimento de software no estilo multi-agent, projetado especificamente para produtos de tecnologia esportiva (triathlon, endurance, fitness).

## 🎯 Agentes Disponíveis

### 1. PM Agent (`pm-agent`)
**Product Manager especialista em produtos de saúde e fitness**

- Discovery de produto e pesquisa de usuários
- Definição de métricas de negócio (CAC, LTV, NPS, Retenção)
- KPIs específicos de fitness (Improvement Rate, Plan Adherence)
- Frameworks RICE, priorização, roadmaps
- Validação de business case

**Use quando**: Iniciar novas features, definir escopo, priorizar backlog

### 2. Stakeholder Agent (`stakeholder-agent`)
**Especialista em triathlon, ciência do esporte e métricas de treinamento**

- Fisiologia do exercício (FCmax, FTP, zones, HRV)
- Cálculos de TrainingPeaks (TSS, CTL, ATL, TSB)
- Métricas de potência (NP, IF, VI, Power Profile)
- Periodização e prescrição de treino
- Base 100% científica, nenhum "achismo"

**Use quando**: Validar cálculos fisiológicos, definir algoritmos de métricas

### 3. Tech Lead Agent (`techlead-agent`)
**Arquiteto de software sênior**

- DDD (Domain-Driven Design)
- Clean Architecture
- Hexagonal Architecture
- Design Patterns (GoF + Arquiteturais)
- Decisões técnicas e ADRs
- Stack: Python/FastAPI, Angular, PostgreSQL/TimescaleDB

**Use quando**: Decisões arquiteturais, design de sistemas, code review

### 4. Backend Dev Agent (`backend-dev-agent`)
**Desenvolvedor Backend Python Especialista**

- FastAPI, Pydantic, SQLAlchemy 2.0
- Processamento de dados (Pandas, NumPy, SciPy)
- Cálculos matemáticos performáticos
- Integrações com wearables (Garmin, Strava)
- Testing com pytest, type hints obrigatórios

**Use quando**: Implementar APIs, algoritmos, integrações

### 5. Frontend Dev Agent (`frontend-dev-agent`)
**Desenvolvedor Frontend Especialista**

- Angular 17+ (standalone, signals, RxJS)
- Streamlit para prototipagem e dashboards
- Visualização de dados (Chart.js, D3.js, ApexCharts)
- UI/UX para atletas e treinadores
- Performance e acessibilidade

**Use quando**: Implementar interfaces, dashboards, visualizações

### 6. QA Agent (`qa-agent`)
**QA Engineer Especialista**

- BDD (Behavior Driven Development) com Gherkin
- Testes automatizados (unit, integration, E2E)
- Validação de cálculos matemáticos
- Playwright para E2E
- Quality gates e CI/CD

**Use quando**: Criar testes, validar qualidade, reportar bugs

---

## 🔄 Workflows Disponíveis

### 1. Discovery (`discovery`)
**Descoberta e validação de novas features**

Fases: Problem Discovery → Stakeholder Validation → Solution Ideation → Technical Feasibility → Business Case → Final Review

**Output**: PRD, Business Case, Go/No-Go decision

### 2. Feature Development (`feature-development`)
**Desenvolvimento completo de feature**

Fases: Technical Design → Backend Implementation → Frontend Implementation → Business Rule Validation → BDD Tests → E2E Tests → Code Review → PM Validation → Deployment

**Output**: Feature implementada, testada e em produção

### 3. Bug Fix (`bug-fix`)
**Correção estruturada de bugs**

Fases: Bug Report → Root Cause Analysis → Solution Design → Implementation → Validation → Code Review → QA Validation → Deployment

**Output**: Bug corrigido com teste de regressão

### 4. Architecture Review (`architecture-review`)
**Decisões arquiteturais significativas**

Fases: Problem Statement → Options Analysis → Proof of Concept → Decision & ADR → Communication

**Output**: ADR documentado, decisão registrada

### 5. Sprint Planning (`sprint-planning`)
**Planejamento de sprint ágil**

Fases: Sprint Review → Backlog Refinement → Estimation → Capacity Planning → Sprint Commitment → QA Planning → Communication

**Output**: Sprint backlog definido, meta clara, time alinhado

### 6. Release (`release`)
**Deploy para produção**

Fases: Preparation → Staging Validation → Pre-Deploy Checklist → Deployment → Post-Deploy Validation → PM Sign-off → Monitoring

**Output**: Release publicada, monitorado

### 7. Refactoring (`refactoring`)
**Refatoração segura de código**

Fases: Code Analysis → Refactoring Strategy → Safety Net → Refactoring Steps → Business Rule Validation → Regression Testing → Code Review → Post-Refactoring Metrics

**Output**: Código mais limpo, testável, mantível - sem mudanças de comportamento

### 8. Orchestrator (`orchestrator`)
**Roteamento inteligente e automático**

Analisa o input do usuário e direciona automaticamente para:
- Agente único (requests simples)
- Workflow estruturado (processos definidos)
- Orquestração multi-agent (requests complexas)
- **Execução paralela** quando tarefas são independentes

**Output**: Coordenação automática de múltiplos agentes/workflows

### 9. Parallel Execution (`parallel-execution`)
**Execução paralela de agentes independentes**

Orquestra múltiplos agentes simultaneamente quando:
- Backend e Frontend podem trabalhar juntos (após API contract)
- Análises independentes (PM, Stakeholder, TechLead)
- Refatoração de módulos desacoplados
- Bugfixes independentes

**Modelos**: Fork-Join, Pipeline com Paralelismo, Swarm
**Output**: Entrega mais rápida com speedup de 1.5x-2x

---

## 🚀 Como Usar

### Uso Básico - Comando Direto

```bash
# Invocar um agente específico
/windsurf pm-agent "Preciso criar um PRD para uma feature de análise de recuperação baseada em HRV"

/windsurf stakeholder-agent "Valide se meu cálculo de TSB está fisiologicamente correto: TSB = CTL - ATL"

/windsurf backend-dev-agent "Implemente uma função para calcular CTL usando média exponencial com numpy"
```

### Uso de Workflow

```bash
# Executar workflow completo
/windsurf discovery "Feature: Dashboard de análise de sono e recuperação para atletas"

/windsurf feature-development "Implementar cálculo automático de Training Stress Balance (TSB)"

/windsurf bug-fix "Bug: Cálculo de TSS retornando valores negativos para atividades curtas"
```

### Uso Avançado - Múltiplos Agentes

```bash
# PM define o que fazer
/windsurf pm-agent "Preciso de uma feature para alertar atletas sobre overtraining"

# Stakeholder valida a abordagem
/windsurf stakeholder-agent "Como detectar overtraining? Quais métricas usar? TSB, HRV, RPE?"

# Tech Lead define arquitetura  
/windsurf techlead-agent "Preciso de uma arquitetura para sistema de alertas em tempo real"

# Backend implementa
/windsurf backend-dev-agent "Implementar serviço de detecção de overtraining com threshold configurável"

# Frontend cria interface
/windsurf frontend-dev-agent "Criar componente de alerta visual e dashboard de status do atleta"

# QA valida
/windsurf qa-agent "Criar BDD scenarios para alertas de overtraining"

# Deixe o orquestrador decidir automaticamente
/windsurf "Crie uma feature de alerta de overtraining baseado em HRV"

# Execução paralela explícita (quando tasks são independentes)
/windsurf parallel-execution "Desenvolver dashboard: Backend API e Frontend UI em paralelo"
```

---

## 📋 Convenções de Comunicação

### Tags de Contexto

Use estas tags para indicar contexto:

- `[INIT]` - Início de novo trabalho
- `[DISCOVERY]` - Fase de discovery
- `[SPEC]` - Especificação técnica
- `[IMPL]` - Implementação
- `[REVIEW]` - Code review
- `[VALIDATE]` - Validação
- `[BUG]` - Report de bug
- `[REFACTOR]` - Refatoração
- `[ARCH]` - Decisão arquitetural
- `[METRICS]` - Definição de métricas
- `[STRATEGY]` - Decisão estratégica

### Exemplos

```bash
/windsurf pm-agent "[INIT] Nova feature: Importação automática do Strava"

/windsurf stakeholder-agent "[SPEC] Definir como calcular RSS (Running Stress Score) baseado em pace"

/windsurf techlead-agent "[ARCH] Devemos usar TimescaleDB ou PostgreSQL puro para métricas?"

/windsurf backend-dev-agent "[IMPL] Criar endpoint POST /api/activities/import com processamento async"

/windsurf qa-agent "[BUG] Cálculo de NP está 10% maior que o esperado para atividades com muitas paradas"
```

---

## 🏗️ Estrutura de Pastas

```
.windsurf/
├── agents/           # Definições dos agentes (6)
│   ├── pm-agent.md
│   ├── stakeholder-agent.md
│   ├── techlead-agent.md
│   ├── backend-dev-agent.md
│   ├── frontend-dev-agent.md
│   └── qa-agent.md
├── workflows/        # Workflows de processo (9)
│   ├── quick-start.md        # Guia de início rápido
│   ├── orchestrator.md       # Roteamento inteligente
│   ├── parallel-execution.md # Execução paralela ⭐ NOVO
│   ├── discovery.md          # Descoberta de produto
│   ├── feature-development.md # Desenvolvimento
│   ├── bug-fix.md            # Correção de bugs
│   ├── refactoring.md        # Refatoração segura
│   ├── architecture-review.md # Decisões técnicas
│   ├── sprint-planning.md    # Planejamento
│   └── release.md            # Deploy
└── README.md         # Este arquivo
```

---

## 🎯 Fluxos de Trabalho Típicos

### Fluxo 1: Nova Feature (Completo)

```
1. discovery → Valida oportunidade e define escopo
2. architecture-review → Se decisão técnica significativa
3. sprint-planning → Planeja sprint de implementação
4. feature-development → Implementa feature
5. release → Deploy para produção
```

### Fluxo 2: Bug em Produção

```
1. bug-fix → Reporta, analisa e corrige
2. (se severo) release (hotfix) → Deploy emergencial
```

### Fluxo 3: Sprint Normal

```
1. sprint-planning → Define backlog da sprint
2. feature-development (N vezes) → Para cada story
3. (opcional) bug-fix → Para bugs encontrados
4. release → Ao final da sprint
```

---

## 💡 Dicas de Uso

1. **Comece com o PM** para features novas - garante alinhamento de negócio
2. **Stakeholder é essencial** para qualquer cálculo fisiológico - validação científica
3. **Tech Lead primeiro** para decisões arquiteturais - evita retrabalho
4. **Use QA cedo** - escreva BDD scenarios antes de implementar
5. **Seja específico** nas requests - contexto melhora muito a qualidade
6. **Itere** - use os agentes em sequência, refinando a cada passo

---

## 🔗 Integração com Windsurf

Estes agentes são projetados para uso com o Cascade (Windsurf AI) usando o comando `/windsurf` ou similar. Cada agente tem:

- **Contexto especializado**: Conhecimento profundo em sua área
- **Instruções claras**: O que fazer e o que não fazer
- **Outputs definidos**: O que esperar de cada interação
- **Comunicação estruturada**: Tags e formatos consistentes

---

## 📚 Referências

### Agente Stakeholder
- **Livros**: "Training and Racing with a Power Meter" (Coggan & Allen), "The Triathlete's Training Bible" (Friel)
- **Software**: TrainingPeaks, WKO5, GoldenCheetah, Intervals.ICU
- **Teoria**: Chronic Training Load, Performance Management Chart, FTP testing protocols

### Agente Tech Lead
- **Livros**: "Clean Architecture" (Martin), "Domain-Driven Design" (Evans), "Building Microservices" (Newman)
- **Patterns**: GoF, Enterprise Patterns, CQRS, Event Sourcing
- **Stack**: FastAPI, Angular, PostgreSQL/TimescaleDB

### Agente PM
- **Frameworks**: RICE, JTBD, Lean Startup
- **Autores**: Marty Cagan, Teresa Torres, John Cutler
- **Métricas**: AARRR, HEART, North Star Framework
