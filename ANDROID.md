# Instalação no Android

Guia passo a passo para instalar e executar o Fitness Metrics no Android usando Termux.

## Opção 1: Termux (Recomendado)

### Passo 1: Instale Termux

1. Abra o **F-Droid** (alternativa open source do Play Store)
   - Se não tiver, baixe em: https://f-droid.org/
2. Procure por "Termux"
3. Instale

**Ou** (se preferir Play Store):
- Acesse: https://play.google.com/store/apps/details?id=com.termux

### Passo 2: Configure o Termux

Abra o Termux e execute:

```bash
# Atualizar pacotes
pkg update
pkg upgrade

# Instalar Python (necessário)
pkg install python

# Instalar Git (opcional, mas recomendado para clonar o projeto)
pkg install git

# Instalar JDK (necessário para algumas bibliotecas)
pkg install openjdk-17
```

### Passo 3: Baixe o Projeto

**Opção A: Via Git (Recomendado)**
```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/fitness_metrics.git
cd fitness_metrics
```

**Opção B: Manualmente**
1. Copie os arquivos do projeto para seu Android
2. Use um gerenciador de arquivos para navegar até: `/sdcard/Download/fitness_metrics/`
3. No Termux: `cd /sdcard/Download/fitness_metrics/`

### Passo 4: Instale as Dependências

```bash
# Navegar até o diretório do projeto
cd ~/fitness_metrics

# Ou se estiver em /sdcard
cd /sdcard/Download/fitness_metrics

# Instalar dependências Python
pip install -r requirements.txt
```

Este processo pode levar alguns minutos.

### Passo 5: Execute a Aplicação

```bash
streamlit run app.py
```

Você verá uma saída como:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Passo 6: Acesse no Navegador

1. Abra seu navegador (Chrome, Firefox, etc.)
2. Digite: `http://localhost:8501`
3. A aplicação deve carregar

## Opção 2: Via Navegador (Sem Termux)

Se preferir executar em outro dispositivo na mesma rede:

1. Execute o app em um PC/servidor com Python instalado
2. Inicie com: `streamlit run app.py --server.port 8501 --server.address 0.0.0.0`
3. No Android, acesse: `http://seu-servidor:8501`

## Solução de Problemas

### Erro: "command not found: python"
```bash
# Instale Python
pkg install python
```

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Permission denied" ao acessar arquivos
```bash
# Conceda permissão de armazenamento
termux-setup-storage
```

### Conexão recusada em http://localhost:8501
1. Verifique se o Streamlit está rodando (você deve ver a mensagem acima)
2. Aguarde 30 segundos para o servidor iniciar completamente
3. Verifique se está usando a URL correta: `http://localhost:8501`
4. Tente recarregar a página (F5)

### O app é muito lento
- Isso é normal no Android. Use `-optimized` mode:
```bash
streamlit run app.py --logger.level=error --client.showErrorDetails=false
```

## Dicas e Truques

### Manter o app rodando em background (Termux)

1. Inicie normalmente: `streamlit run app.py`
2. Pressione `Ctrl+Z` para pausar
3. Digite: `bg` para enviar para background
4. Digite: `jobs` para listar processos

### Atalho para iniciar rapidamente

Crie um arquivo `startup.sh`:

```bash
#!/bin/bash
cd ~/fitness_metrics
streamlit run app.py --logger.level=error
```

Depois execute: `bash startup.sh`

### Acessar de outro dispositivo na rede

Ao iniciar, procure pela linha `Network URL: http://192.168.x.x:8501`

Use esse IP para acessar de outro aparelho na mesma WiFi!

### Permissão de armazenamento

Para acessar arquivos do armazenamento do Android:

```bash
# Ativar acesso ao armazenamento
termux-setup-storage

# Seus arquivos estarão em:
cd ~/storage/shared
```

## Estrutura de Arquivos no Android

```
/data/data/com.termux/
├── files/
│   └── home/
│       └── .fitness_metrics/          # Pasta de dados do app
│           ├── garmin_credentials.json
│           ├── user_config.json
│           ├── fitness_metrics.json
│           └── workouts_42_dias.json
└── ...

/sdcard/Download/
└── fitness_metrics/                   # Seu projeto (se copiou aqui)
    ├── app.py
    ├── requirements.txt
    └── ...
```

## Limitações no Android

1. **Bateria**: Use em modo de bateria conservador se possível
2. **Memória**: Feche outros apps se houver lag
3. **Rede**: Mantenha WiFi ativa ou use dados móveis
4. **Storage**: Verifique espaço disponível

## Próximos Passos

1. Vá para a página de **Configuração**
2. Insira suas credenciais do Garmin Connect
3. Configure seus parâmetros de fitness
4. Clique em **Atualizar Dados**
5. Visualize seu progresso no **Dashboard**

## Suporte

- Para problemas com Termux: https://termux.dev/
- Para problemas com Streamlit: https://discuss.streamlit.io/
- Para problemas com Garmin: https://support.garmin.com/

---

**Aproveite seu rastreamento de fitness no Android! 💪📱**
