Especificação Técnica (Spec) - LordCRM
Este documento detalha as especificações técnicas para a implementação do sistema LordCRM, seguindo os requisitos de arquitetura MVT, conteinerização e controle de acesso (RBAC).

4.1 Infraestrutura e Configuração Inicial
/Dockerfile
ação: criar

descrição: Define a imagem Docker baseada em Python 3.11-slim para isolamento do ambiente.

pseudocódigo:

Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
/docker-compose.yml
ação: criar

descrição: Orquestra o serviço web e o volume para persistência do banco de dados SQLite.

pseudocódigo:

YAML
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    env_file:
      - .env
4.2 Camada de Dados (Models)
/app/models.py
ação: criar

descrição: Definição do esquema relacional utilizando SQLAlchemy.

pseudocódigo:

Python
CLASSE Usuario(UserMixin):
    id = Integer, Primary Key
    nome = String(100)
    email = String(120), Unique, Indexed
    senha_hash = String(128)
    papel = Enum('admin', 'gestor', 'atendente', 'cliente')

CLASSE Ticket:
    id = Integer, Primary Key
    titulo = String(200)
    descricao = Text
    status = Enum('aberto', 'em_andamento', 'concluido', 'cancelado')
    data_criacao = DateTime (default: UTC_NOW)
    cliente_id = ForeignKey(Usuario.id)
    atendente_id = ForeignKey(Usuario.id, nullable=True)
4.3 Inicialização e Segurança
/app/__init__.py
ação: modificar

descrição: Configura a aplicação e garante a existência do administrador padrão (Seed).

pseudocódigo:

Python
FUNCAO create_app():
    app = Flask(__name__)
    db.init_app(app)
    
    COM app.app_context():
        db.create_all()
        SE Usuario.query.filter_by(papel='admin').count() == 0:
            admin = Usuario(
                nome=os.getenv('ADMIN_DEFAULT_NAME'),
                email=os.getenv('ADMIN_DEFAULT_EMAIL'),
                papel='admin'
            )
            admin.set_password(os.getenv('ADMIN_DEFAULT_PASSWORD'))
            db.session.add(admin)
            db.session.commit()
4.4 Rotas e Regras de Negócio (Routes)
/app/routes.py - Registro de Cliente
ação: criar

descrição: Endpoint para permitir que novos clientes criem contas.

pseudocódigo:

Python
@rota('/register', methods=['POST'])
FUNCAO registrar_cliente():
    DADOS = requisicao.form
    SE Usuario.query(email=DADOS.email):
        RETORNAR erro("Email já existe")
    NOVO_CLIENTE = Usuario(nome=DADOS.nome, email=DADOS.email, papel='cliente')
    NOVO_CLIENTE.set_password(DADOS.senha)
    db.session.add(NOVO_CLIENTE)
    db.session.commit()
    RETORNAR redirecionar('/login')
/app/routes.py - Fluxo de Chamados
ação: modificar

descrição: Lógica para abertura e atribuição de tickets.

pseudocódigo:

Python
# Abertura (Cliente)
@rota('/ticket/novo', methods=['POST'])
@login_required(papel='cliente')
FUNCAO abrir_ticket():
    NOVO_TICKET = Ticket(
        titulo=req.form.titulo, 
        descricao=req.form.descricao, 
        cliente_id=current_user.id
    )
    db.session.add(NOVO_TICKET)
    db.session.commit()

# Atendimento (Atendente)
@rota('/ticket/<id>/assumir', methods=['POST'])
@login_required(papel='atendente')
FUNCAO assumir_ticket(id):
    TICKET = Ticket.query.get(id)
    TICKET.atendente_id = current_user.id
    TICKET.status = 'em_andamento'
    4.5 Interface e Templates
    /app/templates/base.html
    ação: criar

    descrição: Template mestre com Bootstrap, FontAwesome, Chart.js e controle de navegação por perfil.

    pseudocódigo:

    HTML
    <nav>
        {% if current_user.is_authenticated %}
            {% if current_user.papel == 'proprietario' or current_user.papel == 'admin' %}
                <a href="/admin/equipe">Gerenciar Equipe</a>
            {% elif current_user.papel == 'gestor' %}
                <a href="/gestor/relatorios">Relatórios</a>
            {% endif %}
            <a href="/logout">Sair</a>
        {% else %}
            <a href="/login">Entrar</a>
        {% endif %}
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        Helivan Lopes | {{ datetime_now }}
    </footer>

    /app/templates/atendente/painel.html
    ação: consultar

    descrição: Visualização da fila de tickets pendentes com ordenação via JS e ações via ícones.

    /app/templates/admin/equipe.html
    ação: consultar

    descrição: Visualização de usuários com ordenação via JS e ações via ícones.

    4.6 Otimização e Performance
    ... (restante do conteúdo)
