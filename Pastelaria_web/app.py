# app.py

import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask import session, flash

# app.py (adicionar este bloco)

from functools import wraps

# app.py (adicionar decorator de admin)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'cliente_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Inicialização do App e do Banco de Dados
app = Flask(__name__)
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "pastelaria.db")}' # Define o arquivo do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---
# Documentação: Cada classe representa uma tabela no banco de dados.

# Tabela de Clientes
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False, unique=True)
    endereco = db.Column(db.String(200), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False) # NOVO CAMPO
    is_admin = db.Column(db.Boolean, default=False) # NOVO CAMPO
    consentimento_lgpd = db.Column(db.Boolean, nullable=False, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    # Método para definir a senha de forma segura
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    # Método para verificar a senha
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

# Tabela de Produtos (Pastéis e Bebidas)
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # Ex: "Pastel Salgado", "Pastel Doce", "Bebida"

# Tabela de Pedidos
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    valor_total = db.Column(db.Float, nullable=False)
    # O status indica se o pedido está "Pendente", "Em Preparo", "Pronto para Entrega", etc.
    status = db.Column(db.String(50), default="Pendente")

# Tabela associativa para os itens de um pedido (relação Muitos-para-Muitos)
itens_pedido = db.Table('itens_pedido',
    db.Column('pedido_id', db.Integer, db.ForeignKey('pedido.id'), primary_key=True),
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), primary_key=True)
)

# Adiciona a relação na tabela Pedido
Pedido.produtos = db.relationship('Produto', secondary=itens_pedido, lazy='subquery',
        backref=db.backref('pedidos', lazy=True))


# --- APLICAÇÃO PRINCIPAL (CONTINUA NO PRÓXIMO PASSO) ---
if __name__ == '__main__':
    # Este bloco será preenchido nos próximos passos
    pass

# app.py (continuação)

# ... (código dos modelos do passo anterior) ...


# --- ROTAS DA APLICAÇÃO ---
# Documentação: Cada função abaixo corresponde a uma página ou ação na aplicação.

# Rota Principal: Página inicial
@app.route('/')
def index():
    """Renderiza a página inicial."""
    return render_template('index.html')

# Rota do Cardápio: Exibe todos os produtos
@app.route('/cardapio')
def cardapio():
    """Busca todos os produtos no banco de dados e exibe na página do cardápio."""
    pasteis_salgados = Produto.query.filter_by(categoria='Pastel Salgado').all()
    pasteis_doces = Produto.query.filter_by(categoria='Pastel Doce').all()
    bebidas = Produto.query.filter_by(categoria='Bebida').all()
    return render_template('cardapio.html', 
                           pasteis_salgados=pasteis_salgados,
                           pasteis_doces=pasteis_doces,
                           bebidas=bebidas)

# Adicione uma chave secreta para o Flask gerenciar sessões
app.secret_key = '8102@sarutneV'

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        senha = request.form['senha']
        consentimento = 'consentimento' in request.form

        if not consentimento:
            flash("É necessário aceitar os termos da LGPD.", "error")
            return redirect(url_for('cadastro'))

        # Verifica se o cliente já existe
        if Cliente.query.filter_by(telefone=telefone).first():
            flash("Este telefone já está cadastrado.", "warning")
            return redirect(url_for('cadastro'))

        novo_cliente = Cliente(
            nome=nome,
            telefone=telefone,
            endereco=endereco,
            consentimento_lgpd=True
        )
        novo_cliente.set_senha(senha) # Usa o método para criptografar a senha

        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash("Cadastro realizado com sucesso! Faça o login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Ocorreu um erro ao cadastrar.", "error")
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

# app.py (novas rotas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefone = request.form['telefone']
        senha = request.form['senha']

        cliente = Cliente.query.filter_by(telefone=telefone).first()

        if cliente and cliente.check_senha(senha):
            # Guarda informações do usuário na sessão
            session['cliente_id'] = cliente.id
            session['cliente_nome'] = cliente.nome
            session['is_admin'] = cliente.is_admin
            flash(f'Bem-vindo de volta, {cliente.nome}!', 'success')

            if cliente.is_admin:
                return redirect(url_for('admin_dashboard')) # Redireciona admin para o painel
            else:
                return redirect(url_for('cardapio')) # Redireciona cliente para o cardápio
        else:
            flash('Telefone ou senha inválidos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Limpa a sessão
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    session.pop('is_admin', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

# app.py (adicionar novas rotas de admin)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Página inicial do painel de administração."""
    total_pedidos = Pedido.query.count()
    total_produtos = Produto.query.count()
    return render_template('admin/dashboard.html', total_pedidos=total_pedidos, total_produtos=total_produtos)

@app.route('/admin/pedidos')
@login_required
@admin_required
def admin_pedidos():
    """Lista todos os pedidos recebidos."""
    pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return render_template('admin/pedidos.html', pedidos=pedidos)

@app.route('/admin/produtos')
@login_required
@admin_required
def admin_produtos():
    """Lista todos os produtos para gerenciamento."""
    produtos = Produto.query.all()
    return render_template('admin/produtos.html', produtos=produtos)

@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_produto():
    """Página para adicionar um novo produto."""
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])
        categoria = request.form['categoria']

        novo_prod = Produto(nome=nome, descricao=descricao, preco=preco, categoria=categoria)
        db.session.add(novo_prod)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))

    return render_template('admin/form_produto.html', titulo="Novo Produto")

@app.route('/admin/produto/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_produto(produto_id):
    """Página para editar um produto existente."""
    produto = Produto.query.get_or_404(produto_id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])
        produto.categoria = request.form['categoria']
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))

    return render_template('admin/form_produto.html', titulo="Editar Produto", produto=produto)

