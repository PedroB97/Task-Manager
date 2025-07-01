from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos aqui para evitar importação circular
from src.models.models import Project, Task, Attachment
