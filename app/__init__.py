import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.models import db, Usuario

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url or db_url.startswith('sqlite:///instance/'):
        db_name = db_url.split('/')[-1] if db_url else 'lordcrm.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, db_name)}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)
        
        db.create_all()

        # Seed admin user
        if Usuario.query.filter_by(papel='admin').first() is None:
            admin = Usuario(
                nome=os.getenv('ADMIN_DEFAULT_NAME', 'Admin'),
                email=os.getenv('ADMIN_DEFAULT_EMAIL', 'admin@lordcrm.com'),
                papel='admin'
            )
            admin.set_password(os.getenv('ADMIN_DEFAULT_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created.")

    # Register routes
    from app import routes
    app.register_blueprint(routes.bp)

    return app