@app.route('/admin/produto/deletar/<int:produto_id>', methods=['POST'])
@login_required
@admin_required
def deletar_produto(produto_id):
    """Ação para deletar um produto."""
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('admin_produtos'))

# --- FUNÇÃO PARA INICIALIZAR O BANCO DE DADOS ---
def inicializar_banco():
    """Cria o banco de dados e adiciona alguns produtos de exemplo."""
    with app.app_context():
        db.create_all()
        
        # Adiciona produtos apenas se o banco estiver vazio
        if not Produto.query.first():
            # Pastéis Salgados
            db.session.add(Produto(nome='Pastel de Carne', descricao='Carne moída temperada', preco=8.50, categoria='Pastel Salgado'))
            db.session.add(Produto(nome='Pastel de Queijo', descricao='Queijo mussarela derretido', preco=8.00, categoria='Pastel Salgado'))
            db.session.add(Produto(nome='Pastel de Frango com Catupiry', descricao='Frango desfiado com catupiry cremoso', preco=9.00, categoria='Pastel Salgado'))
            
            # Pastéis Doces
            db.session.add(Produto(nome='Pastel de Chocolate', descricao='Chocolate ao leite derretido', preco=7.50, categoria='Pastel Doce'))
            db.session.add(Produto(nome='Pastel de Banana com Canela', descricao='Banana com açúcar e canela', preco=7.00, categoria='Pastel Doce'))

            # Bebidas
            db.session.add(Produto(nome='Refrigerante Lata', descricao='Coca-Cola, Guaraná, etc.', preco=5.00, categoria='Bebida'))
            db.session.add(Produto(nome='Suco Natural de Laranja', descricao='300ml', preco=6.00, categoria='Bebida'))
            
            db.session.commit()
            print("Banco de dados inicializado e produtos de exemplo adicionados.")

# app.py (adicionar novas rotas do carrinho)

@app.route('/adicionar_carrinho/<int:produto_id>', methods=['POST'])
@login_required
def adicionar_carrinho(produto_id):
    """Adiciona um produto ao carrinho na sessão."""
    # Inicializa o carrinho na sessão se não existir
    if 'carrinho' not in session:
        session['carrinho'] = {}

    carrinho = session['carrinho']
    id_str = str(produto_id) # Dicionários em sessão usam chaves de string

    # Busca o produto no banco para pegar os detalhes
    produto = Produto.query.get_or_404(produto_id)

    # Se o item já está no carrinho, incrementa a quantidade
    if id_str in carrinho:
        carrinho[id_str]['quantidade'] += 1
    else: # Se não, adiciona com quantidade 1
        carrinho[id_str] = {
            'nome': produto.nome,
            'preco': produto.preco,
            'quantidade': 1
        }

    # Marca a sessão como modificada para garantir que seja salva
    session.modified = True
    flash(f'"{produto.nome}" adicionado ao carrinho!', 'success')
    return redirect(url_for('cardapio'))

@app.route('/carrinho')
@login_required
def ver_carrinho():
    """Exibe o conteúdo do carrinho de compras."""
    carrinho = session.get('carrinho', {})
    total_pedido = 0
    # Calcula o valor total do pedido
    for item in carrinho.values():
        total_pedido += item['preco'] * item['quantidade']

    return render_template('carrinho.html', carrinho=carrinho, total_pedido=total_pedido)

@app.route('/remover_item/<int:produto_id>', methods=['POST'])
@login_required
def remover_item(produto_id):
    """Remove um item do carrinho."""
    carrinho = session.get('carrinho', {})
    id_str = str(produto_id)

    if id_str in carrinho:
        del carrinho[id_str]
        session.modified = True
        flash('Item removido do carrinho.', 'info')

    return redirect(url_for('ver_carrinho'))

@app.route('/finalizar_pedido', methods=['POST'])
@login_required
def finalizar_pedido():
    """Processa o carrinho e o transforma em um pedido no banco de dados."""
    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('cardapio'))

    cliente_id = session['cliente_id']
    valor_total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # Cria o novo pedido
    novo_pedido = Pedido(cliente_id=cliente_id, valor_total=valor_total, status="Recebido")

    # Adiciona os produtos do carrinho ao pedido
    for produto_id_str in carrinho:
        produto_id = int(produto_id_str)
        produto = Produto.query.get(produto_id)
        if produto:
            novo_pedido.produtos.append(produto)

    try:
        db.session.add(novo_pedido)
        db.session.commit()

        # Limpa o carrinho da sessão
        session.pop('carrinho', None)

        flash('Pedido finalizado com sucesso! Em breve você receberá seu delicioso pastel.', 'success')
        return redirect(url_for('pedido_confirmado', pedido_id=novo_pedido.id))
    except:
        flash('Ocorreu um erro ao finalizar seu pedido.', 'error')
        return redirect(url_for('ver_carrinho'))

@app.route('/pedido_confirmado/<int:pedido_id>')
@login_required
def pedido_confirmado(pedido_id):
    """Exibe a página de confirmação do pedido."""
    pedido = Pedido.query.get_or_404(pedido_id)
    # Garante que o cliente só veja seus próprios pedidos
    if pedido.cliente_id != session['cliente_id']:
        return "Acesso negado", 403
    return render_template('pedido_confirmado.html', pedido=pedido)


# --- APLICAÇÃO PRINCIPAL ---
if __name__ == '__main__':
    inicializar_banco() # Executa a função para criar o BD e os produtos
    
    
    app.run(debug=True) # Inicia o servidor web em modo de depuração