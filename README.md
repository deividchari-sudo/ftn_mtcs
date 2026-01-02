# 💪 Fitness Metrics Dashboard

Um dashboard interativo moderno para monitoramento de métricas de fitness com integração ao Garmin Connect. Acompanhe seu progresso através das métricas CTL (Chronic Training Load), ATL (Acute Training Load) e TSB (Training Stress Balance).

## 📋 Visão Geral

Este aplicativo Dash permite que atletas monitorem seu estado de forma física através de métricas científicas baseadas em dados de atividades físicas. A integração com Garmin Connect permite sincronização automática de dados de treino.

### ✨ Funcionalidades Principais

- **📊 Dashboard Interativo**: Visualize seu estado atual de forma física com métricas CTL, ATL e TSB
- **🤖 Chat IA**: Consulte um assistente inteligente sobre seus dados de treino e progresso
- **🔄 Sincronização Garmin**: Importe automaticamente atividades dos últimos 42 dias
- **📅 Calendário de Treinos**: Veja seu histórico de atividades em formato de calendário
- **🎯 Metas Personalizáveis**: Configure e acompanhe metas semanais e mensais
- **❤️ Métricas Avançadas de Saúde**: HRV, Stress, Sleep, VO2 Max e Composição Corporal
- **🧠 Status de Treino**: Acompanhe seu status diário (Overreaching, High, Balanced, Low, Detraining)
- **⚙️ Configuração Segura**: Armazenamento local de credenciais (nunca enviado para servidores)
- **🗄️ Cache Inteligente**: Sistema de cache com TTL para melhor performance e suporte offline
- **📱 Design Responsivo**: Funciona em desktop, tablet e dispositivos móveis
- **🎨 UX Moderna**: Interface rica e bonita com componentes visuais avançados

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior
- Conta Garmin Connect

### Instalação

1. **Clone ou baixe o projeto**
   ```bash
   git clone <repository-url>
   cd fitness-metrics
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

   Para desenvolvimento (testes/lint/format):
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Execute o aplicativo**
   ```bash
   python app.py
   ```

4. **Acesse no navegador**
   - Local: http://127.0.0.1:8050
   - Rede: http://[seu-ip]:8050

## 📊 Métricas de Fitness

### CTL (Chronic Training Load)
- **O que é**: Capacidade de forma física crônica
- **Cálculo**: Média ponderada dos últimos 42 dias
- **Interpretação**: Valores mais altos indicam melhor condição física

### ATL (Acute Training Load)
- **O que é**: Carga de treino aguda (fadiga)
- **Cálculo**: Média ponderada dos últimos 7 dias
- **Interpretação**: Valores altos indicam fadiga acumulada

### TSB (Training Stress Balance)
- **O que é**: Equilíbrio entre forma física e fadiga
- **Cálculo**: CTL - ATL
- **Interpretação**:
  - **Positivo**: Pronto para treinos intensos
  - **Negativo**: Período de recuperação
  - **Zero**: Equilíbrio ideal

## ❤️ Recursos Avançados de Saúde & Wellness

### Saúde & Wellness Tab

Monitore suas métricas de saúde em tempo real:

- **HRV (Heart Rate Variability)**: Variabilidade da frequência cardíaca - indica recuperação e estado nervoso autônomo
- **Stress Score**: Nível de stress medido pelo seu dispositivo Garmin
- **Sleep Data**: Análise de qualidade do sono (duração, sleep profundo, REM)
- **VO2 Max**: Capacidade aeróbica máxima estimada
- **Body Composition**: Composição corporal (peso, IMC, massa muscular, percentual de gordura)
- **Training Status**: Status diário de treino com recomendações de intensidade

**Gráficos e visualizações**:
- Linhas temporais com 42 dias de histórico
- Cards com informações resumidas e status visuais
- Indicadores de cores para fácil interpretação

### Exercícios Tab

Acompanhe detalhadamente seu histórico de exercícios de força:

- **Progressão de Carga**: Visualize aumento de peso ao longo do tempo
- **Séries e Repetições**: Histórico completo de séries, reps e pesos utilizados
- **Gráfico de Progressão**: Análise visual de tendências de força
- **Tabela Detalhada**: Últimos 10 treinos com breakdown de exercícios

**Recursos**:
- Filtra automaticamente atividades de força/strength training
- Mostra estatísticas agregadas (total de atividades, exercícios, séries)
- Suporte para múltiplos exercícios por treino

## 🤖 Chat com IA Especialista em Triathlon

O assistente de IA integrado é um **treinador especialista em triathlon**, com formação em fisiologia do exercício e ciência do treinamento esportivo. Ele analisa seus dados usando métodos científicos específicos para atletas de triathlon, considerando as três modalidades (natação, ciclismo e corrida).

### 🏊‍♂️ **Especialização em Triathlon:**

- **Análise integrada** das três modalidades
- **Periodização científica** baseada em macrociclos
- **Adaptações fisiológicas** específicas do treinamento cruzado
- **Equilíbrio de volume** entre natação, ciclismo e corrida
- **Avaliação de risco** de overtraining em atletas de endurance
- **Recomendações baseadas em evidências** científicas

### Configuração da IA

1. **Obtenha uma chave API gratuita**:
   - Acesse [https://console.groq.com/](https://console.groq.com/)
   - Crie uma conta gratuita
   - Gere uma chave API

2. **Configure no aplicativo**:
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env e adicione sua chave
   GROQ_API_KEY=sua_chave_api_aqui
   ```

