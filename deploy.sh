#!/bin/bash

# Script de Deploy Automatizado - Pastelaria Web
# Uso: ./deploy.sh [ambiente]
# Ambientes: local, production

set -e  # Para o script se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${2}${1}${NC}"
}

# Função para verificar se o Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_message "❌ Docker não está instalado!" $RED
        exit 1
    fi
    
    # Verifica se docker compose está disponível (versão 2.x)
    if ! docker compose version &> /dev/null; then
        print_message "❌ Docker Compose não está disponível!" $RED
        exit 1
    fi
    
    print_message "✅ Docker e Docker Compose encontrados" $GREEN
}

# Função para criar arquivo .env se não existir
create_env_file() {
    if [ ! -f .env ]; then
        print_message "📝 Criando arquivo .env..." $YELLOW
        
        # Gera uma chave secreta aleatória
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
        
        cat > .env << EOF
FLASK_ENV=${1:-production}
SECRET_KEY=${SECRET_KEY}
EOF
        
        print_message "✅ Arquivo .env criado com chave secreta gerada" $GREEN
    else
        print_message "✅ Arquivo .env já existe" $GREEN
    fi
}

# Função para fazer backup do banco de dados
backup_database() {
    if [ -f "instance/pastelaria.db" ]; then
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).db"
        print_message "💾 Fazendo backup do banco de dados..." $YELLOW
        cp instance/pastelaria.db "backups/${BACKUP_FILE}" 2>/dev/null || mkdir -p backups && cp instance/pastelaria.db "backups/${BACKUP_FILE}"
        print_message "✅ Backup salvo em: backups/${BACKUP_FILE}" $GREEN
    fi
}

# Função para parar containers existentes
stop_containers() {
    print_message "🛑 Parando containers existentes..." $YELLOW
    docker compose down 2>/dev/null || true
    print_message "✅ Containers parados" $GREEN
}

# Função para construir e iniciar containers
start_containers() {
    print_message "🔨 Construindo e iniciando containers..." $YELLOW
    docker compose up --build -d
    print_message "✅ Containers iniciados" $GREEN
}

# Função para aguardar a aplicação ficar pronta
wait_for_app() {
    print_message "⏳ Aguardando aplicação ficar pronta..." $YELLOW
    sleep 10
    
    # Tenta fazer uma requisição para verificar se está funcionando
    for i in {1..30}; do
        if curl -s http://localhost:5000/ > /dev/null 2>&1; then
            print_message "✅ Aplicação está respondendo" $GREEN
            return 0
        fi
        sleep 2
    done
    
    print_message "⚠️  Aplicação pode não estar pronta ainda" $YELLOW
}

# Função para inicializar banco de dados
init_database() {
    print_message "🗄️  Inicializando banco de dados..." $YELLOW
    docker compose exec -T pastelaria-web python init_simple.py
    print_message "✅ Banco de dados inicializado" $GREEN
}

# Função para mostrar status
show_status() {
    print_message "\n📊 Status dos containers:" $BLUE
    docker compose ps
    
    print_message "\n🌐 URLs de acesso:" $BLUE
    print_message "   Aplicação: http://localhost:5000" $GREEN
    print_message "   Com Nginx: http://localhost:80" $GREEN
    
    print_message "\n🔑 Credenciais padrão:" $BLUE
    print_message "   Admin - Telefone: 11999999999 | Senha: admin123" $YELLOW
    print_message "   Cliente - Telefone: 11988888888 | Senha: 123456" $YELLOW
    
    print_message "\n⚠️  IMPORTANTE: Altere as senhas padrão em produção!" $RED
}

# Função para mostrar logs
show_logs() {
    print_message "\n📋 Logs da aplicação (Ctrl+C para sair):" $BLUE
    docker compose logs -f pastelaria-web
}

# Função principal
main() {
    local ambiente=${1:-production}
    
    print_message "🚀 Iniciando deploy da Pastelaria Web" $BLUE
    print_message "   Ambiente: $ambiente" $YELLOW
    
    # Verificações
    check_docker
    create_env_file $ambiente
    
    # Backup se existir banco
    backup_database
    
    # Deploy
    stop_containers
    start_containers
    wait_for_app
    init_database
    
    # Status final
    show_status
    
    # Pergunta se quer ver logs
    read -p "Deseja ver os logs da aplicação? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
    
    print_message "\n🎉 Deploy concluído com sucesso!" $GREEN
}

# Verificar argumentos
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Uso: $0 [ambiente]"
    echo ""
    echo "Ambientes disponíveis:"
    echo "  local      - Deploy local para desenvolvimento"
    echo "  production - Deploy para produção"
    echo ""
    echo "Exemplos:"
    echo "  $0 local"
    echo "  $0 production"
    echo "  $0  # Usa 'production' por padrão"
    exit 0
fi

# Executar função principal
main "$@"
