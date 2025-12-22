# 🔧 Documentação Técnica - Fitness Metrics

## Arquitetura Técnica

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                 │
│  Streamlit Web App (HTML/CSS/JavaScript Automático)     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Application Logic Layer (Python)           │
│  • Page Navigation (Page Router)                        │
│  • Data Processing & Calculations                       │
│  • File Management & I/O                                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Data Access Layer                          │
│  • Local JSON File Storage                              │
│  • Garmin Connect API Client                            │
│  • Session State Management                             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              External Services                          │
│  • Garmin Connect REST API                              │
│  • Local Filesystem (~/.fitness_metrics/)               │
└──────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

### 1. Inicialização
```
app.py executa
    ↓
Carrega configuração Streamlit
    ↓
Verifica armazenamento local (~/.fitness_metrics/)
    ↓
Carrega credenciais (se existirem)
    ↓
Carrega métricas anteriores (se existirem)
    ↓
Renderiza página selecionada
```

### 2. Configuração
```
Usuário → Insere dados → app.py
              ↓
        Valida entrada
              ↓
        Encripta (se necessário)
              ↓
        Salva em ~/.fitness_metrics/
              ↓
        Feedback ao usuário
```

### 3. Sincronização Garmin
```
Usuário clica "Atualizar"
              ↓
        Carrega credenciais locais
              ↓
        Conecta Garmin Connect API
              ↓
        Fetch últimas 42 dias de atividades
              ↓
        Calcula TRIMP por atividade
              ↓
        Calcula CTL, ATL, TSB
              ↓
        Salva em ~/. fitness_metrics/
              ↓
        Renderiza Dashboard
```

## Estrutura de Arquivos JSON

### garmin_credentials.json
```json
{
    "email": "usuario@gmail.com",
    "password": "senha_criptografada_ou_plana"
}
```
**Localização:** `~/.fitness_metrics/garmin_credentials.json`
**Permissões:** `0o600` (apenas leitura do proprietário)

### user_config.json
```json
{
    "age": 29,
    "ftp": 250,
    "pace_threshold": "4:22",
    "swim_pace_threshold": "2:01",
    "hr_rest": 50,
    "hr_max": 191
}
```

### fitness_metrics.json
```json
[
    {
        "date": "2025-12-21",
        "daily_load": 95.5,
        "ctl": 45.2,
        "atl": 28.1,
        "tsb": 17.1
    },
    ...
]
```

### workouts_42_dias.json
```json
[
    {
        "activityId": 12345,
        "activityName": "Morning Run",
        "startTimeLocal": "2025-12-21T07:00:00",
        "duration": 3600,
        "distance": 10000,
        "averageHR": 145,
        "activityType": {
            "typeKey": "running"
        },
        ...
    },
    ...
]
```

## Algoritmos de Cálculo

### TRIMP (Training Impulse)

#### Ciclismo
```python
if avg_power e ftp:
    intensity_factor = avg_power / ftp
    TRIMP = duration_hours * (intensity_factor²) * 100
else:
    # Fallback para HR
    hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
    TRIMP = duration_min * hr_reserve * 0.64 * e^(1.92 * hr_reserve)
```

#### Corrida
```python
if avg_hr:
    hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
    TRIMP = duration_min * hr_reserve * 0.64 * e^(1.92 * hr_reserve)
else if avg_speed:
    pace_s_km = 1000 / avg_speed
    intensity = threshold_pace / current_pace
    TRIMP = duration_h * (intensity²) * 100
else:
    TRIMP = 0
```

#### Natação
```python
if distance > 0:
    pace_sec_100m = (duration_sec / distance) * 100
    intensity = threshold_pace / current_pace
    TRIMP = duration_h * (intensity²) * 100
else:
    TRIMP = duration_h * 25  # Fallback
```

### CTL (Chronic Training Load)
```
Fórmula: CTL = CTL_anterior + (TRIMP_do_dia - CTL_anterior) / 42

É uma média móvel exponencial com período de 42 dias
Atualiza diariamente com nova carga de treino
```

### ATL (Acute Training Load)
```
Fórmula: ATL = ATL_anterior + (TRIMP_do_dia - ATL_anterior) / 7

É uma média móvel exponencial com período de 7 dias
Detecta fadiga recente rapidamente
```

### TSB (Training Stress Balance)
```
Fórmula: TSB = CTL - ATL

Interpretação:
  >10: Sobre-descansado (risco de perda de forma)
  0-10: Forma ótima (pronto para competir)
  -10 a 0: Fadiga controlada (bom estado)
  <-10: Fadiga elevada (repouso recomendado)
```

## Estrutura de Código Streamlit

### Session State Management
```python
st.session_state['update_status']  # Status última atualização
st.session_state['email_input']    # Email do usuário
st.session_state['password_input'] # Senha do usuário
```

### Componentes Streamlit Utilizados
```python
st.set_page_config()      # Configuração da página
st.sidebar.radio()        # Menu de navegação
st.metric()               # Cards de métricas
st.columns()              # Layout em colunas
st.button()               # Botões de ação
st.text_input()           # Campos de texto
st.number_input()         # Campos numéricos
st.pyplot()               # Gráficos matplotlib
st.dataframe()            # Tabelas de dados
st.success/error/warning  # Mensagens
st.spinner()              # Indicador de carregamento
```

