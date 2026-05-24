import pytest
from app.models import Usuario

def test_register(client, auth, app):
    response = auth.register()
    assert response.status_code == 200
    with app.app_context():
        assert Usuario.query.filter_by(email='teste@teste.com').first() is not None

def test_login(client, auth, db_session):
    # Test admin default user (seeded in create_app)
    response = auth.login()
    assert response.status_code == 200
    # In my routes.py, the index redirects to painel_atendente if papel == 'atendente'
    # But for admin, it might stay at index or go to base.html
    # Let's check the content for "Sair" which indicates successful login
    assert b'Sair' in response.data

def test_login_invalid(client, auth):
    response = auth.login(email='wrong@email.com', password='wrongpassword')
    assert b'Email ou senha inv\xc3\xa1lidos.' in response.data

def test_logout(client, auth):
    auth.login()
    response = auth.logout()
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')
