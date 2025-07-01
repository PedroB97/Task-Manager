import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Define extensions globally
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

migrate = Migrate()

def create_app():
    # Use instance_relative_config=True
    # Rely on Flask finding 'templates' folder relative to __init__.py
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY="dev_secret_key_change_in_production", # CHANGE THIS!
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024, # 10MB max upload
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads")
    )

    # Configure Database URI (inside instance folder)
    db_path = os.path.join(app.instance_path, "taskmanager.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    except OSError:
        pass # Already exists

    # Initialize extensions WITH the app context
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # User loader callback (import User model here)
    from .models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # Import and register blueprints within app context
    with app.app_context():
        from .routes.project_routes import project_bp
        from .routes.task_routes import task_bp
        from .routes.attachment_routes import attachment_bp
        from .routes.auth_routes import auth_bp
        from .routes.user_routes import user_bp

        app.register_blueprint(project_bp)
        app.register_blueprint(task_bp)
        app.register_blueprint(attachment_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)

        # Create database tables if they don't exist
        # Moved this here to ensure app context is fully set up
        db.create_all()

    # Define root route
    @app.route("/")
    def index():
        # Redirect to project list (login required will handle auth)
        return redirect(url_for("project_bp.list_projects"))

    return app