## Fluxo de Páginas

### Router Streamlit
```python
if page == "📊 Dashboard":
    # Renderiza dashboard
    # Carrega métricas
    # Exibe gráficos
    
elif page == "⚙️ Configuração":
    # Formulário de entrada
    # Validação
    # Salvamento local
    
elif page == "🔄 Atualizar Dados":
    # Interface Garmin
    # Status de sincronização
    # Histórico
```

## Integração com Garmin Connect

### Biblioteca: garminconnect

```python
from garminconnect import Garmin

# 1. Inicializar cliente
client = Garmin(email, password)

# 2. Autenticar
client.login()

# 3. Buscar atividades
activities = client.get_activities_by_date(
    start_date.isoformat(),
    end_date.isoformat()
)

# 4. Processar dados
for activity in activities:
    process_activity(activity)
```

### Campos de Activity Disponíveis
```python
activity = {
    'activityId': int,
    'activityName': str,
    'startTimeLocal': datetime_str,
    'duration': int (segundos),
    'distance': float (metros),
    'averageHR': int,
    'maxHR': int,
    'averagePower': int,
    'maxPower': int,
    'averageSpeed': float,
    'maxSpeed': float,
    'calories': int,
    'activityType': {
        'typeKey': str  # 'running', 'cycling', 'swimming', etc
    }
}
```

## Tratamento de Erros

### Garmin Connection
```python
try:
    client = Garmin(email, password)
    client.login()
except GarminConnectConnectionError:
    # Erro de conexão/credenciais
    st.error("Erro ao conectar com Garmin")
except GarminConnectAuthenticationError:
    # Erro de autenticação
    st.error("Email ou senha incorretos")
except Exception as e:
    # Erro genérico
    st.error(f"Erro: {str(e)}")
```

### File I/O
```python
try:
    with open(file_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    # Arquivo não existe - retorna padrão
    return default_value
except json.JSONDecodeError:
    # JSON inválido - retorna padrão
    return default_value
```

## Performance

### Otimizações Implementadas
1. **Cache Streamlit:** `@st.cache_data` para funções puras
2. **Session State:** Reutiliza dados entre reruns
3. **Lazy Loading:** Carrega dados sob demanda
4. **Minimal Re-rendering:** Evita renderizar tudo novamente

### Pontos de Otimização Futuros
```python
@st.cache_data
def load_metrics():
    # Cache resultados por 1 hora
    return load_metrics_from_file()

@st.cache_resource
def get_garmin_client():
    # Reutiliza cliente entre reruns
    return Garmin(email, password)
```

## Segurança

### Checklist Implementado
- [x] Credenciais não em variáveis de ambiente globais
- [x] Armazenamento local com permissões restritas
- [x] Validação de entrada
- [x] Tratamento seguro de exceções
- [x] Sem logs de credenciais
- [x] HTTPS em produção recomendado
- [x] Sem cache de senhas em sessão

### Melhorias de Segurança Futuras
```python
# Criptografia de credenciais
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_password = cipher.encrypt(password.encode())
```

## Testing

### Testes Sugeridos
```bash
# Teste de unidade
pytest tests/test_calculations.py

# Teste de integração Garmin
pytest tests/test_garmin_integration.py

# Teste de UI
pytest tests/test_ui.py --headless
```

## Deployment

### Docker (Opcional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port", "8501", \
     "--server.address", "0.0.0.0"]
```

### Executar
```bash
docker build -t fitness-metrics .
docker run -p 8501:8501 -v ~/.fitness_metrics:/root/.fitness_metrics fitness-metrics
```

## Variáveis de Ambiente (Opcional)

```bash
# .env ou environment
STREAMLIT_THEME_BASE_COLOR=light
STREAMLIT_LOGGER_LEVEL=error
STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false
```

## Logs e Debug

### Ativar Debug Mode
```bash
streamlit run app.py --logger.level=debug
```

### Logs Disponíveis
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## Métricas de Monitoramento

### Observabilidade Sugerida
```python
import time

start_time = time.time()
# ... operação ...
elapsed = time.time() - start_time
st.write(f"Tempo de execução: {elapsed:.2f}s")
```

## Roadmap Técnico

### v1.1.0 (Próxima)
- [ ] Cache com Redis
- [ ] Autenticação OAuth2
- [ ] Banco de dados SQLite
- [ ] API REST

### v1.2.0
- [ ] Background tasks
- [ ] Notificações push
- [ ] Exportação avançada
- [ ] Gráficos interativos (Plotly)

### v2.0.0
- [ ] Multi-usuário
- [ ] Sincronização em nuvem
- [ ] Mobile app nativo
- [ ] Integração IA/ML

---

## Referências Técnicas

- [Streamlit Docs](https://docs.streamlit.io/)
- [garminconnect GitHub](https://github.com/cyberjunky/python-garminconnect)
- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- [JSON Serialization](https://docs.python.org/3/library/json.html)
- [Matplotlib](https://matplotlib.org/)
- [Pandas](https://pandas.pydata.org/)

---

**Última Atualização:** 21 de dezembro de 2025
**Versão:** 1.0.0
**Status:** Production Ready