3. **Reinicie o aplicativo** para carregar a configuração

**✅ Status**: Configuração da API Groq concluída e testada!

### Como Usar o Chat IA

- Acesse a aba **"🤖 AI Chat"** no aplicativo
- Digite suas perguntas sobre:
  - Estado atual de forma física
  - Análise de treinos recentes
  - Recomendações de carga de treino
  - Progresso em direção às metas
  - Interpretação de métricas

### Exemplos de Perguntas

- "Como está meu equilíbrio entre as três modalidades?"
- "Preciso ajustar minha periodização de treinamento?"
- "Como está minha preparação para uma prova de triathlon?"
- "Qual modalidade precisa de mais foco?"
- "Como otimizar meu treinamento de transição?"
- "Análise da distribuição de volume por modalidade"
- "Recomendações para melhorar minha economia de corrida"
- "Como está minha adaptação ao treinamento cruzado?"

**Nota**: A IA usa o modelo Llama-3.1-8B da Groq, que é gratuito e poderoso para análise de dados de fitness.

## 🔧 Configuração

### Autenticação Garmin Connect

O aplicativo oferece duas formas de autenticação com o Garmin Connect:

#### **Opção 1: Login com Email e Senha (Recomendado - Mais Seguro)**

1. Acesse a página "⚙️ Configuração"
2. Insira seu email e senha do Garmin Connect
3. Clique em "💾 Salvar Credenciais"
4. **Ao salvar, os tokens serão automaticamente gerados e armazenados**
5. Na próxima sincronização, o app usará os tokens (não precisa mais da senha)

#### **Opção 2: Login com Tokens Salvos (Mais Rápido)**

Se você já tem um arquivo `garmin_tokens.json`:

1. **Coloque o arquivo na raiz do projeto**:
   ```
   seu_projeto/
   ├── app.py
   ├── garmin_tokens.json/
   │   ├── oauth1_token.json
   │   └── oauth2_token.json
   └── ...
   ```

2. Na sincronização de dados, o app usará os tokens automaticamente
3. **Você não precisa configurar email e senha**

#### **Gerar Novos Tokens via Linha de Comando**

Se os tokens expirarem, você pode regenerá-los clicando em "🔄 Atualizar Tokens" na página de configuração do app.

### Prioridade de Autenticação

1. ✅ Tenta usar tokens salvos em `garmin_tokens.json` (mais rápido)
2. ↪️ Se falhar, tenta usar email/senha armazenados
3. ❌ Se ambos falharem, exibe erro

### Credenciais Garmin Connect

1. Acesse a página "⚙️ Configuração"
2. Insira seu email e senha do Garmin Connect
3. As credenciais são armazenadas **apenas localmente** no seu dispositivo

### Parâmetros de Fitness

Configure os seguintes parâmetros na página de configuração:

- **Idade**: Para cálculos de zonas cardíacas
- **FTP**: Functional Threshold Power (ciclismo)
- **Pace Threshold**: Ritmo limite (corrida)
- **Swim Pace Threshold**: Ritmo limite (natação)
- **HR Rest**: Frequência cardíaca em repouso
- **HR Max**: Frequência cardíaca máxima

## 📱 Como Usar

### Primeiro Uso

