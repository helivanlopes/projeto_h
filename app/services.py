from app.models import db, Usuario, Ticket

def get_all_users():
    return Usuario.query.all()

def create_user(nome, email, senha, papel):
    if Usuario.query.filter_by(email=email).first():
        return None
    novo_usuario = Usuario(nome=nome, email=email, papel=papel)
    novo_usuario.set_password(senha)
    db.session.add(novo_usuario)
    db.session.commit()
    return novo_usuario

def delete_user(user_id):
    usuario = Usuario.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return True
    return False
