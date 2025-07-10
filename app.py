from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crie a instância do SQLAlchemy fora da factory
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configurações (use sua configuração atual)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///taskmanager.db').replace("postgres://", "postgresql://", 1)
    
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
