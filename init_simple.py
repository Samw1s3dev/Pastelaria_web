#!/usr/bin/env python3
"""
Script simples para inicializar o banco de dados
"""

import os
import sys

# Define a variável de ambiente antes de importar o app
os.environ['DATABASE_URL'] = 'sqlite:////tmp/pastelaria.db'

from app import app, db, Cliente, Produto, Pedido
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa o banco de dados e cria dados de exemplo"""
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        print("✅ Tabelas do banco de dados criadas com sucesso!")
        
        # Verifica se já existem dados
        if Produto.query.first():
            print("⚠️  Banco de dados já possui dados. Pulando inicialização...")
            return
        
        # Cria produtos de exemplo
        produtos_exemplo = [
            # Pastéis Salgados
            Produto(nome='Pastel de Carne', descricao='Carne moída temperada', preco=8.50, categoria='Pastel Salgado'),
            Produto(nome='Pastel de Queijo', descricao='Queijo mussarela derretido', preco=8.00, categoria='Pastel Salgado'),
            Produto(nome='Pastel de Frango com Catupiry', descricao='Frango desfiado com catupiry cremoso', preco=9.00, categoria='Pastel Salgado'),
            Produto(nome='Pastel de Pizza', descricao='Molho de tomate, queijo e orégano', preco=8.50, categoria='Pastel Salgado'),
            Produto(nome='Pastel de Palmito', descricao='Palmito com queijo', preco=9.50, categoria='Pastel Salgado'),
            
            # Pastéis Doces
            Produto(nome='Pastel de Chocolate', descricao='Chocolate ao leite derretido', preco=7.50, categoria='Pastel Doce'),
            Produto(nome='Pastel de Banana com Canela', descricao='Banana com açúcar e canela', preco=7.00, categoria='Pastel Doce'),
            Produto(nome='Pastel de Doce de Leite', descricao='Doce de leite cremoso', preco=7.50, categoria='Pastel Doce'),
            
            # Bebidas
            Produto(nome='Refrigerante Lata', descricao='Coca-Cola, Guaraná, etc.', preco=5.00, categoria='Bebida'),
            Produto(nome='Suco Natural de Laranja', descricao='300ml', preco=6.00, categoria='Bebida'),
            Produto(nome='Café', descricao='Café expresso', preco=3.50, categoria='Bebida'),
            Produto(nome='Água', descricao='Água mineral 500ml', preco=2.50, categoria='Bebida'),
        ]
        
        for produto in produtos_exemplo:
            db.session.add(produto)
        
        # Cria um usuário administrador padrão
        admin = Cliente(
            nome='Administrador',
            telefone='11999999999',
            endereco='Endereço administrativo',
            is_admin=True,
            consentimento_lgpd=True
        )
        admin.set_senha('admin123')  # Senha padrão - deve ser alterada em produção
        db.session.add(admin)
        
        # Cria um cliente de exemplo
        cliente_exemplo = Cliente(
            nome='João Silva',
            telefone='11988888888',
            endereco='Rua das Flores, 123',
            is_admin=False,
            consentimento_lgpd=True
        )
        cliente_exemplo.set_senha('123456')
        db.session.add(cliente_exemplo)
        
        # Salva todas as alterações
        db.session.commit()
        
        print("✅ Produtos de exemplo adicionados!")
        print("✅ Usuário administrador criado:")
        print("   📱 Telefone: 11999999999")
        print("   🔑 Senha: admin123")
        print("✅ Cliente de exemplo criado:")
        print("   📱 Telefone: 11988888888")
        print("   🔑 Senha: 123456")
        print("\n🎉 Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Erro ao inicializar o banco de dados: {e}")
        sys.exit(1)
