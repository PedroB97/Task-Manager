import os
from flask import Flask
from src.models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave_secreta_do_aplicativo'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload
    
    # Inicializar extensões
    db.init_app(app)
    
    # Garantir que o diretório de uploads exista
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Importar e registrar blueprints
    from src.routes.project_routes import project_bp
    from src.routes.task_routes import task_bp
    from src.routes.attachment_routes import attachment_bp
    
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(attachment_bp)
    
    # Definir rota principal
    from flask import redirect, url_for
    
    @app.route('/')
    def index():
        return redirect(url_for('project_bp.list_projects'))
    
    # Inicializar banco de dados
    with app.app_context():
        db.create_all()
    
    return app