1. **Configure credenciais**: Vá para "⚙️ Configuração" e adicione suas credenciais Garmin
2. **Configure parâmetros**: Ajuste seus parâmetros de fitness
3. **Sincronize dados**: Clique em "🔄 Atualizar Dados Agora"
4. **Visualize dashboard**: Veja suas métricas na página "📊 Dashboard"

### Navegação

- **📊 Dashboard**: Visão geral das métricas atuais (CTL, ATL, TSB)
- **📅 Calendário**: Histórico visual de atividades em calendário interativo
- **🎯 Metas**: Configuração e acompanhamento de objetivos semanais/mensais
- **❤️ Saúde & Wellness**: Métricas avançadas de saúde (HRV, Stress, Sleep, VO2 Max, Composição Corporal, Status de Treino)
- **💪 Exercícios**: Histórico detalhado de exercícios com progressão de carga, séries e repetições
- **🤖 AI Chat**: Assistente especializado em triathlon para análise e recomendações
- **📋 Mais Detalhes**: Análise detalhada de atividades, recordes pessoais e conquistas
- **⚙️ Configuração**: Gerenciamento de credenciais, parâmetros e sincronização de dados

## 🌐 Hospedagem e Deploy

### ✅ Provedores Recomendados

Para **sincronização em tempo real** com Garmin, recomendamos estes provedores:

#### 🚂 **Railway** (Recomendado - Fácil e Gratuito)
```bash
# Instale Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Faça login e deploy
railway login
railway init
railway up
```

#### 🟣 **Render** (Gratuito com limites)
- Conecte seu repositório GitHub
- Deploy automático a cada push
- Bom para projetos pessoais

#### 🟠 **Heroku** (Profissional)
```bash
# Deploy profissional
heroku create seu-app-garmin
git push heroku main
```

### 🚫 Limitações do PythonAnywhere

**IMPORTANTE**: O PythonAnywhere tem restrições de rede que **impedem completamente** a sincronização com Garmin Connect. Mesmo com tokens válidos, todas as tentativas de conexão falharão.

**Sintomas**:
- Erro 403 Forbidden no proxy
- `ProxyError: Unable to connect to proxy`
- Impossível buscar dados do Garmin

**Solução**: Migre para Railway, Render ou Heroku para funcionalidade completa.

## �️ Sistema de Cache Inteligente

O aplicativo implementa um **sistema de cache com TTL (Time-To-Live)** para melhor performance e suporte offline:

### Como Funciona

- **Cache Local**: Dados são armazenados em SQLite local (`~/.fitness_metrics/cache.db`)
- **TTL Automático**: Cada tipo de dado tem um tempo de vida configurável
- **Cache-First**: Se os dados estão em cache e válidos, são usados imediatamente
- **Fallback**: Se o cache expirou, novos dados são buscados do Garmin
- **Offline**: Você pode consultar dados offline (desde que estejam em cache)

### Tempos de Cache (TTL)

| Tipo de Dado | TTL |
|---|---|
| Atividades | 1 hora |
| Métricas de Saúde (HRV, Stress, Sleep) | 6 horas |
| Status de Treino | 2 horas |
| Exercícios | 4 horas |
| VO2 Max | 24 horas |
| Composição Corporal | 6 horas |
| Informações de Dispositivos | 24 horas |

### Limpeza de Cache

O cache expirado é limpo automaticamente durante a sincronização. Você também pode limpar manualmente através da aba "⚙️ Configuração":

- Invalidar tipos específicos de dados
- Limpar todo o cache
- Visualizar estatísticas de cache (entries, tamanho)

## 🔒 Segurança e Privacidade

- **Armazenamento Local**: Todas as credenciais e dados são armazenados apenas no seu dispositivo
- **Sem Servidores Externos**: Não há transmissão de dados para servidores externos
- **Permissões de Arquivo**: O app tenta restringir permissões dos arquivos localmente (quando suportado pelo SO)
- **Cache Seguro**: Cache de credenciais não é persistido entre reinicializações
- **Controle Total**: Você pode deletar todos os dados a qualquer momento

## 📋 Dependências

