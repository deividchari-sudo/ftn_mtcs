---
description: Workflow de Refatoração - Processo estruturado para melhorar código existente sem mudar comportamento externo. Foca em código limpo, performance, e redução de débito técnico.
---

# Workflow de Refatoração

## Objetivo
Melhorar código existente de forma segura - mais limpo, performático, testável e mantível - sem alterar comportamento externo visível.

## Trigger
- Código difícil de manter ou entender
- Duplicação identificada
- Performance issues
- Débito técnico acumulado
- Preparação para nova feature
- Code smells detectados

## Tipos de Refatoração

### 1. Structural (Arquitetural)
- Extrair serviços/módulos
- Reorganizar packages
- Aplicar patterns (Repository, Strategy, etc.)
- Separar concerns

### 2. Code Quality
- Renomear variáveis/funções
- Extrair funções/métodos
- Simplificar condicionais
- Remover duplicação

### 3. Performance
- Otimizar algoritmos
- Melhorar queries de banco
- Implementar caching
- Reduzir complexidade ciclomática

### 4. Testing
- Aumentar cobertura
- Refatorar para testabilidade
- Remover mocks excessivos
- Adicionar testes de contrato

## Participantes
- **techlead-agent**: Define estratégia e valida arquitetura
- **backend-dev-agent**: Refatora código backend
- **frontend-dev-agent**: Refatora código frontend
- **qa-agent**: Garante que comportamento não mudou (regressão)
- **stakeholder-agent**: Valida se regras de negócio preservadas (se cálculos/métricas)

## Fases

### 1. Code Analysis & Assessment [qa-agent + dev-agent]
**Duração**: 30-45 min

**Atividades**:
1. Identificar code smells
2. Medir métricas atuais (coverage, complexidade, duplicação)
3. Documentar comportamento atual (golden masters)
4. Priorizar áreas para refatoração

**Code Smells Checklist**:
- [ ] Métodos longos (>20 linhas)
- [ ] Classes grandes (>200 linhas)
- [ ] Duplicação de código
- [ ] Nomes não descritivos
- [ ] Acoplamento alto
- [ ] Baixa coesão
- [ ] Comentários excessivos (código não auto-explicativo)
- [ ] Cadeias de if/else profundas
- [ ] Feature envy (método que usa mais dados de outra classe)
- [ ] Dead code

**Ferramentas**:
- SonarQube / CodeClimate
- radon (complexidade Python)
- coverage.py
- pylint/ruff

**Outputs**:
- Lista de code smells priorizada
- Métricas baseline (coverage %, complexidade média, etc.)
- Testes de golden master (snapshot dos outputs atuais)

### 2. Refactoring Strategy [techlead-agent]
**Duração**: 30-45 min

**Atividades**:
1. Escolher estratégia de refatoração
2. Definir "refactoring bounds" (o que está in/out)
3. Planejar passos pequenos e seguros
4. Identificar riscos e mitigações

**Estratégias Comuns**:

**Extract Service/Module**:
```
1. Criar novo módulo/service vazio
2. Mover funções uma a uma
3. Atualizar imports
4. Testar após cada movimento
```

**Simplify Algorithm**:
```
1. Documentar comportamento atual com testes
2. Criar nova implementação lado a lado
3. Feature flag para alternar
4. Comparar outputs (property-based testing)
5. Remover código antigo
```

**Improve Testability**:
```
1. Identificar dependências externas
2. Extrair interfaces/ports
3. Injetar dependências
4. Adicionar testes
5. Refatorar implementação
```

**Outputs**:
- Plano de refatoração passo a passo
- Refactoring bounds definidos
- Estratégia de validação (como garantir que não quebrou)
- Rollback plan

### 3. Pre-Refactoring: Safety Net [qa-agent]
**Duração**: 30-60 min

**Atividades**:
1. Adicionar testes de caracterização (documentar comportamento atual)
2. Criar golden masters (inputs/outputs esperados)
3. Snapshot testing para outputs complexos
4. Aumentar cobertura mínima

**Testes de Caracterização**:
```python
# Antes de refatorar, capture comportamento atual
def test_characterization_current_behavior():
    result = function_under_refactor(input_data)
    # Não assert valor específico, capture
    assert result == snapshot  # ou documente expected
```

**Outputs**:
- Testes de caracterização passando
- Golden masters criados
- Cobertura mínima garantida (>70%)

### 4. Refactoring Steps [dev-agent]
**Duração**: Variável (iterativo)

**Princípios**:
- **Passos pequenos**: Cada commit deve compilar e passar testes
- **Testes sempre verdes**: Se quebrar, rollback imediato
- **Uma coisa por vez**: Não misture refactoring com feature work
- **Commit frequente**: Cada pequena mudança commitada

**Checklist por Passo**:
- [ ] Testes passando antes de começar
- [ ] Mudança pequena e focada
- [ ] Testes passando após mudança
- [ ] Commit com mensagem clara
- [ ] Se testes quebrarem: revert imediato

**Técnicas Específicas**:

