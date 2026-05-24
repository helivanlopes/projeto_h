from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Usuario, Ticket
from functools import wraps

bp = Blueprint('main', __name__)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.papel != role:
                flash(f"Acesso negado. Esta página é restrita a {role}s.", "danger")
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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash("Email ou senha inválidos.", "danger")
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
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
        
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.register'))
        
        novo_usuario = Usuario(nome=nome, email=email, papel='cliente')
        novo_usuario.set_password(senha)
        db.session.add(novo_usuario)
        db.session.commit()
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
        flash("Ticket aberto com sucesso!", "success")
        return redirect(url_for('main.index'))
    return render_template('novo_ticket.html')

@bp.route('/ticket/<int:id>/assumir', methods=['POST'])
@login_required
@role_required('atendente')
def assumir_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    if ticket.status != 'aberto':
        flash("Este ticket já está sendo atendido ou foi finalizado.", "warning")
    else:
        ticket.atendente_id = current_user.id
        ticket.status = 'em_andamento'
        db.session.commit()
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
@role_required('admin')
def gerenciar_equipe():
    usuarios = Usuario.query.all()
    return render_template('gerenciar_equipe.html', usuarios=usuarios)

@bp.route('/admin/usuario/novo', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def criar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        papel = request.form.get('papel')
        
        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.criar_usuario'))
        
        novo_usuario = Usuario(nome=nome, email=email, papel=papel)
        novo_usuario.set_password(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash(f"Usuário {nome} ({papel}) criado com sucesso!", "success")
        return redirect(url_for('main.gerenciar_equipe'))
    return render_template('admin/novo_usuario.html')

@bp.route('/gestor/relatorios')
@login_required
@role_required('gestor')
def relatorios():
    return render_template('relatorios.html')
