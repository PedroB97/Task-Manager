import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10MB max upload
    )

    # Configuração do banco de dados para Render (PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///taskmanager.db').replace("postgres://", "postgresql://", 1)
    
    # Configuração do upload folder para Render
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configurações do LoginManager
    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "info"

    # User loader
    from models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # Registrar blueprints
    from routes.project_routes import project_bp
    from routes.task_routes import task_bp
    from routes.attachment_routes import attachment_bp
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp

    app.register_blueprint(project_bp, url_prefix='/projects')
    app.register_blueprint(task_bp, url_prefix='/tasks')
    app.register_blueprint(attachment_bp, url_prefix='/attachments')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')

    # Rota raiz
    @app.route('/')
    def index():
        return redirect(url_for('auth_bp.login'))  # Ou para project_bp.list_projects

    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        # Garantir que a pasta de uploads existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
