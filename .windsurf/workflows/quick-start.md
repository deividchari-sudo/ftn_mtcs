---
description: Workflow Quick Start - Início rápido para novos ciclos de trabalho ou quando você não sabe por onde começar.
---

# Workflow Quick Start

## Objetivo
Ajuda a decidir por onde começar e qual workflow ou agente usar para sua necessidade atual.

## Quando Usar
- Não sabe qual agente chamar
- Nova sessão de trabalho
- Contexto misto (precisa de múltiplos agentes)
- Quer overview do que fazer

## Perguntas de Diagnóstico

Responda mentalmente (ou explique na request):

### 1. O que você precisa fazer?

| Se você quer... | Use... |
|----------------|--------|
| Criar algo novo | `discovery` ou `feature-development` |
| Consertar algo quebrado | `bug-fix` |
| Mudar como o sistema funciona | `architecture-review` |
| Planejar o trabalho da semana | `sprint-planning` |
| Colocar código em produção | `release` |
| Validar cálculo/métrica | `stakeholder-agent` |
| Decidir tecnologia/arquitetura | `techlead-agent` |
| Entender usuário/negócio | `pm-agent` |
| Escrever código backend | `backend-dev-agent` |
| Fazer interface/dashboard | `frontend-dev-agent` |
| Criar testes | `qa-agent` |

### 2. Em que estágio está?

| Estágio | Ação |
|---------|------|
| Só tenho uma ideia | Comece com `pm-agent` ou `discovery` |
| Ideia validada, preciso implementar | Use `feature-development` |
| Já estou implementando, preciso de ajuda | Chame agente específico (`backend-dev`, `frontend-dev`) |
| Terminei, preciso validar | Use `qa-agent` |
| Tem bug em produção | Use `bug-fix` |
| Preciso lançar | Use `release` |

### 3. Quem precisa estar envolvido?

| Tipo de Trabalho | Agentes Típicos |
|-----------------|-----------------|
| Nova feature de métricas | PM → Stakeholder → TechLead → Backend → Frontend → QA |
| Bug em cálculo de TSS | QA → Stakeholder → Backend → QA |
| Refatoração de arquitetura | TechLead → Backend → Frontend → QA |
| Dashboard novo | PM → TechLead → Frontend → QA |
| Integração com API externa | TechLead → Backend → QA |
| Alerta de negócio | PM → Stakeholder → TechLead → Backend → Frontend → QA |

## Atalhos Rápidos

### Quero implementar uma feature nova
```bash
/windsurf discovery "[descrição da feature]"
# Depois, quando aprovado:
/windsurf feature-development "Implementar [feature aprovada]"
```

### Quero corrigir um bug
```bash
/windsurf bug-fix "[descrição do bug]"
```

### Quero validar se meu cálculo está certo
```bash
/windsurf stakeholder-agent "[descrição do cálculo e valores esperados]"
```

### Quero decidir arquitetura
```bash
/windsurf architecture-review "Preciso decidir [decisão arquitetural]"
```

### Quero planejar sprint
```bash
/windsurf sprint-planning "Planejar sprint para [período]"
```

### Quero fazer release
```bash
/windsurf release "Preparar release X.Y.Z"
```

## Exemplos por Tipo de Tarefa

### Tarefas de Negócio/Product

```bash
# Nova ideia
/windsurf pm-agent "Tenho uma ideia: alerta de overtraining baseado em HRV e TSB"

# Definir métricas
/windsurf pm-agent "Quais KPIs devo acompanhar para uma feature de plano de treino?"

# Priorizar backlog
/windsurf pm-agent "Tenho essas 5 stories, qual framework usar para priorizar?"

# Validar discovery
/windsurf discovery "Feature: Importação automática do Strava com sync diário"
```

### Tarefas Técnicas/Esportivas

```bash
# Validar métrica
/windsurf stakeholder-agent "Estou calculando TSS assim: (segundos * NP * IF) / (FTP * 3600) * 100. Está correto?"

# Definir zonas
/windsurf stakeholder-agent "Como definir zonas de frequência cardíaca para um atleta com FCmax 185 e FCrepouso 45?"

# Periodização
/windsurf stakeholder-agent "Qual ramp rate semanal de CTL é segura para um atleta intermediário?"
```

### Tarefas de Arquitetura

```bash
# Decisão técnica
/windsurf techlead-agent "Devo usar PostgreSQL puro ou TimescaleDB para armazenar métricas de atividades?"

# Design de API
/windsurf techlead-agent "Como modelar API REST para recursos de treino (planos, sessões, métricas)?"

# Padrão de código
/windsurf techlead-agent "Qual padrão usar para cálculos de métricas: Service, Strategy, ou outro?"
```

### Tarefas de Implementação

```bash
# Backend - API
/windsurf backend-dev-agent "Criar endpoint POST /api/v1/activities que recebe arquivo FIT e retorna métricas processadas"

# Backend - Cálculo
/windsurf backend-dev-agent "Implementar função calculate_tsb(ctl_values, atl_values) usando numpy para performance"

# Backend - Integração
/windsurf backend-dev-agent "Implementar cliente para Garmin Connect API com OAuth2 e rate limiting"

# Frontend - Dashboard
/windsurf frontend-dev-agent "Criar componente PMCChart (Performance Management Chart) usando Chart.js ou D3"

# Frontend - Página
/windsurf frontend-dev-agent "Criar página de dashboard do atleta com cards de métricas e gráfico PMC"

# Streamlit - Protótipo
/windsurf frontend-dev-agent "Criar protótipo em Streamlit de análise de potência com upload de arquivo FIT"
```

### Tarefas de Qualidade

```bash
# BDD
/windsurf qa-agent "Criar BDD scenarios para feature de cálculo automático de FTP"

# Teste de cálculo
/windsurf qa-agent "Como testar que meu cálculo de CTL está matematicamente correto?"

# E2E
/windsurf qa-agent "Criar teste E2E com Playwright para fluxo de importação de atividade"

# Bug report
/windsurf qa-agent "Reportar bug: Cálculo de NP retorna None para atividades sem potência"
```

## Checklist de Início Rápido

Antes de chamar um agente, tenha claro:

- [ ] **O que** precisa ser feito (descrição clara)
- [ ] **Por que** (contexto de negócio ou técnico)
- [ ] **Quem** é o usuário afetado (se aplicável)
- [ ] **Critérios de sucesso** (como saber que está pronto)

Exemplo de request bem estruturada:
```
/windsurf pm-agent "Preciso de discovery para uma feature de alerta de recuperação:
- Contexto: Atletas estão se lesionando por overtraining
- Usuário: Triatletas amadores que treinam 8-12h/semana
- Sucesso: Reduzir lesões reportadas em 30% em 3 meses
- Escopo inicial: Alerta baseado em TSB < -30 por 3+ dias"
```

## Próximo Workflow

Baseado na sua necessidade:
- Feature nova → `discovery`
- Implementar → `feature-development`
- Bug → `bug-fix`
- Arquitetura → `architecture-review`
- Planejar → `sprint-planning`
- Lançar → `release`
