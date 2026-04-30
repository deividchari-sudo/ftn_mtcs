---
description: Workflow de Review de Arquitetura - Processo para decisões arquiteturais significativas, refatorações estruturais e introdução de novos padrões.
---

# Workflow de Architecture Review

## Objetivo
Tomar decisões arquiteturais importantes de forma estruturada, documentando trade-offs e garantindo consistência com a visão técnica do produto.

## Trigger
- Nova dependência/arquitetura proposta
- Débito técnico significativo identificado
- Escalabilidade ou performance issues
- Nova integração complexa
- Migração tecnológica

## Participantes
- **techlead-agent**: Lidera e documenta
- **backend-dev-agent**: Implementa prova de conceito
- **frontend-dev-agent**: Avalia impacto frontend (se aplicável)
- **pm-agent**: Contexto de negócio e priorização

## Fases

### 1. Problem Statement [techlead-agent]
**Duração**: 20-30 min

**Atividades**:
1. Descrever problema arquitetural
2. Contexto e motivação
3. Impacto atual e projetado
4. Constraints e non-negotiables

**Outputs**:
- Problem statement claro
- Contexto de negócio
- Constraints identificadas

### 2. Options Analysis [techlead-agent]
**Duração**: 40-60 min

**Atividades**:
1. Brainstorm de alternativas (mínimo 2-3)
2. Análise de trade-offs
3. Prós e contras de cada opção
4. Considerar: não fazer nada

**Outputs**:
```markdown
## Opções Consideradas

### Opção A: [Nome]
- Descrição: ...
- Prós: ...
- Contras: ...
- Esforço: ...
- Riscos: ...

### Opção B: [Nome]
...

### Opção C: Não fazer nada
- Descrição: Manter estado atual
- Prós: Zero esforço
- Contras: Problema persiste
```

### 3. Proof of Concept [backend-dev-agent ou frontend-dev-agent]
**Duração**: 2-4 horas (ou um dia)

**Atividades**:
1. Implementar PoC da opção recomendada
2. Validar hipóteses principais
3. Medir impacto de performance (se aplicável)
4. Identificar gotchas

**Outputs**:
- Código de PoC
- Resultados de validação
- Métricas de performance (se aplicável)
- Issues identificadas

### 4. Decision & Documentation [techlead-agent]
**Duração**: 30-45 min

**Atividades**:
1. Revisar PoC
2. Tomar decisão final
3. Escrever ADR completo
4. Definir plano de implementação

**Outputs**:
- ADR (Architecture Decision Record)
- Decision: Accepted/Rejected/Superseded
- Plano de migração (se aplicável)

### 5. Communication [todos]
**Duração**: 15-20 min

**Atividades**:
1. Compartilhar ADR com time
2. Alinhar próximos passos
3. Atualizar documentação

**Outputs**:
- Time alinhado
- Documentação atualizada

## Template de ADR

```markdown
# ADR-XXX: [Título da Decisão]

## Status
- Proposed | Accepted | Deprecated | Superseded by ADR-YYY

## Context
Descreva o problema que estamos tentando resolver. Qual é o contexto?
O que motivou essa decisão?

## Decision
Descreva a decisão tomada. Seja específico.

## Consequences
### Positivas
- Benefício 1
- Benefício 2

### Negativas
- Trade-off 1
- Trade-off 2

### Riscos
- Risco identificado 1
- Mitigação: ...

## Alternatives Considered

### Alternativa A: [Nome]
Por que não foi escolhida?

### Alternativa B: [Nome]
Por que não foi escolhida?

## Implementation Notes
- Notas sobre como implementar
- Migração de código existente
- Breaking changes

## References
- Links relevantes
- Documentação
- Artigos de referência
```

## Exemplos de Decisões Típicas

### Exemplo 1: Adoção de TimescaleDB
```
Context: Precisamos armazenar métricas time-series de atividades
Opções: PostgreSQL puro, TimescaleDB, InfluxDB
Decisão: TimescaleDB
Rationale: Compatível com PostgreSQL, SQL familiar, 
           hypertables para performance, menos infra para gerenciar
Trade-off: Menos features específicas que InfluxDB
```

### Exemplo 2: Separação em Microserviços
```
Context: Módulos de cálculo e relatórios crescendo demais
Opções: Monolith modular, Microserviços, Serverless functions
Decisão: Monolith modular (por enquanto)
Rationale: Time pequeno, complexidade operacional alta,
           não temos problemas de escala ainda
Trade-off: Menor independência de deploy
Revisão: Reavaliar quando time > 10 devs
```

### Exemplo 3: Mudança de REST para GraphQL
```
Context: Frontend precisa de dados complexos e flexíveis
Opções: REST com expansion, GraphQL, gRPC + gateway
Decisão: GraphQL para queries complexas, REST para mutations simples
Rationale: Flexibilidade para frontend, sem overhead total
Trade-off: Complexidade adicional, caching mais difícil
```

## Checklist Final
- [ ] Problema claramente definido
- [ ] Múltiplas alternativas consideradas
- [ ] Trade-offs explicitados
- [ ] PoC realizado (para decisões grandes)
- [ ] ADR escrito e revisado
- [ ] Time comunicado
- [ ] Documentação atualizada
- [ ] Plano de implementação definido (se accepted)

## Próximo Workflow
Se aprovado: **feature-development** para implementação
