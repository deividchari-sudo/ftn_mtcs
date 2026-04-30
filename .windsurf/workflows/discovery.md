---
description: Workflow de Discovery - Processo de descoberta e validação de novas features ou melhorias. Ideal para iniciar novas funcionalidades com alinhamento entre negócio e técnico.
---

# Workflow de Discovery

## Objetivo
Realizar discovery completo de uma nova funcionalidade, garantindo que problemas reais sejam identificados, soluções sejam validadas e todos os stakeholders estejam alinhados antes de iniciar desenvolvimento.

## Trigger
- Nova feature solicitada
- Problema identificado em métricas
- Oportunidade de mercado descoberta
- Feedback recorrente de usuários

## Participantes
- **pm-agent**: Lidera, define escopo e métricas
- **stakeholder-agent**: Valida aspectos técnicos de triathlon
- **techlead-agent**: Avalia viabilidade técnica e esforço

## Fases

### 1. Problem Discovery [pm-agent]
**Duração**: 30-60 min de análise

**Atividades**:
1. Definir problema a ser resolvido
2. Identificar usuários afetados
3. Mapear jobs-to-be-done
4. Analisar dados atuais (se disponíveis)

**Outputs**:
- Problem Statement claro
- Personas afetadas
- Hipóteses iniciais

### 2. Stakeholder Validation [stakeholder-agent]
**Duração**: 20-30 min

**Atividades**:
1. Validar se problema é real para atletas/treinadores
2. Identificar soluções existentes no mercado
3. Verificar se há base científica para a solução
4. Questionar métricas propostas

**Outputs**:
- Validação ou refutação do problema
- Referências científicas relevantes
- Restrições fisiológicas/conceituais

### 3. Solution Ideation [pm-agent + stakeholder-agent]
**Duração**: 30-45 min

**Atividades**:
1. Brainstorm de soluções possíveis
2. Análise de alternativas no mercado
3. Definição de MVP vs. versão completa
4. Priorização de features

**Outputs**:
- 2-3 alternativas de solução
- Prós e contras de cada
- Recomendação de solução MVP

### 4. Technical Feasibility [techlead-agent]
**Duração**: 30-45 min

**Atividades**:
1. Avaliar complexidade técnica
2. Identificar dependências
3. Avaliar esforço (T-shirt sizing)
4. Identificar riscos técnicos

**Outputs**:
- Assessment de viabilidade
- Estimativa de esforço (S, M, L, XL)
- Riscos e mitigações
- Recomendações técnicas

### 5. Business Case [pm-agent]
**Duração**: 20-30 min

**Atividades**:
1. Definir métricas de sucesso
2. Calcular ROI esperado
3. Definir critérios de aceitação
4. Priorizar no backlog

**Outputs**:
- Business Case document
- KPIs de sucesso
- Critérios de aceitação
- Recomendação: Go/No-Go

### 6. Final Review [todos]
**Duração**: 15-20 min

**Atividades**:
1. Revisão de todos os outputs
2. Alinhamento final
3. Próximos passos definidos

**Outputs**:
- Decision: Go (com escopo definido) ou No-Go
- Handoff para desenvolvimento (se Go)

## Outputs Finais do Discovery
1. **PRD** (Product Requirements Document)
2. **Business Case** com métricas
3. **Technical Assessment**
4. **User Stories** iniciais (backlog técnico)
5. **Go/No-Go decision**

## Checklist de Conclusão
- [ ] Problema validado com dados ou pesquisa
- [ ] Solução proposta tem valor claro
- [ ] Viabilidade técnica confirmada
- [ ] Esforço está aceitável
- [ ] Métricas de sucesso definidas
- [ ] Critérios de aceitação claros

## Próximo Workflow
Se aprovado: **feature-development**
