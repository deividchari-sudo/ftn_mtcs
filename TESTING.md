# 🧪 Guia de Testes - Fitness Metrics

## ✅ Testes Manuais

### 1️⃣ Teste de Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python -c "import streamlit; import garminconnect; import matplotlib; print('✅ OK')"
```

**Resultado Esperado:** ✅ OK

---

### 2️⃣ Teste de Inicialização

```bash
streamlit run app.py
```

**Resultado Esperado:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Ação:** Abra `http://localhost:8501` no navegador

---

### 3️⃣ Teste de Interface

#### 📊 Dashboard
- [ ] Página carrega
- [ ] Aviso aparece se sem dados
- [ ] Cards de métrica aparecem com dados
- [ ] Gráfico renderiza corretamente
- [ ] Tabela exibe últimos 7 dias
- [ ] Layout responsivo

#### ⚙️ Configuração
- [ ] Página carrega
- [ ] Campos de entrada são interativos
- [ ] Valores padrão aparecem
- [ ] Botão "Salvar" funciona
- [ ] Mensagem de sucesso aparece
- [ ] Dados são salvos localmente
- [ ] Botão "Deletar" funciona
- [ ] Botão "Ver Local" funciona

#### 🔄 Atualizar Dados
- [ ] Página carrega
- [ ] Aviso aparece se sem credenciais
- [ ] Botão atualizar está disponível
- [ ] Spinner aparece durante atualização
- [ ] Mensagem de sucesso/erro aparece
- [ ] Dados atualizam corretamente

---

### 4️⃣ Teste de Segurança

#### Armazenamento Local
```bash
# Verificar se credenciais foram criadas
ls ~/.fitness_metrics/

# Esperado:
# garmin_credentials.json
# user_config.json
# fitness_metrics.json
# workouts_42_dias.json
```

#### Permissões de Arquivo
```bash
# Windows: Verificar com Properties
# Linux/Mac:
ls -la ~/.fitness_metrics/

# Esperado: drwx------ para diretório
#          -rw------- para credenciais
```

---

### 5️⃣ Teste de Cálculos

#### Dados de Teste
Crie um arquivo `test_data.json`:

```json
[
    {
        "activityId": 1,
        "activityName": "Test Run",
        "startTimeLocal": "2025-12-21T08:00:00",
        "duration": 3600,
        "distance": 10000,
        "averageHR": 150,
        "activityType": {
            "typeKey": "running"
        }
    }
]
```

#### Verificar Cálculos
```python
# No Python console
from app import calculate_trimp, calculate_fitness_metrics
from datetime import datetime, timedelta

# Verificar TRIMP
activity = {...}
config = {...}
trimp = calculate_trimp(activity, config)
print(f"TRIMP: {trimp}")

# Verificar Métricas
metrics = calculate_fitness_metrics([activity], config, 
                                     datetime.now().date() - timedelta(42),
                                     datetime.now().date())
print(f"Métricas: {metrics}")
```

**Resultado Esperado:** Valores numéricos > 0

---

### 6️⃣ Teste de Garmin Connect (Com Credenciais Reais)

**⚠️ Somente com conta de teste!**

```bash
# Definir credenciais de teste
# Via interface Streamlit
```

**Passos:**
1. Vá para ⚙️ Configuração
2. Insira email e senha Garmin
3. Clique "Salvar"
4. Vá para 🔄 Atualizar Dados
5. Clique "Atualizar Dados Agora"
6. Aguarde sincronização

**Resultado Esperado:**
- ✅ Login bem-sucedido
- Atividades carregadas
- Métricas calculadas
- Mensagem de sucesso

---

## 🤖 Testes Automatizados

### Setup
```bash
pip install pytest pytest-streamlit
```

### Test Suite
```python
# tests/test_calculations.py

import pytest
from app import calculate_trimp, calculate_fitness_metrics
from datetime import datetime, timedelta

def test_calculate_trimp():
    """Testa cálculo de TRIMP"""
    activity = {
        'activityType': {'typeKey': 'running'},
        'duration': 3600,
        'averageHR': 150,
        'distance': 10000,
        'averageSpeed': 2.78
    }
    config = {
        'hr_rest': 50,
        'hr_max': 191,
        'pace_threshold': '4:22'
    }
    
    trimp = calculate_trimp(activity, config)
    assert trimp > 0, "TRIMP deve ser positivo"
    assert isinstance(trimp, (int, float)), "TRIMP deve ser numérico"

def test_calculate_fitness_metrics():
    """Testa cálculo de CTL, ATL, TSB"""
    activities = [...]
    config = {...}
    start_date = datetime.now().date() - timedelta(days=42)
    end_date = datetime.now().date()
    
    metrics = calculate_fitness_metrics(activities, config, start_date, end_date)
    
    assert len(metrics) == 43, "Deve ter 43 dias de dados"
    assert all(m['ctl'] >= 0 for m in metrics), "CTL deve ser >= 0"
    assert all(m['atl'] >= 0 for m in metrics), "ATL deve ser >= 0"
```

### Executar Testes
```bash
pytest tests/ -v
```

