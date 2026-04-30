---
description: Workflow de Release - Processo de preparação, validação e deploy de release para produção.
---

# Workflow de Release

## Objetivo
Garantir que releases sejam feitas de forma segura, previsível e com rollback plan, minimizando riscos e tempo de downtime.

## Trigger
- Sprint concluída
- Features prontas para produção
- Hotfix crítico necessário

## Participantes
- **pm-agent**: Validação de features e sign-off
- **techlead-agent**: Preparação técnica e rollback plan
- **qa-agent**: Regression testing e validação final
- **backend-dev-agent**: Deploy backend e monitoramento
- **frontend-dev-agent**: Deploy frontend e verificação

## Tipos de Release

### 1. Regular Release
- Ciclo normal (sprint-based)
- Múltiplas features
- Testing completo

### 2. Hotfix Release
- Bug crítico em produção
- Mínimo changeset
- Fast-track testing

### 3. Rollback
- Release problemático
- Retorno à versão anterior
- Incident response

## Fases

### 1. Release Preparation [techlead-agent]
**Duração**: 30-45 min

**Atividades**:
1. Criar release branch (git flow)
2. Atualizar versão (semantic versioning)
3. Consolidar changelog
4. Preparar rollback plan

**Semantic Versioning**:
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes

**Outputs**:
- Release branch criada
- CHANGELOG.md atualizado
- Versão bumpada
- Rollback plan documentado

### 2. Staging Validation [qa-agent]
**Duração**: 2-4 horas

**Atividades**:
1. Regression testing completo
2. Testar novas features
3. Validar integrações
4. Performance testing (se necessário)
5. Smoke tests

**Regression Suite**:
- Fluxos críticos: login, importação de atividades, cálculos
- Core features: PMC, análises, planos
- Integrações: Garmin, Strava
- Edge cases conhecidos

**Outputs**:
- QA Sign-off para staging
- Report de regressão
- Bugs críticos: fix ou postpone

### 3. Pre-Deployment Checklist [techlead-agent]
**Duração**: 15-20 min

**Checklist**:
- [ ] Todos os testes passando
- [ ] Code freeze em vigor
- [ ] Database migrations testadas
- [ ] Feature flags configuradas (se aplicável)
- [ ] Rollback plan validado
- [ ] Monitoramento pronto
- [ ] Comunicação agendada
- [ ] Time on-call disponível

**Rollback Plan**:
```markdown
## Rollback Plan - Release X.Y.Z

### Database
- Migrations podem ser revertidas? [Sim/Não]
- Backup necessário: [Detalhes]
- Rollback procedure: [Passos]

### Código
- Versão anterior: X.Y.(Z-1)
- Rollback command: [Comando]
- Tempo estimado: X minutos

### Verificação pós-rollback
- [ ] Health check passando
- [ ] Core features funcionando
- [ ] Logs sem erros
```

**Outputs**:
- Go/No-Go decision
- Pre-deployment checklist completo

### 4. Deployment [backend-dev-agent + frontend-dev-agent]
**Duração**: 30-60 min (com monitoramento)

**Atividades**:
1. Database migrations (primeiro)
2. Backend deployment
3. Frontend deployment
4. Verificar health checks
5. Smoke tests em produção

**Deployment Order**:
```
1. Database migrations (com backup)
2. Backend services (rolling deployment)
3. Frontend assets (CDN)
4. Verificação de integrações
5. Feature flags enable (gradual)
```

**Outputs**:
- Deploy realizado
- Health checks passando
- Feature flags ativadas

### 5. Post-Deployment Validation [qa-agent + pm-agent]
**Duração**: 30-60 min

**Atividades**:
1. Smoke tests críticos em produção
2. Validar features novas
3. Monitorar métricas e logs
4. Verificar alertas

**Smoke Tests**:
- [ ] Homepage carrega
- [ ] Login funciona
- [ ] Importação de atividade funciona
- [ ] Cálculos de PMC retornam valores
- [ ] Dashboard carrega sem erros

**Monitoring**:
- Error rate < 1%
- Response time < 500ms p95
- CPU/Memory normal
- No critical alerts

**Outputs**:
- QA Sign-off em produção
- Validation report

### 6. PM Sign-off & Communication [pm-agent]
**Duração**: 15-20 min

**Atividades**:
1. Validar features de negócio
2. Comunicar stakeholders
3. Atualizar release notes
4. Fechar release

**Communication**:
```markdown
## Release X.Y.Z - Notes

**Data**: [Data]
**Versão**: X.Y.Z

**Novidades**:
- Feature 1: [Descrição]
- Feature 2: [Descrição]
- Bug fixes: [Lista]

**Comunicação**:
- Email para usuários: [Se major release]
- In-app changelog: [Sim]
- Documentação atualizada: [Links]
```

**Outputs**:
- Release notes publicadas
- Stakeholders comunicados
- Release fechado

### 7. Monitoring & Follow-up [todos]
**Duração**: 24-48 horas

**Atividades**:
1. Monitorar métricas
2. Watch error logs
3. Coletar feedback
4. Hotfix se necessário

**Dashboards**:
- Error rate by endpoint
- Response times
- User sessions
- Feature adoption (novas features)

**Outputs**:
- 24h report
- Issues identificadas (se houver)

## Checklist Final
- [ ] Staging validada
- [ ] Rollback plan pronto
- [ ] Database migrations testadas
- [ ] Deploy realizado com sucesso
- [ ] Smoke tests em produção passando
- [ ] QA sign-off
- [ ] PM sign-off
- [ ] Release notes publicadas
- [ ] 24h monitoring completo
- [ ] Nenhum incidente crítico

## Template de Release Notes

```markdown
# Release X.Y.Z - [Data]

## 🚀 Novidades

### Feature 1
[Descrição da feature e valor para usuário]

### Feature 2
[Descrição da feature e valor para usuário]

## 🐛 Correções
- Bug 1: [Descrição]
- Bug 2: [Descrição]

## 🔧 Melhorias Técnicas
- [Lista de refatorações e melhorias]

## 📊 Métricas da Release
- X stories entregues
- Y bugs corrigidos
- Z pontos de velocity
- Tempo de deploy: X minutos

## 👏 Agradecimentos
- [Lista de contribuidores]
```

## Próximo Workflow
Se incidente: **incident-response**
Se hotfix necessário: **bug-fix** → **hotfix-release**