```
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.14.0
pandas>=2.0.0
numpy>=2.3.0
garminconnect>=0.2.30
langchain-groq>=0.1.0
python-dotenv>=1.0.0
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
fitness-metrics/
├── app.py                 # Aplicação principal Dash
├── requirements.txt       # Dependências Python
├── cache_manager.py       # Sistema de cache com SQLite + TTL
├── garmin_enhanced.py     # Wrapper Garmin com novos endpoints
├── wellness_page.py       # Aba "Saúde & Wellness" 
├── exercises_page.py      # Aba "Exercícios"
├── details_page.py        # Aba "Mais Detalhes"
├── calculations.py        # Cálculos de TSS/CTL/ATL/TSB
├── storage.py             # Persistência local (JSON + dados saúde)
├── garmin.py              # Integração Garmin Connect
├── ai_chat.py             # Assistente IA em Triathlon
├── utils.py               # Utilitários e funções auxiliares
├── callbacks.py           # Callbacks Dash
├── components.py          # Componentes reutilizáveis
├── styles.py              # Estilos customizados
└── README.md              # Este arquivo
```

### Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## � Troubleshooting

### Aba de Saúde & Wellness não mostra dados

**Sintoma**: Ao clicar na aba "❤️ Saúde & Wellness", vê uma mensagem "Nenhum dado de saúde disponível"

**Solução**:
1. Vá para ⚙️ **Configuração** e confirme que adicionou suas credenciais do Garmin
2. Clique em **🔄 Atualizar Dados** e aguarde a sincronização completar
3. Verifique o console para mensagens de log como `[HEALTH] HRV 2025-01-10: OK`
4. Sincronize novamente e verifique a aba depois de alguns segundos

Se o problema persistir:
- Verifique se o arquivo `~/.fitness_metrics/health_metrics.json` existe
- Se não existir, pode ser um problema de permissões na pasta
- Veja os detalhes em [WELLNESS_DEBUG_GUIDE.md](WELLNESS_DEBUG_GUIDE.md)

### Erro ao sincronizar com Garmin

**Sintoma**: Mensagem de erro durante "🔄 Atualizar Dados"

**Solução**:
1. Verifique suas credenciais do Garmin em ⚙️ **Configuração**
2. Se usado 2FA (autenticação de dois fatores), pode ser necessário gerar uma senha específica de app
3. Consulte os logs no console para mensagens `[FATAL]` ou `[ERROR]`
4. Tente sincronizar novamente

### Dados de treino não aparecem no Dashboard

**Sintoma**: Dashboard vazio ou mostra "Sem dados disponíveis"

**Solução**:
1. Verifique se tem atividades registradas no Garmin dos últimos 42 dias
2. Clique em 🔄 **Atualizar Dados** para sincronizar
3. Aguarde pelo menos 5 segundos e recarregue a página
4. Se ainda não aparecer, verifique o arquivo `~/.fitness_metrics/fitness_metrics.json`

### Problemas de Performance / App Lento

**Sintoma**: Dashboard demora muito para carregar ou desacelera ao navegar

**Solução**:
1. O app usa cache para melhor performance - isso é normal na primeira sincronização
2. Se persistir, pode ter muitas atividades (>500). Considere:
   - Arquivar atividades antigas no Garmin
   - Limpar a cache: delete `~/.fitness_metrics/` e ressincronize
3. Em Android/Termux, aumentar memória alocada pode ajudar

### Erro de Permissão no Linux/Android

**Sintoma**: `PermissionError: [Errno 13] Permission denied`

**Solução**:
```bash
# Linux/Termux
chmod 700 ~/.fitness_metrics
chmod 600 ~/.fitness_metrics/*.json
```

### Cache não está funcionando corretamente

**Sintoma**: Dados antigos aparecem ou cache parece não estar salvando

**Solução**:
1. O cache é armazenado em `~/.fitness_metrics/cache.db` (SQLite)
2. Para resetar: `rm ~/.fitness_metrics/cache.db`
3. Ressincronize e os dados frescos serão coletados

## 📚 Documentação Adicional

- **[WELLNESS_DEBUG_GUIDE.md](WELLNESS_DEBUG_GUIDE.md)** - Guia detalhado de diagnóstico da aba Saúde
- **[API_FIXES_REPORT.md](API_FIXES_REPORT.md)** - Relatório técnico das correções da API Garmin

## �📞 Suporte

Para suporte ou dúvidas:

1. Verifique a documentação neste README
2. Abra uma issue no repositório
3. Consulte os arquivos de documentação adicionais na raiz do projeto

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🙏 Agradecimentos

- Garmin Connect API pela integração de dados
- Comunidade de treinamento por compartilhar conhecimento sobre métricas de fitness
- Dash pela plataforma de desenvolvimento

---

**💡 Dica**: Para melhores resultados, mantenha suas configurações de fitness atualizadas e sincronize regularmente com o Garmin Connect.