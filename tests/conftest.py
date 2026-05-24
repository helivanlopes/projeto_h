import pytest
from app import create_app
from app.models import db, Usuario

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='admin@lordcrm.com', password='admin123'):
        return self._client.post(
            '/login',
            data={'email': email, 'senha': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout')

    def register(self, nome='Teste', email='teste@teste.com', senha='password123'):
        return self._client.post(
            '/register',
            data={'nome': nome, 'email': email, 'senha': senha},
            follow_redirects=True
        )

@pytest.fixture
def auth(client):
    return AuthActions(client)
