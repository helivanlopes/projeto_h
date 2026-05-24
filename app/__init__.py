import os
import logging
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from app.models import db, Usuario

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'main.login'

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

    # Configure Logging
    os.makedirs(app.instance_path, exist_ok=True)
    log_file = os.path.join(app.instance_path, 'app.log')
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                        handlers=[
                            logging.FileHandler(log_file),
                            logging.StreamHandler()
                        ])
    
    app.logger.info('LordCRM startup')

    with app.app_context():
        # Ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)
        
        db.create_all()

        # Seed proprietario user
        if Usuario.query.filter_by(papel='proprietario').first() is None:
            proprietario = Usuario(
                nome=os.getenv('OWNER_DEFAULT_NAME', 'Proprietário'),
                email=os.getenv('OWNER_DEFAULT_EMAIL', 'owner@lordcrm.com'),
                papel='proprietario'
            )
            proprietario.set_password(os.getenv('OWNER_DEFAULT_PASSWORD', 'owner123'))
            db.session.add(proprietario)
            db.session.commit()
            app.logger.info("Default owner user created.")

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
