---
description: Workflow de Desenvolvimento de Feature - Processo completo de implementação desde design técnico até entrega em produção.
---

# Workflow de Desenvolvimento de Feature

## Objetivo
Implementar uma feature do discovery até produção, seguindo boas práticas de arquitetura, desenvolvimento e qualidade.

## Trigger
- Discovery aprovado (Go decision)
- PRD disponível
- User stories prontas

## Participantes
- **techlead-agent**: Design arquitetural e decisões técnicas
- **backend-dev-agent**: Implementação backend
- **frontend-dev-agent**: Implementação frontend
- **stakeholder-agent**: Validação de regras de negócio
- **qa-agent**: Testes e qualidade
- **pm-agent**: Validação de entrega

## Fases

### 1. Technical Design [techlead-agent]
**Duração**: 45-60 min

**Atividades**:
1. Criar ADR (Architecture Decision Record) se necessário
2. Definir contratos de API (OpenAPI/JSON Schema)
3. Modelar banco de dados
4. Definir padrões e estruturas

**Outputs**:
- ADR (se decisão significativa)
- API contract
- Database schema/migrations
- Architecture diagram (se complexo)

### 2. Backend Implementation [backend-dev-agent]
**Duração**: Depende da feature (2h - 2 dias)

**Atividades**:
1. Criar models e repositories
2. Implementar domain services
3. Criar use cases
4. Implementar API endpoints
5. Adicionar tests unitários

**Checklist**:
- [ ] Type hints em todas as funções públicas
- [ ] Domain logic testada
- [ ] API endpoints documentados (OpenAPI)
- [ ] Error handling implementado
- [ ] Validações com Pydantic

### 3. Frontend Implementation [frontend-dev-agent]
**Duração**: Depende da feature (2h - 2 dias)

**Atividades**:
1. Criar/ajustar models TypeScript
2. Implementar services (API calls)
3. Criar componentes
4. Implementar páginas/views
5. Adicionar tests de componentes

**Checklist**:
- [ ] Componentes standalone
- [ ] Signals para estado reativo
- [ ] Loading e error states
- [ ] Responsividade testada
- [ ] Acessibilidade básica

### 4. Business Rule Validation [stakeholder-agent]
**Duração**: 20-30 min

**Atividades**:
1. Revisar implementação de cálculos/algoritmos
2. Validar fórmulas e constantes
3. Verificar unidades e conversões
4. Validar lógica de negócio

**Outputs**:
- Aprovação ou lista de correções
- Validação de precisão numérica

### 5. BDD Test Creation [qa-agent]
**Duração**: 30-45 min

**Atividades**:
1. Escrever scenarios Gherkin baseados nos critérios de aceitação
2. Implementar step definitions
3. Criar testes unitários para cálculos
4. Criar testes de integração para APIs

**Outputs**:
- Feature files (.feature)
- Step definitions
- Testes automatizados

### 6. E2E Testing [qa-agent]
**Duração**: 30-60 min

**Atividades**:
1. Implementar testes E2E com Playwright
2. Cobrir fluxos principais
3. Testar edge cases
4. Validar integração backend-frontend

**Outputs**:
- Testes E2E passando
- Report de coverage

### 7. Code Review Simulation [techlead-agent]
**Duração**: 30 min

**Atividades**:
1. Revisar arquitetura
2. Verificar padrões aplicados
3. Checar qualidade de código
4. Validar testes

**Outputs**:
- Aprovação ou itens de correção

### 8. PM Validation [pm-agent]
**Duração**: 20-30 min

**Atividades**:
1. Validar contra critérios de aceitação
2. Verificar se resolve o problema original
3. Validar UX/UI
4. Aprovar para deploy

**Outputs**:
- Go/No-Go para produção

### 9. Deployment & Monitoring
**Duração**: 15-20 min

**Atividades**:
1. Deploy para produção
2. Smoke tests
3. Verificar métricas
4. Monitoramento inicial

## Checklist Final
- [ ] Feature implementada conforme PRD
- [ ] Testes unitários passando (>80% coverage)
- [ ] Testes de integração passando
- [ ] Testes E2E passando
- [ ] BDD scenarios executáveis
- [ ] Stakeholder validou regras de negócio
- [ ] PM aprovou entrega
- [ ] Deploy realizado com sucesso
- [ ] Monitoramento configurado

## Outputs Finais
1. Código implementado e testado
2. Documentação de API atualizada
3. Testes automatizados
4. Métricas de coverage
5. Feature em produção

## Próximo Workflow
Se houver bugs: **bug-fix**
Se próxima feature: **feature-development** ou **discovery**
