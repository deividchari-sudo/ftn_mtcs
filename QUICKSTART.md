# 🚀 Início Rápido - Fitness Metrics

## ⚡ 30 segundos para começar

### Windows
```bash
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Android (Termux)
```bash
pkg install python
pip install -r requirements.txt
streamlit run app.py
```

Depois, abra seu navegador em: **http://localhost:8501**

---

## 📋 Checklist de Primeiro Uso

- [ ] Instale as dependências: `pip install -r requirements.txt`
- [ ] Inicie o app: `streamlit run app.py`
- [ ] Acesse: http://localhost:8501
- [ ] Vá para **⚙️ Configuração**
- [ ] Insira email e senha do Garmin Connect
- [ ] Preencha seus parâmetros de fitness (FTP, FC máxima, etc.)
- [ ] Clique em **💾 Salvar Configurações**
- [ ] Vá para **🔄 Atualizar Dados**
- [ ] Clique em **🔄 Atualizar Dados Agora**
- [ ] Visualize seus dados em **📊 Dashboard**

---

## 🔐 Segurança - Importante!

✅ **Suas credenciais são armazenadas APENAS no seu dispositivo**

Arquivo: `~/.fitness_metrics/garmin_credentials.json`

- Nunca são enviadas para servidores
- Nunca são enviadas para a internet
- Permissões restritas (0o600)
- Você pode deletar a qualquer momento via interface

---

## 📱 Versão Android

Veja [ANDROID.md](ANDROID.md) para instruções detalhadas.

**Resumo:**
1. Instale Termux (F-Droid ou Play Store)
2. `pkg install python`
3. `pip install -r requirements.txt`
4. `streamlit run app.py`
5. Acesse em `http://localhost:8501`

---

## 🎯 O que o app faz

### 📊 Dashboard
- Visualiza suas métricas atuais (Fitness, Fadiga, Equilíbrio)
- Gráfico de 42 dias
- Histórico em tabela

### ⚙️ Configuração  
- Armazena email e senha do Garmin (localmente)
- Parâmetros de fitness pessoais
- Deletar credenciais em segurança

### 🔄 Atualizar Dados
- Sincroniza com Garmin Connect
- Busca atividades dos últimos 42 dias
- Calcula CTL, ATL, TSB automaticamente

---

## 📊 Métricas Explicadas

- **CTL (Chronic Training Load)**: Sua forma física acumulada
- **ATL (Acute Training Load)**: Sua fadiga recente
- **TSB (Training Stress Balance)**: Equilíbrio = CTL - ATL

---

## ❓ Precisa de ajuda?

### Erro de instalação
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de conexão com Garmin
- Verifique email e senha
- Tente fazer login manualmente em garmin.com
- Aguarde 5 minutos e tente novamente

### Nenhum dado aparece
1. Verifique as credenciais em **⚙️ Configuração**
2. Clique em **🔄 Atualizar Dados Agora**
3. Aguarde a sincronização

### Streamlit não abre
- Verifique se Python está instalado: `python --version`
- Instale Streamlit: `pip install streamlit`
- Verifique a porta 8501: `netstat -an | findstr 8501`

---

## 📖 Documentação Completa

Veja [README.md](README.md) para documentação detalhada.

---

## 🎬 Próximos Passos

1. **Configure sua conta**: ⚙️ Configuração
2. **Sincronize dados**: 🔄 Atualizar Dados  
3. **Visualize progresso**: 📊 Dashboard
4. **Acompanhe diariamente**: Use o botão de atualização

---

**Aproveite seu rastreamento de fitness! 💪**

*Última atualização: 21 de dezembro de 2025*
