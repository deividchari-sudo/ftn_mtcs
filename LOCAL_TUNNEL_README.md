# Acesso Remoto com LocalTunnel

## 🚀 Como Usar

### 1. **Iniciar o Dashboard**
```bash
python app.py --host 0.0.0.0 --port 8050
```

### 2. **Criar Túnel Remoto**
Em outro terminal, execute:
```bash
./start_tunnel.bat
```

### 3. **Acessar Remotamente**
Use a URL gerada pelo LocalTunnel (ex: `https://wild-moles-camp.loca.lt`)

## 📋 Sobre LocalTunnel

- **Gratuito**: Sem cadastro necessário
- **Seguro**: HTTPS automático
- **Simples**: Uma linha de comando
- **Limitado**: URL muda a cada execução

## 🛠️ Solução de Problemas

- **Erro de conexão**: Certifique-se que o dashboard está rodando
- **URL não carrega**: Verifique se a porta 8050 está liberada no firewall
- **Timeout**: Reinicie o túnel

Para suporte: https://localtunnel.github.io/www/