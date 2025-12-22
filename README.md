# Fitness Metrics - Webapp Streamlit

Um aplicativo web de rastreamento de métricas de fitness que se integra com Garmin Connect. Funciona perfeitamente em Android (via Termux ou navegador web).

## 🎯 Características

- **📊 Dashboard Interativo**: Visualize suas métricas de fitness (CTL, ATL, TSB) em tempo real
- **⚙️ Configuração Segura**: Armazene credenciais do Garmin Connect localmente no seu dispositivo
- **🔄 Sincronização com Garmin Connect**: Busque atividades dos últimos 42 dias e atualize métricas
- **📱 Responsivo**: Funciona perfeitamente em desktop, tablet e Android
- **🔐 Seguro**: Credenciais armazenadas apenas no dispositivo, nunca em servidores

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Execute a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá no seu navegador padrão (geralmente `http://localhost:8501`)

## 📱 Uso no Android

### Opção 1: Via Termux (Recomendado)

1. Instale [Termux](https://termux.dev/) do F-Droid ou Play Store
2. Instale Python: `pkg install python`
3. Clone/baixe este projeto
4. Execute: `cd /caminho/para/projeto && pip install -r requirements.txt && streamlit run app.py`
5. Acesse em seu navegador: `http://localhost:8501`

### Opção 2: Servidor remoto

1. Inicie o app em um servidor com acesso à sua rede
2. Acesse via: `http://seu-servidor:8501` no navegador do Android

## 🎮 Guia de Uso

### 📊 Dashboard
- Visualize suas métricas atuais (Fitness, Fadiga, Equilíbrio)
- Confira gráficos de evolução dos últimos 42 dias
- Veja um histórico das métricas

### ⚙️ Configuração
**Credenciais Garmin Connect:**
- Email e senha da sua conta Garmin Connect
- ⚠️ Armazenados de forma segura apenas neste dispositivo

**Parâmetros de Fitness:**
- **Idade**: Sua idade em anos
- **FTP (Watts)**: Seu limiar de potência funcional (para ciclismo)
- **FC Repouso**: Sua frequência cardíaca em repouso
- **FC Máxima**: Sua frequência cardíaca máxima
- **Limiar de Pace (Corrida)**: Seu limiar de pace em formato mm:ss
- **Limiar de Pace (Natação)**: Seu limiar de pace para natação em mm:ss

### 🔄 Atualizar Dados
- Clique em "Atualizar Dados Agora" para sincronizar com Garmin Connect
- A aplicação buscará todas as atividades dos últimos 42 dias
- Recalcula automaticamente CTL, ATL e TSB

## 📊 Métricas Explicadas

- **CTL (Chronic Training Load)**: Forma física acumulada (média de 42 dias)
- **ATL (Acute Training Load)**: Fadiga recente (média de 7 dias)
- **TSB (Training Stress Balance)**: Equilíbrio entre forma e fadiga (CTL - ATL)

## 🔐 Segurança

- As credenciais do Garmin Connect são armazenadas **apenas no seu dispositivo**
- Arquivo: `~/.fitness_metrics/garmin_credentials.json` (permissões restritas)
- Você pode deletar as credenciais a qualquer momento via interface
- Nenhum dado é enviado para servidores externos

## 📁 Estrutura de Arquivos

```
~/.fitness_metrics/
├── garmin_credentials.json    # Credenciais (armazenadas localmente)
├── user_config.json           # Parâmetros de fitness
├── fitness_metrics.json       # Métricas calculadas
└── workouts_42_dias.json      # Lista de atividades
```

## 🛠️ Solução de Problemas

### "garminconnect não instalado"
```bash
pip install garminconnect
```

### Erro de conexão com Garmin
- Verifique se seu email e senha estão corretos
- Verifique sua conexão com a internet
- Tente fazer login no site do Garmin manualmente

### Dados não aparecem no Dashboard
1. Vá para "⚙️ Configuração"
2. Verifique se as credenciais estão corretas
3. Clique em "🔄 Atualizar Dados Agora"
4. Aguarde a sincronização

## 📝 Notas

- A aplicação respeita os limites da API do Garmin Connect
- Dados são recalculados a cada atualização
- Os parâmetros de fitness podem ser ajustados a qualquer momento

## 📞 Suporte

Para questões sobre o Garmin Connect, acesse: https://www.garmin.com/

## 📄 Licença

Este projeto é fornecido como está. Use por sua conta e risco.
