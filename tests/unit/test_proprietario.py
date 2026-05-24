import pytest
from app.models import Usuario

def test_proprietario_creates_admin(client, auth, db_session):
    # Setup: Login as proprietor
    auth.login(email='owner@lordcrm.com', password='owner123')
    
    # Action: Proprietario creates an Admin
    response = client.post('/admin/usuario/novo', data={
        'nome': 'Admin Novo',
        'email': 'novo_admin@lordcrm.com',
        'senha': 'password',
        'papel': 'admin'
    }, follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    admin = Usuario.query.filter_by(email='novo_admin@lordcrm.com').first()
    assert admin is not None
    assert admin.papel == 'admin'

def test_admin_cannot_create_admin(client, auth, db_session):
    # Setup: Login as Admin
    # Create an admin user first
    admin = Usuario(nome='Admin', email='admin@test.com', papel='admin')
    admin.set_password('admin123')
    db_session.add(admin)
    db_session.commit()
    auth.login(email='admin@test.com', password='admin123')
    
    # Action: Admin tries to create another Admin
    response = client.post('/admin/usuario/novo', data={
        'nome': 'Admin 2',
        'email': 'admin2@test.com',
        'senha': 'password',
        'papel': 'admin'
    }, follow_redirects=True)
    
    # Assert
    assert b'Voc\xc3\xaa n\xc3\xa3o tem permiss\xc3\xa3o' in response.data
    assert Usuario.query.filter_by(email='admin2@test.com').first() is None
