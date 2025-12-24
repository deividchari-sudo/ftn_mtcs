# 💪 Fitness Metrics Dashboard

Um dashboard interativo para monitoramento de métricas de fitness com integração ao Garmin Connect. Acompanhe seu progresso através das métricas CTL (Chronic Training Load), ATL (Acute Training Load) e TSB (Training Stress Balance).

## 📋 Visão Geral

Este aplicativo Streamlit permite que atletas monitorem seu estado de forma física através de métricas científicas baseadas em dados de atividades físicas. A integração com Garmin Connect permite sincronização automática de dados de treino.

### ✨ Funcionalidades Principais

- **📊 Dashboard Interativo**: Visualize seu estado atual de forma física com métricas CTL, ATL e TSB
- **🔄 Sincronização Garmin**: Importe automaticamente atividades dos últimos 42 dias
- **📅 Calendário de Treinos**: Veja seu histórico de atividades em formato de calendário
- **🎯 Metas Personalizáveis**: Configure e acompanhe metas semanais e mensais
- **⚙️ Configuração Segura**: Armazenamento local de credenciais (nunca enviado para servidores)
- **📱 Design Responsivo**: Funciona em desktop, tablet e dispositivos móveis

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

3. **Execute o aplicativo**
   ```bash
   streamlit run app.py
   ```

4. **Acesse no navegador**
   - Local: http://localhost:8501
   - Rede: http://[seu-ip]:8501

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

## 🔧 Configuração

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

- **📊 Dashboard**: Visão geral das métricas atuais
- **📅 Calendário**: Histórico visual de atividades
- **🎯 Metas**: Configuração e acompanhamento de objetivos
- **⚙️ Configuração**: Gerenciamento de credenciais e parâmetros

## 🔒 Segurança e Privacidade

- **Armazenamento Local**: Todas as credenciais e dados são armazenados apenas no seu dispositivo
- **Sem Servidores Externos**: Não há transmissão de dados para servidores externos
- **Criptografia**: Credenciais são criptografadas localmente
- **Controle Total**: Você pode deletar todos os dados a qualquer momento

## 📋 Dependências

```
streamlit>=1.28.0
garminconnect>=0.2.30
pandas>=2.0.0
plotly>=5.14.0
```

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
fitness-metrics/
├── app.py                 # Aplicação principal Streamlit
├── requirements.txt       # Dependências Python
├── user_config.json       # Configurações do usuário
├── utils.py              # Utilitários e funções auxiliares
├── fitness_metrics_flutter/  # Versão mobile (Flutter)
└── README.md             # Este arquivo
```

### Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte ou dúvidas:

1. Verifique a documentação neste README
2. Abra uma issue no repositório
3. Consulte os arquivos de documentação adicionais na raiz do projeto

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🙏 Agradecimentos

- Garmin Connect API pela integração de dados
- Comunidade de treinamento por compartilhar conhecimento sobre métricas de fitness
- Streamlit pela plataforma de desenvolvimento

---

**💡 Dica**: Para melhores resultados, mantenha suas configurações de fitness atualizadas e sincronize regularmente com o Garmin Connect.</content>
<parameter name="filePath">c:\Users\deivi\Developer\README.md