---

## 📱 Teste no Android

### Pre-requisitos
- [ ] Termux instalado
- [ ] Python instalado
- [ ] Dependências instaladas
- [ ] Projeto copiado para Android

### Passos
1. Abra Termux
2. Navegue para o projeto: `cd ~/fitness_metrics`
3. Inicie: `streamlit run app.py`
4. Abra navegador: `http://localhost:8501`

### Testes Específicos
- [ ] App inicia sem erros
- [ ] Interface é responsiva
- [ ] Toque em botões funciona
- [ ] Input de texto funciona
- [ ] Gráfico renderiza
- [ ] Sincronização funciona
- [ ] Dados persistem

---

## 🐛 Checklist de Bugs Comuns

| Bug | Sintoma | Solução |
|-----|---------|---------|
| Porta 8501 em uso | "Address already in use" | `lsof -i :8501` + kill |
| Módulo não instalado | "ModuleNotFoundError" | `pip install <modulo>` |
| Credenciais inválidas | Erro Garmin | Verifique em garmin.com |
| Dados não salvam | Nenhuma pasta ~/.fitness_metrics | Verifique permissões |
| Gráfico não carrega | Blank page | Verifique dados em JSON |
| Android muito lento | Lag interface | Feche outros apps |
| Memória cheia | Crash | Limpe cache: `rm -rf ~/.cache/*` |

---

## 📊 Teste de Performance

### Benchmark
```python
import time

def benchmark_operations():
    operations = {
        'load_config': load_config,
        'load_metrics': load_metrics,
        'calculate_trimp': calculate_trimp,
        'calculate_fitness_metrics': calculate_fitness_metrics
    }
    
    for name, func in operations.items():
        start = time.time()
        result = func(...)
        elapsed = time.time() - start
        print(f"{name}: {elapsed:.3f}s")
```

**Tempo Esperado:**
- load_config: < 10ms
- load_metrics: < 50ms
- calculate_trimp: < 5ms
- calculate_fitness_metrics: < 500ms

---

## 🔐 Teste de Segurança

### Checklist
- [ ] Credenciais não em logs
- [ ] Arquivo de credenciais tem permissões restritas
- [ ] Senhas não são exibidas na interface
- [ ] Sem validação de XSS em inputs
- [ ] CORS desativado
- [ ] XSRF protection ativo

### Teste Manual
```bash
# Verificar se senha aparece em logs
streamlit run app.py 2>&1 | grep -i password
# Esperado: Nenhuma saída

# Verificar arquivo de credenciais
file ~/.fitness_metrics/garmin_credentials.json
# Esperado: permissões 0600
```

---

## 📈 Teste de Carga

### Simulação com Muitos Dados
```bash
# Gerar dados de teste (365 dias)
python -c "
import json
from datetime import datetime, timedelta

metrics = []
for i in range(365):
    date = datetime.now() - timedelta(days=365-i)
    metrics.append({
        'date': date.isoformat(),
        'daily_load': 100 + i,
        'ctl': 45 + i*0.1,
        'atl': 30 + i*0.05,
        'tsb': 15 + i*0.05
    })

with open('test_metrics.json', 'w') as f:
    json.dump(metrics, f)

print('✅ Dados de teste gerados')
"

# Copiar para pasta local
cp test_metrics.json ~/.fitness_metrics/fitness_metrics.json

# Testar performance
streamlit run app.py
```

**Resultado Esperado:**
- Carregamento em < 2s
- Gráfico renderiza em < 3s
- Sem crashes ou memory leaks

---

## 🎨 Teste de UI/UX

### Responsividade
- [ ] Desktop (1920x1080): OK
- [ ] Tablet (768x1024): OK
- [ ] Mobile (360x640): OK
- [ ] Android (vário): OK

### Acessibilidade
- [ ] Botões têm contraste adequado
- [ ] Texto legível
- [ ] Inputs têm labels
- [ ] Mensagens são claras

### Usabilidade
- [ ] Fluxo intuitivo
- [ ] Sem cliques desnecessários
- [ ] Feedback visual claro
- [ ] Tempo resposta aceitável

---

## 📋 Teste de Documentação

- [ ] README.md está completo
- [ ] QUICKSTART.md funciona
- [ ] ANDROID.md está atualizado
- [ ] TECHNICAL.md é preciso
- [ ] Exemplos funcionam
- [ ] Links estão válidos

---

## ✅ Checklist Final

Antes de deployer em produção:

- [ ] Todos os testes manuais passam
- [ ] Nenhum erro em console
- [ ] Credenciais funcionam
- [ ] Dados sincronizam corretamente
- [ ] Cálculos são precisos
- [ ] Performance é aceitável
- [ ] Segurança validada
- [ ] Documentação completa
- [ ] Android testado
- [ ] Sem memory leaks

---

## 📞 Suporte

Se encontrar bugs:
1. Descreva o sintoma
2. Forneça passos para reproduzir
3. Compartilhe logs (sem senhas!)
4. Especifique ambiente (OS, Python, etc.)

---

**Boa sorte com os testes! 🎉**