Este documento detalha as especificações técnicas para a implementação do sistema LordCRM, seguindo os requisitos de arquitetura MVT, conteinerização e controle de acesso (RBAC).

4.1 Infraestrutura e Configuração Inicial
/Dockerfile
ação: criar

descrição: Define a imagem Docker baseada em Python 3.11-slim para isolamento do ambiente.

pseudocódigo:

Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
/docker-compose.yml
ação: criar

descrição: Orquestra o serviço web e o volume para persistência do banco de dados SQLite.

pseudocódigo:

YAML
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    env_file:
      - .env
4.2 Camada de Dados (Models)
/app/models.py
ação: criar

descrição: Definição do esquema relacional utilizando SQLAlchemy.

pseudocódigo:

Python
CLASSE Usuario(UserMixin):
    id = Integer, Primary Key
    nome = String(100)
    email = String(120), Unique, Indexed
    senha_hash = String(128)
    papel = Enum('admin', 'gestor', 'atendente', 'cliente')

CLASSE Ticket:
    id = Integer, Primary Key
    titulo = String(200)
    descricao = Text
    status = Enum('aberto', 'em_andamento', 'concluido', 'cancelado')
    data_criacao = DateTime (default: UTC_NOW)
    cliente_id = ForeignKey(Usuario.id)
    atendente_id = ForeignKey(Usuario.id, nullable=True)
4.3 Inicialização e Segurança
/app/__init__.py
ação: modificar

descrição: Configura a aplicação e garante a existência do administrador padrão (Seed).

pseudocódigo:

Python
FUNCAO create_app():
    app = Flask(__name__)
    db.init_app(app)
    
    COM app.app_context():
        db.create_all()
        SE Usuario.query.filter_by(papel='admin').count() == 0:
            admin = Usuario(
                nome=os.getenv('ADMIN_DEFAULT_NAME'),
                email=os.getenv('ADMIN_DEFAULT_EMAIL'),
                papel='admin'
            )
            admin.set_password(os.getenv('ADMIN_DEFAULT_PASSWORD'))
            db.session.add(admin)
            db.session.commit()
4.4 Rotas e Regras de Negócio (Routes)
/app/routes.py - Registro de Cliente
ação: criar

descrição: Endpoint para permitir que novos clientes criem contas.

pseudocódigo:

Python
@rota('/register', methods=['POST'])
FUNCAO registrar_cliente():
    DADOS = requisicao.form
    SE Usuario.query(email=DADOS.email):
        RETORNAR erro("Email já existe")
    NOVO_CLIENTE = Usuario(nome=DADOS.nome, email=DADOS.email, papel='cliente')
    NOVO_CLIENTE.set_password(DADOS.senha)
    db.session.add(NOVO_CLIENTE)
    db.session.commit()
    RETORNAR redirecionar('/login')
/app/routes.py - Fluxo de Chamados
ação: modificar

descrição: Lógica para abertura e atribuição de tickets.

pseudocódigo:

Python
# Abertura (Cliente)
@rota('/ticket/novo', methods=['POST'])
@login_required(papel='cliente')
FUNCAO abrir_ticket():
    NOVO_TICKET = Ticket(
        titulo=req.form.titulo, 
        descricao=req.form.descricao, 
        cliente_id=current_user.id
    )
    db.session.add(NOVO_TICKET)
    db.session.commit()

# Atendimento (Atendente)
@rota('/ticket/<id>/assumir', methods=['POST'])
@login_required(papel='atendente')
FUNCAO assumir_ticket(id):
    TICKET = Ticket.query.get(id)
    TICKET.atendente_id = current_user.id
    TICKET.status = 'em_andamento'
    db.session.commit()
4.5 Interface e Templates
/app/templates/base.html
ação: criar

descrição: Template mestre com Bootstrap e controle de navegação por perfil.

pseudocódigo:

HTML
<nav>
    {% if current_user.is_authenticated %}
        {% if current_user.papel == 'admin' %}
            <a href="/admin">Gerenciar Equipe</a>
        {% elif current_user.papel == 'gestor' %}
            <a href="/relatorios">Relatórios</a>
        {% endif %}
        <a href="/logout">Sair</a>
    {% else %}
        <a href="/login">Entrar</a>
    {% endif %}
</nav>
<main>
    {% block content %}{% endblock %}
/app/routes.py - CRUD de Proprietários
ação: criar

descrição: Endpoints para que um Proprietário possa gerenciar outros usuários com papel 'proprietario' e 'admin'.

/app/__init__.py - Caching e Jobs
ação: modificar

descrição: Integração de `Flask-Caching` para otimização de consultas e `APScheduler` para processamento de tarefas em segundo plano (jobs).

4.6 Otimização e Performance
/app/services.py
ação: criar

descrição: Camada de serviço para abstrair a lógica de negócio dos endpoints (`routes.py`).

/app/jobs.py
ação: criar

descrição: Definição de tarefas agendadas (jobs) para manutenção automática do sistema.

