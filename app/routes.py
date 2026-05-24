from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Usuario, Ticket
from app import cache
from app.services import get_all_users, create_user, delete_user
from functools import wraps

bp = Blueprint('main', __name__)

def role_required(roles):
    if isinstance(roles, str):
        roles = [roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.papel not in roles:
                flash(f"Acesso negado. Esta página é restrita a {', '.join(roles)}s.", "danger")
                return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/')
@login_required
def index():
    if current_user.papel == 'atendente':
        return redirect(url_for('main.painel_atendente'))
    return render_template('base.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(senha):
            login_user(usuario)
            current_app.logger.info(f"Usuário {usuario.email} ({usuario.papel}) fez login.")
            
            # Redirecionamento baseado no papel
            if usuario.papel in ['proprietario', 'admin']:
                return redirect(url_for('main.gerenciar_equipe'))
            elif usuario.papel == 'gestor':
                return redirect(url_for('main.relatorios'))
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        current_app.logger.warning(f"Tentativa de login falhou para email: {email}")
        flash("Email ou senha inválidos.", "danger")
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"Usuário {current_user.email} fez logout.")
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = create_user(nome, email, senha, 'cliente')
        if not user:
            current_app.logger.warning(f"Tentativa de registro com email já existente: {email}")
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.register'))
        
        current_app.logger.info(f"Novo cliente registrado: {email}")
        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/ticket/novo', methods=['GET', 'POST'])
@login_required
@role_required('cliente')
def abrir_ticket():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        novo_ticket = Ticket(titulo=titulo, descricao=descricao, cliente_id=current_user.id)
        db.session.add(novo_ticket)
        db.session.commit()
        current_app.logger.info(f"Usuário {current_user.email} abriu novo ticket: {titulo}")
        flash("Ticket aberto com sucesso!", "success")
        return redirect(url_for('main.index'))
    return render_template('novo_ticket.html')

@bp.route('/ticket/<int:id>/assumir', methods=['POST'])
@login_required
@role_required('atendente')
def assumir_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    if ticket.status != 'aberto':
        current_app.logger.warning(f"Atendente {current_user.email} tentou assumir ticket {id} que não está aberto.")
        flash("Este ticket já está sendo atendido ou foi finalizado.", "warning")
    else:
        ticket.atendente_id = current_user.id
        ticket.status = 'em_andamento'
        db.session.commit()
        current_app.logger.info(f"Atendente {current_user.email} assumiu o ticket {id}.")
        flash("Você assumiu o ticket com sucesso!", "success")
    return redirect(url_for('main.painel_atendente'))

@bp.route('/atendente/painel')
@login_required
@role_required('atendente')
def painel_atendente():
    tickets = Ticket.query.filter(Ticket.status.in_(['aberto', 'em_andamento'])).all()
    return render_template('atendente/painel.html', tickets=tickets)

@bp.route('/admin/equipe')
@login_required
@role_required(['admin', 'proprietario'])
@cache.cached(timeout=60, key_prefix='all_users')
def gerenciar_equipe():
    usuarios = get_all_users()
    return render_template('gerenciar_equipe.html', usuarios=usuarios)

@bp.route('/admin/usuario/novo', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'proprietario'])
def criar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        papel = request.form.get('papel')
        
        # Restrição: Admin não pode criar Admin ou Proprietário
        if current_user.papel == 'admin' and papel in ['admin', 'proprietario']:
            current_app.logger.warning(f"Admin {current_user.email} tentou criar usuário com papel restrito: {papel}")
            flash("Você não tem permissão para criar administradores ou proprietários.", "danger")
            return redirect(url_for('main.criar_usuario'))

        user = create_user(nome, email, senha, papel)
        if not user:
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.criar_usuario'))
        
        cache.delete('all_users')
        current_app.logger.info(f"Usuário {current_user.email} criou novo usuário: {email} ({papel})")
        flash(f"Usuário {nome} ({papel}) criado com sucesso!", "success")
        return redirect(url_for('main.gerenciar_equipe'))
    return render_template('admin/novo_usuario.html')

@bp.route('/proprietario/usuario/<int:id>/excluir', methods=['POST'])
@login_required
@role_required('proprietario')
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash("Você não pode excluir a si mesmo.", "danger")
        return redirect(url_for('main.gerenciar_equipe'))
    
    email = usuario.email
    if delete_user(id):
        cache.delete('all_users')
        current_app.logger.info(f"Proprietário {current_user.email} excluiu o usuário {email}")
        flash(f"Usuário {email} excluído com sucesso.", "success")
    return redirect(url_for('main.gerenciar_equipe'))

@bp.route('/gestor/relatorios')
@login_required
@role_required('gestor')
def relatorios():
    return render_template('relatorios.html')
