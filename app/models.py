from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(128), nullable=False)
    papel = db.Column(db.Enum('proprietario', 'admin', 'gestor', 'atendente', 'cliente', name='papeis_usuario'), nullable=False)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('aberto', 'em_andamento', 'concluido', 'cancelado', name='status_ticket'), default='aberto', nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    cliente = db.relationship('Usuario', foreign_keys=[cliente_id], backref='tickets_criados')
    atendente = db.relationship('Usuario', foreign_keys=[atendente_id], backref='tickets_atendidos')
