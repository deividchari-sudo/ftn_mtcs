---
description: Workflow de Planning de Sprint - Processo de planejamento de sprint ágil com definição de escopo, estimativas e alinhamento do time.
---

# Workflow de Sprint Planning

## Objetivo
Planejar sprint de forma colaborativa, definindo escopo realista, alinhando expectativas e garantindo que o time tenha clareza sobre o que será entregue.

## Trigger
- Início de nova sprint
- Ciclo de desenvolvimento semanal/quizenal

## Participantes
- **pm-agent**: Priorização e escopo de negócio
- **techlead-agent**: Viabilidade técnica e dependências
- **backend-dev-agent**: Capacidade e estimativas backend
- **frontend-dev-agent**: Capacidade e estimativas frontend
- **qa-agent**: Planejamento de testes

## Fases

### 1. Review da Sprint Anterior [todos]
**Duração**: 15-20 min

**Atividades**:
1. O que foi entregue?
2. O que ficou pendente e por quê?
3. Métricas de velocidade
4. Lições aprendidas

**Outputs**:
- Sprint retrospective resumida
- Ajustes no processo (se necessário)
- Velocidade atualizada

### 2. Backlog Refinement [pm-agent + techlead-agent]
**Duração**: 20-30 min

**Atividades**:
1. Revisar stories priorizadas
2. Garantir que estão prontas para desenvolvimento (Definition of Ready)
3. Quebrar stories grandes
4. Identificar dependências entre stories

**Definition of Ready Checklist**:
- [ ] Título claro
- [ ] Descrição de valor para usuário
- [ ] Critérios de aceitação definidos
- [ ] Regras de negócio claras
- [ ] Mockups ou referências visuais (se aplicável)
- [ ] Estimativa técnica possível

**Outputs**:
- Stories refinadas
- Dependências mapeadas
- Stories quebradas se necessário

### 3. Estimation [backend-dev-agent + frontend-dev-agent]
**Duração**: 30-45 min

**Atividades**:
1. Estimar cada story
2. Usar planning poker ou similar
3. Discussão de complexidade
4. Considerar: desenvolvimento + testes + code review

**Escala de Estimativa** (Story Points):
- 1: Trivial (menos de 2h)
- 2: Simples (2-4h)
- 3: Médio (meio dia)
- 5: Complexo (1 dia)
- 8: Muito complexo (2 dias)
- 13+: Precisa ser quebrado

**Outputs**:
- Estimativas para cada story
- Stories que precisam ser quebradas

### 4. Capacity Planning [todos]
**Duração**: 15-20 min

**Atividades**:
1. Verificar disponibilidade do time
2. Considerar: feriados, reuniões, tech talks
3. Aplicar foco factor (focus factor ~60-70%)
4. Capacidade total disponível

**Cálculo**:
```
Backend dev: 10 dias × 0.7 = 7 pontos disponíveis
Frontend dev: 10 dias × 0.7 = 7 pontos disponíveis
Total capacidade: ~14 pontos
```

**Outputs**:
- Capacidade total calculada
- Foco factor aplicado

### 5. Sprint Commitment [pm-agent]
**Duração**: 20-30 min

**Atividades**:
1. Selecionar stories que cabem na capacidade
2. Ordenar por prioridade e dependências
3. Definir meta da sprint (sprint goal)
4. Alinhar expectativas

**Sprint Goal Template**:
```
Meta da Sprint: [Descrição clara do objetivo principal]

Entregáveis:
- [Story 1] - X pontos
- [Story 2] - Y pontos
- ...

Total: Z pontos
```

**Outputs**:
- Sprint backlog definido
- Sprint goal claro
- Compromisso do time

### 6. QA Planning [qa-agent]
**Duração**: 10-15 min

**Atividades**:
1. Identificar stories que precisam de BDD
2. Planejar testes exploratórios
3. Alocar tempo para regressão
4. Definir critérios de "done"

**Definition of Done**:
- [ ] Código implementado
- [ ] Unit tests passando (>80% coverage)
- [ ] Code review aprovado
- [ ] Testes de integração passando
- [ ] BDD scenarios passando
- [ ] QA sign-off
- [ ] Documentação atualizada
- [ ] Deploy em staging

**Outputs**:
- Plano de testes da sprint
- Checklist de DoD revisado

### 7. Communication & Setup [todos]
**Duração**: 10 min

**Atividades**:
1. Atualizar board/tickets
2. Criar branches de feature
3. Setup de ambientes se necessário
4. Alinhamento final

**Outputs**:
- Board atualizado
- Time alinhado

## Template de Sprint Backlog

```markdown
# Sprint N - [Data início] a [Data fim]

## Meta
[Descrição clara do objetivo principal da sprint]

## Capacidade
- Backend: X pontos
- Frontend: Y pontos
- Total: Z pontos

## Stories

### Prioridade 1 - Must Have
- [ ] [Story 1] - [Título] - X pts
  - Assignee: [Nome]
  - Dependências: [Lista]
  
- [ ] [Story 2] - [Título] - Y pts
  - Assignee: [Nome]
  - Dependências: [Lista]

### Prioridade 2 - Should Have
...

### Prioridade 3 - Nice to Have
...

## Riscos
- [Risco 1]: [Mitigação]
- [Risco 2]: [Mitigação]

## Métricas Alvo
- Velocity: Z pontos
- Cycle time médio: X dias
- Bug count: < Y
```

## Checklist Final
- [ ] Stories refinadas e estimadas
- [ ] Capacidade calculada
- [ ] Sprint backlog definido
- [ ] Sprint goal claro
- [ ] Definition of Done revisado
- [ ] Plano de testes definido
- [ ] Riscos identificados
- [ ] Time comprometido

## Próximos Workflows Durante Sprint
- **feature-development**: Para cada story
- **bug-fix**: Para bugs encontrados
- **daily-standup**: Sincronização diária (opcional)

## Ritmo de Sprint Recomendado
- **Sprint**: 2 semanas
- **Planning**: 2 horas no início
- **Review**: 1 hora na quinta-feira da semana 2
- **Retrospective**: 1 hora na sexta-feira da semana 2
