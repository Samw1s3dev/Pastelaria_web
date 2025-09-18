# 🚀 Guia de Deploy - Pastelaria Web

Este guia contém instruções para fazer o deploy da aplicação Pastelaria Web em diferentes ambientes.

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Git (para clonar o repositório)
- Acesso a um servidor (VPS, cloud, etc.)

## 🐳 Deploy com Docker

### 1. Preparação do Ambiente

```bash
# Clone o repositório
git clone <seu-repositorio>
cd pastelaria_web

# Crie um arquivo .env para variáveis de ambiente
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DATABASE_URL=sqlite:///instance/pastelaria.db
EOF
```

### 2. Deploy Local com Docker Compose

```bash
# Construir e iniciar os containers
docker compose up --build -d

# Verificar se os serviços estão rodando
docker compose ps

# Ver logs da aplicação
docker compose logs -f pastelaria-web
```

### 3. Inicializar o Banco de Dados

```bash
# Executar o script de inicialização
docker compose exec pastelaria-web python init_simple.py
```

### 4. Acessar a Aplicação

- **Aplicação**: http://localhost:5000
- **Com Nginx**: http://localhost:80

### 5. Credenciais Padrão

- **Administrador**:
  - Telefone: `11999999999`
  - Senha: `admin123`

- **Cliente de Exemplo**:
  - Telefone: `11988888888`
  - Senha: `123456`

⚠️ **IMPORTANTE**: Altere essas senhas em produção!

## ☁️ Deploy em Servidor de Produção

### 1. Preparação do Servidor

```bash
# Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose já vem incluído no Docker v2.x
# Verificar se está disponível:
docker compose version

# Reiniciar a sessão
exit
```

### 2. Configuração do Projeto

```bash
# Clonar o repositório
git clone <seu-repositorio>
cd pastelaria_web

# Criar arquivo .env para produção
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/pastelaria.db
EOF
```

### 3. Deploy

```bash
# Fazer deploy
docker compose up --build -d

# Inicializar banco de dados
docker compose exec pastelaria-web python init_simple.py

# Verificar status
docker compose ps
```

### 4. Configurar Firewall

```bash
# Permitir tráfego HTTP e HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22  # SSH
sudo ufw enable
```

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Parar todos os serviços
docker compose down

# Parar e remover volumes
docker compose down -v

# Ver logs em tempo real
docker compose logs -f

# Acessar shell do container
docker compose exec pastelaria-web bash

# Reiniciar um serviço específico
docker compose restart pastelaria-web
```

### Backup do Banco de Dados

```bash
# Fazer backup
docker compose exec pastelaria-web cp instance/pastelaria.db /tmp/backup_$(date +%Y%m%d_%H%M%S).db

# Restaurar backup
docker compose exec pastelaria-web cp /caminho/para/backup.db instance/pastelaria.db
```

### Atualização da Aplicação

```bash
# Parar a aplicação
docker compose down

# Atualizar código
git pull origin main

# Reconstruir e iniciar
docker compose up --build -d

# Inicializar banco se necessário
docker compose exec pastelaria-web python init_simple.py
```

## 🔒 Configurações de Segurança

### 1. Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```env
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-muito-segura
DATABASE_URL=sqlite:///instance/pastelaria.db
```

### 2. Configuração do Nginx (Opcional)

Para usar HTTPS, configure o Nginx com certificados SSL:

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com
```

## 📊 Monitoramento

### Health Check

A aplicação inclui um health check que verifica se está funcionando:

```bash
# Verificar status
curl http://localhost:5000/

# Health check do Docker
docker-compose ps
```

### Logs

```bash
# Ver logs da aplicação
docker compose logs pastelaria-web

# Ver logs do Nginx
docker compose logs nginx

# Seguir logs em tempo real
docker compose logs -f
```

## 🆘 Solução de Problemas

### Problema: Container não inicia

```bash
# Verificar logs
docker compose logs pastelaria-web

# Verificar se a porta está em uso
sudo netstat -tulpn | grep :5000
```

### Problema: Banco de dados não inicializa

```bash
# Verificar permissões
docker compose exec pastelaria-web ls -la instance/

# Reexecutar inicialização
docker compose exec pastelaria-web python init_simple.py
```

### Problema: Aplicação não responde

```bash
# Verificar se o container está rodando
docker compose ps

# Reiniciar o serviço
docker compose restart pastelaria-web
```

## 📝 Notas Importantes

1. **Backup**: Faça backup regular do banco de dados
2. **Senhas**: Altere as senhas padrão em produção
3. **SSL**: Configure HTTPS para produção
4. **Monitoramento**: Configure alertas para falhas
5. **Atualizações**: Mantenha o sistema atualizado

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `docker compose logs`
2. Consulte este guia
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ para a Pastelaria Web**
