from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos aqui para evitar importação circular
from models.models import Project, Task, Attachment

