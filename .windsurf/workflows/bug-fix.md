---
description: Workflow de Correção de Bugs - Processo estruturado para investigar, reproduzir e corrigir bugs em produção ou desenvolvimento.
---

# Workflow de Bug Fix

## Objetivo
Investigar, corrigir e validar bugs de forma estruturada, garantindo que a correção seja adequada e não introduza regressões.

## Trigger
- Bug reportado em produção
- Testes falhando
- Comportamento inesperado identificado

## Severidade
- **P0 (Critical)**: Sistema inoperante, data loss, segurança
- **P1 (High)**: Feature principal quebrada, workaround difícil
- **P2 (Medium)**: Feature secundária, workaround disponível
- **P3 (Low)**: Cosmetic, enhancement

## Participantes
- **qa-agent**: Reporta e investiga
- **backend-dev-agent**: Fix backend
- **frontend-dev-agent**: Fix frontend
- **stakeholder-agent**: Valida se comportamento está correto (bugs de regra de negócio)
- **techlead-agent**: Review de solução complexa

## Fases

### 1. Bug Report & Triage [qa-agent]
**Duração**: 15-20 min

**Atividades**:
1. Documentar reprodução passo a passo
2. Coletar logs e evidências
3. Definir severidade
4. Identificar área afetada

**Outputs**:
```
Bug Report:
- Título: [Área] Breve descrição
- Severidade: P0/P1/P2/P3
- Ambiente: staging/prod/dev
- Passos para reproduzir:
  1. ...
  2. ...
- Comportamento esperado: ...
- Comportamento atual: ...
- Evidências: screenshots, logs, videos
- Primeira análise: qual componente suspeito
```

### 2. Root Cause Analysis [dev-agent apropriado]
**Duração**: 30-60 min (depende da complexidade)

**Atividades**:
1. Reproduzir o bug localmente
2. Analisar logs e stack traces
3. Debug do fluxo de execução
4. Identificar causa raiz

**Outputs**:
- Causa raiz identificada
- Explicação técnica do problema
- Componentes afetados

### 3. Solution Design [dev-agent]
**Duração**: 15-30 min

**Atividades**:
1. Projetar correção
2. Avaliar impacto
3. Considerar regressões
4. Decidir: quick fix vs. proper fix

**Outputs**:
- Plano de correção
- Trade-offs documentados
- Estimativa de tempo

### 4. Implementation [dev-agent]
**Duração**: Depende da complexidade

**Atividades**:
1. Implementar correção
2. Adicionar testes para regressão
3. Testar localmente

**Checklist**:
- [ ] Bug corrigido
- [ ] Teste de regressão adicionado
- [ ] Código segue padrões do projeto
- [ ] Não introduz novos bugs

### 5. Stakeholder Validation (se regra de negócio) [stakeholder-agent]
**Duração**: 10-15 min

**Atividades**:
1. Validar se comportamento agora está correto
2. Verificar cálculos/algoritmos
3. Confirmar que atende requisito

**Outputs**:
- Validação ou ajustes necessários

### 6. Code Review [techlead-agent ou peer]
**Duração**: 15-20 min

**Atividades**:
1. Revisar solução
2. Verificar qualidade
3. Validar testes

**Outputs**:
- Aprovação ou itens de correção

### 7. QA Validation [qa-agent]
**Duração**: 20-30 min

**Atividades**:
1. Reproduzir bug original (deve passar)
2. Testar cenários relacionados
3. Testar regressões
4. Validar fix em staging

**Outputs**:
- QA Sign-off
- Report de testes

### 8. Deployment & Verification
**Duração**: 15-20 min

**Atividades**:
1. Deploy para produção
2. Verificar fix
3. Monitorar métricas
4. Fechar ticket

## Checklist Final
- [ ] Bug reproduzido e entendido
- [ ] Causa raiz identificada
- [ ] Correção implementada
- [ ] Teste de regressão adicionado
- [ ] QA validou a correção
- [ ] Deploy para produção
- [ ] Bug resolvido em produção
- [ ] Documentação atualizada (se necessário)

## Template de Bug Report
```markdown
## Bug Report

**Título:** [Módulo] Descrição curta

**Severidade:** P0/P1/P2/P3

**Ambiente:** 
- Versão: X.Y.Z
- Navegador/OS: ...
- Ambiente: prod/staging/dev

**Descrição:**
Descrição detalhada do problema

**Passos para Reproduzir:**
1. Passo 1
2. Passo 2
3. Passo 3

**Comportamento Esperado:**
O que deveria acontecer

**Comportamento Atual:**
O que está acontecendo

**Evidências:**
- Screenshot: [link]
- Log: [trecho relevante]
- Video: [link]

**Análise Inicial:**
Suspeita inicial de causa/componente afetado

**Relacionado a:**
Links para issues/PRs relacionados
```

## Próximo Workflow
Se bug recorrente: Análise de padrão
Se muitos bugs: **tech-debt-assessment**
