import os  # Adicione esta linha
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configurações (agora com 'os' importado corretamente)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///taskmanager.db').replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicialize o db com a app
    db.init_app(app)
    
    # Importe os modelos DEPOIS de criar a app
    from models import Project, Task
    
    # Importe e registre blueprints
    from routes.project_routes import project_bp
    from routes.task_routes import task_bp
    
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    
    # Crie as tabelas
    with app.app_context():
        db.create_all()
    
    return app

# Crie a instância da app
app = create_app()