**Extract Method**:
```python
# Antes
def calculate_tss(np, ftp, duration):
    if ftp <= 0:
        raise ValueError("FTP must be positive")
    intensity_factor = np / ftp
    tss = (duration * np * intensity_factor) / (ftp * 3600) * 100
    return tss

# Depois
def _validate_ftp(ftp):
    if ftp <= 0:
        raise ValueError("FTP must be positive")

def _calculate_intensity_factor(np, ftp):
    return np / ftp

def calculate_tss(np, ftp, duration):
    _validate_ftp(ftp)
    intensity_factor = _calculate_intensity_factor(np, ftp)
    return (duration * np * intensity_factor) / (ftp * 3600) * 100
```

**Rename for Clarity**:
```python
# Antes
def calc(x, y):
    return x / y * 100

# Depois
def calculate_percentage(part: float, whole: float) -> float:
    """Calculate what percentage 'part' is of 'whole'."""
    return (part / whole) * 100
```

**Remove Duplication**:
```python
# Antes
def calculate_zone_2_min(ftp):
    return ftp * 0.56

def calculate_zone_2_max(ftp):
    return ftp * 0.75

# Depois
ZONE_2_PERCENTAGE = (0.56, 0.75)
ZONE_3_PERCENTAGE = (0.76, 0.90)

def calculate_power_zone(ftp: float, zone_percentages: tuple) -> tuple:
    """Calculate min/max watts for a power zone."""
    return (ftp * zone_percentages[0], ftp * zone_percentages[1])
```

### 5. Business Rule Validation [stakeholder-agent] (se aplicável)
**Duração**: 20-30 min

**Atividades**:
1. Revisar cálculos/algoritmos refatorados
2. Validar que fórmulas estão preservadas
3. Verificar unidades e constantes
4. Comparar outputs: antigo vs. novo

**Outputs**:
- Validação de que regras de negócio estão preservadas
- Sign-off ou correções necessárias

### 6. Regression Testing [qa-agent]
**Duração**: 30-45 min

**Atividades**:
1. Rodar suite completa de testes
2. Comparar golden masters
3. Testes de propriedade (property-based)
4. Testes de performance (se aplicável)
5. Smoke tests em ambiente de integração

**Property-Based Testing**:
```python
from hypothesis import given, strategies as st

@given(
    np=st.floats(min_value=0, max_value=500),
    ftp=st.floats(min_value=100, max_value=500),
    duration=st.integers(min_value=1, max_value=36000)
)
def test_tss_properties(np, ftp, duration):
    tss = calculate_tss(np, ftp, duration)
    # Propriedades que devem sempre valer
    assert tss >= 0
    if np == ftp and duration == 3600:
        assert abs(tss - 100) < 0.01
```

**Outputs**:
- Todos os testes passando
- Golden masters equivalentes
- Report de regressão (nenhuma encontrada)

### 7. Code Review [techlead-agent]
**Duração**: 30 min

**Atividades**:
1. Revisar qualidade do código refatorado
2. Verificar se objetivos foram atingidos
3. Validar que padrões foram seguidos
4. Aprovar ou solicitar ajustes

**Checklist de Review**:
- [ ] Código mais limpo e legível?
- [ ] Duplicação removida?
- [ ] Complexidade reduzida?
- [ ] Testes adequados?
- [ ] Documentação atualizada?
- [ ] Sem mudanças de comportamento?

**Outputs**:
- Aprovação ou itens de correção

### 8. Post-Refactoring Metrics [qa-agent]
**Duração**: 15-20 min

**Atividades**:
1. Medir métricas pós-refatoração
2. Comparar com baseline
3. Documentar ganhos

**Métricas a Comparar**:
| Métrica | Before | After | Delta |
|---------|--------|-------|-------|
| Coverage | 65% | 85% | +20% |
| Complexidade média | 8.5 | 4.2 | -51% |
| Linhas por método | 35 | 12 | -66% |
| Code smells | 25 | 5 | -80% |

**Outputs**:
- Report de métricas comparativas
- Documentação dos ganhos

### 9. Documentation Update [dev-agent]
**Duração**: 15-20 min

**Atividades**:
1. Atualizar docstrings
2. Atualizar ADRs (se arquitetura mudou)
3. Atualizar README/docs de API
4. Atualizar diagramas

**Outputs**:
- Documentação sincronizada com código

## Checklist Final
- [ ] Code smells identificados e corrigidos
- [ ] Testes passando (100%)
- [ ] Golden masters preservados
- [ ] Sem regressões detectadas
- [ ] Métricas melhoradas
- [ ] Código revisado e aprovado
- [ ] Documentação atualizada
- [ ] Commits organizados e claros

## Outputs Finais
1. Código refatorado e mais limpo
2. Testes robustos (caracterização + regressão)
3. Métricas comparativas (before/after)
4. Documentação atualizada
5. Aprendizados documentados

## Anti-Patterns a Evitar

❌ **Nunca**:
- Refatore sem testes de segurança
- Mude comportamento durante refactoring
- Faça refactoring em código que não entende
- Misture refactoring com nova feature no mesmo commit
- Refatore "só porque sim" - precisa de objetivo claro

✅ **Sempre**:
- Tenha testes antes de começar
- Faça passos pequenos e commit frequente
- Mantenha testes verdes
- Revise código após refactoring
- Documente métricas de melhoria

## Próximo Workflow
- Se refatoração foi para preparar feature: **feature-development**
- Se bugs encontrados durante refactoring: **bug-fix**
- Se arquitetura mudou significativamente: **architecture-review**
- Se performance melhorou e precisa validar: **release**
